"""RemEYEnder: a tiny, silent reminder to look away from the screen every so often."""

import ctypes
import ctypes.util
import sys
import tkinter as tk
from tkinter import ttk

BREAK_INTERVAL_S: int = 30 * 60
REMINDER_DURATION_S: int = 10
TICK_MS: int = 1000
# Postpone a due break while any app is capturing the microphone (i.e. you're in a call).
POSTPONE_DURING_CALLS: bool = True


class _AudioObjectPropertyAddress(ctypes.Structure):
    _fields_ = [
        ("mSelector", ctypes.c_uint32),
        ("mScope", ctypes.c_uint32),
        ("mElement", ctypes.c_uint32),
    ]


def _fourcc(code: str) -> int:
    return int.from_bytes(code.encode("ascii"), "big")


_K_AUDIO_OBJECT_SYSTEM_OBJECT: int = 1
_K_SCOPE_GLOBAL: int = _fourcc("glob")
_K_PROCESS_OBJECT_LIST: int = _fourcc("prs#")  # kAudioHardwarePropertyProcessObjectList
_K_PROCESS_IS_RUNNING_INPUT: int = _fourcc("piri")  # kAudioProcessPropertyIsRunningInput


def _load_coreaudio() -> ctypes.CDLL | None:
    if sys.platform != "darwin":
        return None
    path = ctypes.util.find_library("CoreAudio")
    return ctypes.CDLL(path) if path else None


_coreaudio: ctypes.CDLL | None = _load_coreaudio()


def microphone_in_use() -> bool:
    """True if any process is capturing audio input (macOS 14+; False elsewhere or on error)."""
    if _coreaudio is None:
        return False
    address = _AudioObjectPropertyAddress(_K_PROCESS_OBJECT_LIST, _K_SCOPE_GLOBAL, 0)
    size = ctypes.c_uint32(0)
    if _coreaudio.AudioObjectGetPropertyDataSize(
        _K_AUDIO_OBJECT_SYSTEM_OBJECT, ctypes.byref(address), 0, None, ctypes.byref(size)
    ):
        return False
    process_ids = (ctypes.c_uint32 * (size.value // 4))()
    if _coreaudio.AudioObjectGetPropertyData(
        _K_AUDIO_OBJECT_SYSTEM_OBJECT, ctypes.byref(address), 0, None, ctypes.byref(size), process_ids
    ):
        return False

    address = _AudioObjectPropertyAddress(_K_PROCESS_IS_RUNNING_INPUT, _K_SCOPE_GLOBAL, 0)
    for process_id in process_ids:
        running = ctypes.c_uint32(0)
        value_size = ctypes.c_uint32(ctypes.sizeof(running))
        status = _coreaudio.AudioObjectGetPropertyData(
            process_id, ctypes.byref(address), 0, None, ctypes.byref(value_size), ctypes.byref(running)
        )
        if status == 0 and running.value:
            return True
    return False


class _CGPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


class _CGSize(ctypes.Structure):
    _fields_ = [("width", ctypes.c_double), ("height", ctypes.c_double)]


class _CGRect(ctypes.Structure):
    _fields_ = [("origin", _CGPoint), ("size", _CGSize)]


_MAX_DISPLAYS: int = 16


def _load_coregraphics() -> ctypes.CDLL | None:
    if sys.platform != "darwin":
        return None
    path = ctypes.util.find_library("CoreGraphics")
    if not path:
        return None
    lib = ctypes.CDLL(path)
    lib.CGDisplayBounds.restype = _CGRect
    lib.CGDisplayBounds.argtypes = [ctypes.c_uint32]
    return lib


_coregraphics: ctypes.CDLL | None = _load_coregraphics()


def display_bounds() -> list[tuple[int, int, int, int]]:
    """(x, y, width, height) of each active display in global top-left-origin points.

    macOS only; empty list elsewhere or on error (callers fall back to Tk's main screen).
    """
    if _coregraphics is None:
        return []
    display_ids = (ctypes.c_uint32 * _MAX_DISPLAYS)()
    count = ctypes.c_uint32(0)
    if _coregraphics.CGGetActiveDisplayList(_MAX_DISPLAYS, display_ids, ctypes.byref(count)):
        return []
    bounds: list[tuple[int, int, int, int]] = []
    for display_id in display_ids[: count.value]:
        rect = _coregraphics.CGDisplayBounds(display_id)
        bounds.append(
            (int(rect.origin.x), int(rect.origin.y), int(rect.size.width), int(rect.size.height))
        )
    return bounds


def format_mmss(seconds: int) -> str:
    minutes, secs = divmod(max(seconds, 0), 60)
    return f"{minutes:02d}:{secs:02d}"


class RemEYEnderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.remaining_s: int = BREAK_INTERVAL_S
        self.running: bool = False
        # One popup (and countdown label) per display while a reminder is showing.
        self.reminders: list[tk.Toplevel] = []
        self._reminder_left_s: int = 0
        self._reminder_labels: list[ttk.Label] = []
        self._tick_job: str | None = None

        root.title("RemEYEnder")
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", self.exit)

        frame = ttk.Frame(root, padding=16)
        frame.grid()

        ttk.Label(frame, text="Next break in").grid(row=0, column=0, columnspan=4)
        self.countdown_label = ttk.Label(frame, font=("Helvetica", 32))
        self.countdown_label.grid(row=1, column=0, columnspan=4, pady=(0, 4))
        self.status_label = ttk.Label(frame)
        self.status_label.grid(row=2, column=0, columnspan=4, pady=(0, 12))

        self.start_button = ttk.Button(frame, text="Start", command=self.start)
        self.stop_button = ttk.Button(frame, text="Stop", command=self.stop)
        self.reset_button = ttk.Button(frame, text="Reset", command=self.reset)
        self.exit_button = ttk.Button(frame, text="Exit", command=self.exit)
        for col, button in enumerate(
            (self.start_button, self.stop_button, self.reset_button, self.exit_button)
        ):
            button.grid(row=3, column=col, padx=2)

        self._refresh()

    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self._schedule_tick()
        self._refresh()

    def stop(self) -> None:
        self.running = False
        # Keep ticking while a reminder is showing so it still closes on its own.
        if not self.reminders:
            self._cancel_tick()
        self._refresh()

    def reset(self) -> None:
        self._close_reminder()
        self.remaining_s = BREAK_INTERVAL_S
        self._refresh()

    def exit(self) -> None:
        self._cancel_tick()
        self.root.destroy()

    def _schedule_tick(self) -> None:
        if self._tick_job is None:
            self._tick_job = self.root.after(TICK_MS, self._tick)

    def _cancel_tick(self) -> None:
        if self._tick_job is not None:
            self.root.after_cancel(self._tick_job)
            self._tick_job = None

    def _tick(self) -> None:
        self._tick_job = None
        if self.reminders:
            self._reminder_left_s -= 1
            if self._reminder_left_s <= 0:
                self._close_reminder()
            else:
                for label in self._reminder_labels:
                    label.configure(text=f"{self._reminder_left_s} s")
        elif self.running:
            self.remaining_s = max(self.remaining_s - 1, 0)
            # Once due, stay at 00:00 and re-check every tick until the call ends.
            if self.remaining_s == 0 and not self._postponed():
                self._show_reminder()

        if self.running or self.reminders:
            self._schedule_tick()
        self._refresh()

    def _postponed(self) -> bool:
        return POSTPONE_DURING_CALLS and microphone_in_use()

    def _show_reminder(self) -> None:
        self._reminder_left_s = REMINDER_DURATION_S
        screens = display_bounds() or [
            (0, 0, self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        ]
        for screen in screens:
            self._show_popup_on(screen)

    def _show_popup_on(self, screen: tuple[int, int, int, int]) -> None:
        screen_x, screen_y, screen_w, screen_h = screen
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.bind("<Button-1>", lambda _event: self._close_reminder())

        body = ttk.Frame(popup, padding=24)
        body.pack()
        ttk.Label(body, text="Look away from the screen 👀", font=("Helvetica", 20)).pack()
        label = ttk.Label(body, text=f"{REMINDER_DURATION_S} s")
        label.pack(pady=(8, 0))

        popup.update_idletasks()
        width, height = popup.winfo_reqwidth(), popup.winfo_reqheight()
        x = screen_x + (screen_w - width) // 2
        y = screen_y + (screen_h - height) // 3
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.lift()
        self.reminders.append(popup)
        self._reminder_labels.append(label)

    def _close_reminder(self) -> None:
        if not self.reminders:
            return
        for popup in self.reminders:
            popup.destroy()
        self.reminders = []
        self._reminder_labels = []
        self.remaining_s = BREAK_INTERVAL_S
        if not self.running:
            self._cancel_tick()
        self._refresh()

    def _refresh(self) -> None:
        self.countdown_label.configure(text=format_mmss(self.remaining_s))
        if self.reminders:
            status = "Break!"
        elif self.running and self.remaining_s == 0:
            status = "Break postponed: in a call"
        elif self.running:
            status = "Running"
        else:
            status = "Paused"
        self.status_label.configure(text=status)
        self.start_button.state(["disabled"] if self.running else ["!disabled"])
        self.stop_button.state(["!disabled"] if self.running else ["disabled"])


def main() -> None:
    root = tk.Tk()
    RemEYEnderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

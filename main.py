"""RemEYEnder: a tiny, silent reminder to look away from the screen every so often."""

import tkinter as tk
from tkinter import ttk

BREAK_INTERVAL_S: int = 30 * 60
REMINDER_DURATION_S: int = 10
TICK_MS: int = 1000


def format_mmss(seconds: int) -> str:
    minutes, secs = divmod(max(seconds, 0), 60)
    return f"{minutes:02d}:{secs:02d}"


class RemEYEnderApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.remaining_s: int = BREAK_INTERVAL_S
        self.running: bool = False
        self.reminder: tk.Toplevel | None = None
        self._reminder_left_s: int = 0
        self._reminder_label: ttk.Label | None = None
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
        if self.reminder is None:
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
        if self.reminder is not None:
            self._reminder_left_s -= 1
            if self._reminder_left_s <= 0:
                self._close_reminder()
            elif self._reminder_label is not None:
                self._reminder_label.configure(text=f"{self._reminder_left_s} s")
        elif self.running:
            self.remaining_s -= 1
            if self.remaining_s <= 0:
                self._show_reminder()

        if self.running or self.reminder is not None:
            self._schedule_tick()
        self._refresh()

    def _show_reminder(self) -> None:
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.bind("<Button-1>", lambda _event: self._close_reminder())

        body = ttk.Frame(popup, padding=24)
        body.pack()
        ttk.Label(body, text="Look away from the screen 👀", font=("Helvetica", 20)).pack()
        self._reminder_left_s = REMINDER_DURATION_S
        self._reminder_label = ttk.Label(body, text=f"{REMINDER_DURATION_S} s")
        self._reminder_label.pack(pady=(8, 0))

        popup.update_idletasks()
        width, height = popup.winfo_reqwidth(), popup.winfo_reqheight()
        x = (popup.winfo_screenwidth() - width) // 2
        y = (popup.winfo_screenheight() - height) // 3
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.lift()
        self.reminder = popup

    def _close_reminder(self) -> None:
        if self.reminder is None:
            return
        self.reminder.destroy()
        self.reminder = None
        self._reminder_label = None
        self.remaining_s = BREAK_INTERVAL_S
        if not self.running:
            self._cancel_tick()
        self._refresh()

    def _refresh(self) -> None:
        self.countdown_label.configure(text=format_mmss(self.remaining_s))
        if self.reminder is not None:
            status = "Break!"
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

# RemEYEnder
A simple app for myself to take regular breaks to release strain on eyes.

As in, take a few moments and look away from screen.

As little intrusive as imaginable while also as simple as possible. 
There are other timer apps "out there" already for more complex purposes.

## Usage
Run app, press start and it reminds every 30 minutes to take 
a break (silent by default; uncheck "Silent alarm" to hear the system alert
sound). The reminder stays for 10 seconds on all screens, then disappears
silently and the timer resets.

If a meeting is ongoing (detected via microphone usage), the reminder waits
at 00:00 and appears as soon as the call ends. While the timer runs, the app
checks the mic every 30 s and shows "in a call" in its status line.


## Installation

Requires [uv](https://docs.astral.sh/uv/). In the repo:

```
uv sync
```

## Run

```
uv run main.py
```

## Build a standalone macOS app

```
uv sync
uv run pyinstaller --windowed --name RemEYEnder --noconfirm \
  --icon icons/RemEYEnder.icns \
  --add-data icons/RemEYEnder.png:icons --add-data icons/RemEYEnder-small.png:icons \
  main.py
```

Result: `dist/RemEYEnder.app` (bundles Python + Tcl/Tk, ~27 MB). Drag it to
`/Applications`. It's unsigned: a locally built copy opens normally, but a copy
downloaded or sent from elsewhere needs right-click → Open on first launch.

## Build a standalone app on other OS

Windows and Linux builds have to be made on that OS. Recommended: a single executable.

```
uv sync
uv run pyinstaller --onefile --windowed --name RemEYEnder --noconfirm \
  --icon icons/RemEYEnder.ico \
  --add-data icons/RemEYEnder.png:icons --add-data icons/RemEYEnder-small.png:icons \
  main.py
```

(In Windows `cmd`, put it on one line without the `\`; in PowerShell use a backtick instead.)

Result: `dist/RemEYEnder.exe` (Windows) or `dist/RemEYEnder` (Linux); place it wherever
you like. `--windowed` stops a console window from opening on Windows (no effect on
Linux). A single-file build starts a little slower, as it unpacks itself on each launch.
Without `--onefile`, the result is a folder, `dist/RemEYEnder/`, that has to be kept
together.

Linux executables carry no icon of their own. For a launcher entry with the icon, fill
in the two paths in `icons/remeyender.desktop` and copy it to
`~/.local/share/applications/`.

## Icons

`icons/iconbasis.png` is the source image. `uv run make_icons.py` derives the rest:
`.icns` (macOS, needs `iconutil` so run it on a Mac), `.ico` (Windows) and the PNGs
(Linux launcher, in-app window icon). Sizes of 32 px and below show only the eyes,
since the clock and tree are unreadable that small.


## Platform support

| | macOS | Windows | Linux |
|---|---|---|---|
| Reminder on all screens | CoreGraphics | `EnumDisplayMonitors` | `xrandr` (X11/XWayland) |
| Postpone during calls | CoreAudio (macOS 14+) | privacy registry (mic usage) | `pactl` (PulseAudio/PipeWire) |

If a check isn't available, the reminder falls back to the main screen / is never postponed.
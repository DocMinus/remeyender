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


## Quick start

Requires [uv](https://docs.astral.sh/uv/). In the repo:

```
uv sync
uv run main.py
```

Setup without uv, standalone builds for macOS/Windows/Linux and regenerating the icons:
see [INSTALL.md](INSTALL.md).


## Platform support

| | macOS | Windows | Linux |
|---|---|---|---|
| Reminder on all screens | CoreGraphics | `EnumDisplayMonitors` | `xrandr` (X11/XWayland) |
| Postpone during calls | CoreAudio (macOS 14+) | privacy registry (mic usage) | `pactl` (PulseAudio/PipeWire) |

If a check isn't available, the reminder falls back to the main screen / is never postponed.

## License

MIT, see [LICENSE](LICENSE).

## Contributions
- DocMinus
- Claude
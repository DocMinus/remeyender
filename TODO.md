# TODO

## Avoid showing the reminder while screen sharing (macOS)

Implemented: breaks are postponed while any app is using the microphone (i.e. in a
call), via CoreAudio's per-process "is running input" property (macOS 14+).
Toggle with `POSTPONE_DURING_CALLS` in `main.py`. Trade-off: this suppresses the reminder
for the whole call, not only while sharing.

Other options, not yet done:

- [ ] **Hide the popup from screen capture.** Set the popup's `NSWindow.sharingType` to
  `NSWindowSharingNone` (via `ctypes`/libobjc or PyObjC). You'd still see the reminder but
  viewers wouldn't. Caveat: since macOS 15, capture through ScreenCaptureKit (likely used
  by current Teams) reportedly ignores this flag. Cheap to try; could be combined with
  the call check so reminders show during calls without sharing.
- [ ] **Detect sharing specifically.** Use `CGWindowListCopyWindowInfo` to look for Teams'
  sharing toolbar / red-border window. Needs the Screen Recording permission to read
  window titles, breaks when Teams renames windows, and only covers Teams (or each app
  you add).
- [ ] **Use native macOS notifications instead of the popup.** macOS can hold back
  notifications while the display is shared (System Settings → Notifications → "Allow
  notifications when mirroring or sharing the display"). Unverified whether Teams
  sharing triggers it; loses the 10 s on-screen countdown.

## App icon

- [ ] **Custom app icon.** Make one 1024×1024 PNG (e.g. an eye) and derive the per-OS
  formats from it:
  - macOS: `.icns` (`iconutil`), build with `--icon RemEYEnder.icns`.
  - Windows: `.ico` (multi-size), build with `--icon RemEYEnder.ico`.
  - Linux: executables carry no embedded icon; point a `.desktop` file at the PNG.
  - PyInstaller can convert the PNG itself if Pillow is installed.
  - In-app (all OS): set the Tk window/taskbar icon via `root.iconphoto(True, ...)`.

## Cross-platform

- [ ] **Test on Windows and Linux.** The Windows/Linux branches in `main.py` are
  type-checked but untested on real machines (developed on macOS).
- [ ] **Linux on Wayland.** Tk runs via XWayland; popup placement on secondary monitors and
  "always on top" may not be honoured by every compositor. `pactl` also counts any
  recording stream (e.g. a volume meter) as "in a call".

## Optional

- [ ] Compiled native version Swift, options 1–3 above get simpler
  (direct AppKit/CoreAudio/CoreGraphics access, no ctypes). Best fit for features that 
  are hard in Python. Those include a menu-bar icon, hiding the popup from
  screen sharing, and a small, signed, native app. 
  It's also less code than C++ for the same Mac app.
- [ ] C++ version for cross platform - doesn't gain much, but could be done. 
  The call check and the monitor list are separate code for each system in any language.
  The window would also need a cross-platform UI library: Qt is large and has licensing
  strings attached, and wxWidgets is the lighter option. 
  One would end up with more code than the Python version, not less.

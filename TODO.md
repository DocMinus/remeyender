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

## Packaged app (macOS)

- [ ] **Hide the Dock icon (`LSUIElement`).** Set `LSUIElement = True` in the bundle's
  Info.plist (PyInstaller: `info_plist={"LSUIElement": True}` in the `.spec`'s
  `BUNDLE(...)`, or edit `Contents/Info.plist` after building). No Dock icon and no
  Cmd-Tab entry; the main window stays. Downside: once the window is hidden behind
  others it's hard to get back. Pairs well with a menu-bar icon (would need e.g.
  `rumps`/PyObjC, since tkinter can't make menu-bar items).
- [ ] **Custom app icon.** Make a 1024×1024 PNG (e.g. an eye), convert to `.icns`
  (`iconutil`, or let PyInstaller convert a PNG if Pillow is installed) and build with
  `--icon RemEYEnder.icns`. Could also set the Tk window icon via `root.iconphoto`.

## Later

- [ ] Compiled native version (Swift or C++). In Swift, options 1–3 above get simpler
  (direct AppKit/CoreAudio/CoreGraphics access, no ctypes).

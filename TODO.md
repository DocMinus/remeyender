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

## Later

- [ ] Compiled native version (Swift or C++). In Swift, options 1–3 above get simpler
  (direct AppKit/CoreAudio/CoreGraphics access, no ctypes).

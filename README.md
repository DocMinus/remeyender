# RemEYEnder
a simple app for myself to take regular breaks to release strain on eyes.

As in, take a few moments and look away from screen.

Starting with python. Maybe do a Mac/Win compiled app at some stage?

Would like it to be as little intrusive but also as simple as possible. 
There are other timer apps out there already.

Here, basically I press start and then it should remind every 30 minutes to take 
a break, the reminder, for now silent, will remain for maybe 10 seconds and
then dissappear silently and reset.

Start window should have a simple start / stop / reset / exit option.

For python perhaps use tkinter?

## Run

```
uv run main.py
```

## Build a standalone macOS app

```
uv sync
uv run pyinstaller --windowed --name RemEYEnder --noconfirm main.py
```

Result: `dist/RemEYEnder.app` (bundles Python + Tcl/Tk, ~27 MB). Drag it to
`/Applications`. It's unsigned: a locally built copy opens normally, but a copy
downloaded or sent from elsewhere needs right-click → Open on first launch.
A Windows `.exe` has to be built on Windows with the same command.
# Installing and building RemEYEnder

RemEYEnder needs Python 3.11+ with tkinter, and nothing else to run. Building a standalone
app also needs PyInstaller; regenerating the icons needs Pillow.

## With uv (recommended)

Requires [uv](https://docs.astral.sh/uv/). In the repo:

```
uv sync
uv run main.py
```

The project is set to use uv's own Python (`python-preference = "only-managed"` in
`pyproject.toml`), which includes tkinter on every OS. `uv sync` also installs PyInstaller and
Pillow.

## Without uv

Any Python 3.11+ works as long as it has tkinter. Check with:

```
python3 -c "import tkinter; print(tkinter.TkVersion)"
```

If that fails:

- **Debian/Ubuntu:** `sudo apt install python3-tk` (and `python3-venv` for the step below).
- **macOS with Homebrew Python:** `brew install python-tk@3.12` (match your Python version).
  The python.org installer already includes it.
- **Windows:** the python.org installer includes it, unless "tcl/tk and IDLE" was unticked
  during installation.

Then, in the repo:

```
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
python main.py
```

Running needs no packages. For building or icons: `pip install pyinstaller pillow`.

A conda environment also works: conda's Python includes tkinter.

The build commands below are written for uv. Without it, drop the `uv run` prefix and run
them inside the activated environment. Only the uv route has been tested.

## Build a standalone macOS app

```
uv run pyinstaller --windowed --name RemEYEnder --noconfirm \
  --icon icons/RemEYEnder.icns \
  --add-data icons/RemEYEnder.png:icons --add-data icons/RemEYEnder-small.png:icons \
  main.py
```

Result: `dist/RemEYEnder.app` (bundles Python + Tcl/Tk, ~27 MB). Drag it to
`/Applications`. It's unsigned: a locally built copy opens normally, but a copy
downloaded or sent from elsewhere needs right-click → Open on first launch.

## Build a standalone app on Windows

Has to be built on Windows. Recommended: a single executable.

```
uv run pyinstaller --onefile --windowed --name RemEYEnder --noconfirm \
  --icon icons/RemEYEnder.ico \
  --add-data icons/RemEYEnder.png:icons --add-data icons/RemEYEnder-small.png:icons \
  main.py
```

(In `cmd`, put it on one line without the `\`; in PowerShell use a backtick instead.)

Result: `dist/RemEYEnder.exe`; place it wherever you like. `--windowed` stops a console
window from opening. A single-file build starts a little slower, as it unpacks itself on
each launch. Without `--onefile`, the result is a folder, `dist/RemEYEnder/`, that has to be
kept together.

## Build a standalone app on Linux

Has to be built on Linux. PyInstaller doesn't find uv's bundled Tcl/Tk libraries (it warns
`Library not found: libtcl9.0.so`), and the binary then fails at launch with an
`ImportError`. Add them explicitly:

```
TCLTK="$(uv run python -c 'import sys; print(sys.base_prefix)')/lib"
uv run pyinstaller --onefile --windowed --name RemEYEnder --noconfirm \
  --add-data icons/RemEYEnder.png:icons --add-data icons/RemEYEnder-small.png:icons \
  --add-binary "$TCLTK/libtcl9.0.so:." --add-binary "$TCLTK/libtcl9tk9.0.so:." \
  main.py
```

Result: `dist/RemEYEnder` (~16 MB), a single file that runs on any desktop (X11 or
XWayland) without Python or Tk installed. With a distro Python and its own Tk package (e.g.
`python3-tk`), the `--add-binary` lines are probably unnecessary (untested).

Linux executables carry no icon of their own. For a launcher entry with the icon, fill
in the two paths in `icons/remeyender.desktop` and copy it to
`~/.local/share/applications/`.

## Icons

`icons/iconbasis.png` is the source image. `uv run make_icons.py` derives the rest:
`.icns` (macOS, needs `iconutil` so run it on a Mac), `.ico` (Windows) and the PNGs
(Linux launcher, in-app window icon). Sizes of 32 px and below show only the eyes,
since the clock and tree are unreadable that small.

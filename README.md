# JavaJiggle

☕ **JavaJiggle** is a lightweight utility that mimics minor mouse movements and keypresses to prevent your computer from going idle or entering sleep mode. It's like a virtual shot of espresso that keeps your system alert while you stay focused on other tasks.

---

## Features

- Supports three activity modes: `keypress`, `mouse`, and `hybrid`
- Settings are fully configurable through a `config.ini` file
- User-friendly graphical interface built with PyQt5
- Command-line version with support for `--status`, `--help`, and `--version` flags
- Safely restores the original state of toggle keys (like Caps Lock)
- Minimal system footprint, runs silently in the background

---

## Requirements

- Python **3.10+** (recommended)
- A virtual environment is strongly recommended to manage dependencies cleanly

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

Then install dependencies:

```bash
pip install -r requirements.txt
```

> Note: `pyautogui` requires appropriate system permissions for input control. Some environments (like Wayland sessions on linux) may restrict this functionality.

---

Lastly, generate the **resources_rc.py** file:
```bash
pyrcc5 resources.qrc -o resources_rc.py
```

## How to Use

### GUI Mode
```bash
python gui.py
```

> Adjust settings such as mode, interval, and key input from the GUI. Configurations are stored in `config.ini`.

### CLI Mode
```bash
python cli.py
```

Additional command-line options:
```bash
python cli.py --help
python cli.py --status
python cli.py --version
```

---

## Configuration

JavaJiggle generates a `config.ini` file automatically on first run. Example:

```ini
[Settings]
Key = shift
Interval = 2
Mode = hybrid
MouseDistance = 1
KeyFrequency = 5
```

- `Mode`: Choose between `keypress`, `mouse`, or `hybrid`
- `Key`: Key to simulate (e.g., `shift`, `capslock`)
- `Interval`: Time in seconds between each activity
- `MouseDistance`: Distance in pixels to move the mouse
- `KeyFrequency`: In hybrid mode, press the key every N mouse movements

---

## Creating a Windows Executable (.exe)

You can package JavaJiggle into a standalone Windows executable using [PyInstaller](https://pyinstaller.org/):

**Install PyInstaller:**
  ```bash
  python build.py
  ```

This will:
- Generate `resources_rc.py` from `resources.qrc`
- Compile `gui.py` into a standalone `.exe` inside the `dist/` folder
- Embed your app icon (`assets/JavaJiggle.ico`)
- Include version info from `version.txt`

> After building, you can delete the `build/`, `dist/JavaJiggle.spec`, and `.pyc` files if needed.

---

## License

MIT License © 2025 Tyler Willis  
> *"Tiny movements. Big uptime."*
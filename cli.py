import time
import configparser
import os
import sys
from datetime import datetime

try:
    import pyautogui
    import ctypes
    from colorama import init, Fore, Style
except ImportError:
    print("Missing modules. Run: pip install pyautogui colorama")
    sys.exit(1)

init(autoreset=True)

TOGGLE_KEYS = {
    "capslock": 0x14,
    "numlock": 0x90,
    "scrolllock": 0x91,
}

def get_toggle_state(key):
    vk = TOGGLE_KEYS.get(key.lower())
    if vk is None:
        return None
    return bool(ctypes.windll.user32.GetKeyState(vk) & 0x0001)

def set_toggle_state(key, desired_state):
    if key.lower() not in TOGGLE_KEYS:
        return
    current = get_toggle_state(key)
    if current != desired_state:
        pyautogui.press(key)

def load_config():
    config = configparser.ConfigParser()

    # Get app path to load config
    if getattr(sys, "frozen", False):
        # Running in a PyInstaller bundle
        app_path = os.path.dirname(sys.executable)
    else:
        app_path = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(app_path, "config.ini")

    if not os.path.exists(config_path):
        config["Settings"] = {
            "Key": "capslock",
            "Interval": "2",
            "Mode": "hybrid",
            "MouseDistance": "1",
            "KeyFrequency": "5"
        }
        with open(config_path, "w") as f:
            config.write(f)
        print(f"{Fore.YELLOW}Created default config file at: {config_path}")
    else:
        config.read(config_path)

    settings = {
        "key": config.get("Settings", "key", fallback="shift"),
        "interval": config.getint("Settings", "interval", fallback=2),
        "mode": config.get("Settings", "mode", fallback="keypress"),
        "mouse_distance": config.getint("Settings", "mousedistance", fallback=1),
        "key_frequency": config.getint("Settings", "keyfrequency", fallback=5)
    }

    return settings, config_path

def no_lock_keypress(button, interval):
    count = 0
    original_state = get_toggle_state(button)
    print(f"{Fore.GREEN}Running in keypress mode: {button} every {interval}s")
    print(f"{Fore.MAGENTA}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        while True:
            pyautogui.press(button)
            count += 1
            print(f"{Fore.CYAN}Keypress #{count}: {button}".ljust(60), end="\r")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Interrupted by user.")
    finally:
        if original_state is not None:
            print(f"{Fore.YELLOW}Restoring {button} to {'ON' if original_state else 'OFF'}")
            set_toggle_state(button, original_state)
        print(f"{Fore.MAGENTA}Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def no_lock_mouse(distance, interval):
    count = 0
    direction = 1
    print(f"{Fore.GREEN}Running in mouse mode: {distance}px wiggle every {interval}s")
    print(f"{Fore.MAGENTA}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        while True:
            pyautogui.moveRel(distance * direction, 0, duration=0.1)
            pyautogui.moveRel(-distance * direction, 0, duration=0.1)
            direction *= -1
            count += 1
            dir_str = "right" if direction == -1 else "left"
            print(f"{Fore.CYAN}Mouse move #{count}: {dir_str}".ljust(60), end="\r")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Interrupted by user.")
    except Exception as ex:
        print(f"{Fore.RED}Mouse error: {ex}")
    finally:
        print(f"{Fore.MAGENTA}Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def no_lock_hybrid(distance, interval, key, key_every_n):
    count = 0
    direction = 1
    original_state = get_toggle_state(key)
    print(f"{Fore.GREEN}Running in hybrid mode\n  Mouse: {distance}px every {interval}s\n  Key: {key} every {key_every_n} moves")
    print(f"{Fore.MAGENTA}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        while True:
            pyautogui.moveRel(distance * direction, 0, duration=0.1)
            pyautogui.moveRel(-distance * direction, 0, duration=0.1)
            direction *= -1
            count += 1
            dir_str = "right" if direction == -1 else "left"
            if count % key_every_n == 0:
                pyautogui.press(key)
                print(f"{Fore.CYAN}Hybrid #{count}: {dir_str} + key ({key})".ljust(60), end="\r")
            else:
                print(f"{Fore.CYAN}Hybrid #{count}: {dir_str}".ljust(60), end="\r")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Interrupted by user.")
    finally:
        if original_state is not None:
            print(f"{Fore.YELLOW}Restoring {key} to {'ON' if original_state else 'OFF'}")
            set_toggle_state(key, original_state)
        print(f"{Fore.MAGENTA}Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--version":
            print("JavaJiggle CLI v1.0")
            sys.exit(0)
        elif arg == "--help":
            print("Usage: python javajiggle.py")
            print("Modes are configured via config.ini:")
            print("  keypress - simulate key presses")
            print("  mouse    - move mouse slightly")
            print("  hybrid   - combine mouse + keypress")
            sys.exit(0)
        elif arg == "--status":
            settings, config_path = load_config()
            print("Current JavaJiggle Status:")
            for k, v in settings.items():
                print(f"  {k}: {v}")
            sys.exit(0)

    print(f"{Fore.CYAN}{Style.BRIGHT}\n☕ JavaJiggle CLI — Tiny movements. Big uptime.")
    print(f"{Fore.MAGENTA}----------------------------")

    settings, config_path = load_config()
    mode = settings["mode"].lower()
    interval = settings["interval"]

    print(f"{Fore.YELLOW}Config loaded: {config_path}")
    print(f"{Fore.YELLOW}Mode: {mode}, Interval: {interval}s")

    if mode == "keypress":
        no_lock_keypress(settings["key"], interval)
    elif mode == "mouse":
        no_lock_mouse(settings["mouse_distance"], interval)
    elif mode == "hybrid":
        no_lock_hybrid(
            settings["mouse_distance"],
            interval,
            settings["key"],
            settings["key_frequency"]
        )
    else:
        print(f"{Fore.RED}Invalid mode: '{mode}'\n{Fore.YELLOW}Valid options: keypress, mouse, hybrid")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()

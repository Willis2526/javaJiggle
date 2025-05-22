import sys
import time
import threading
import pyautogui
import ctypes
import configparser
import os

from PyQt5.QtWidgets import (
    QSizePolicy,
    QMainWindow, QMenuBar, QMenu, QAction,
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QComboBox, QSpinBox, QHBoxLayout, QLineEdit,
    QTextEdit, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QPixmap

import resources_rc  # ensures embedded resources are available

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

class OutputSignal(QObject):
    message = pyqtSignal(str)

class JiggleThread(threading.Thread):
    def __init__(self, mode, key, interval, distance, key_frequency, signal):
        super(JiggleThread, self).__init__()
        self.mode = mode
        self.key = key
        self.interval = interval
        self.distance = distance
        self.key_frequency = key_frequency
        self.signal = signal
        self.running = True
        self.toggle_state = get_toggle_state(key)

    def stop(self):
        self.running = False
        if self.toggle_state is not None:
            set_toggle_state(self.key, self.toggle_state)

    def run(self):
        count = 0
        direction = 1
        while self.running:
            if self.mode == "keypress":
                pyautogui.press(self.key)
                count += 1
                self.signal.message.emit(f"Keypress #{count}: {self.key}")
            elif self.mode == "mouse":
                pyautogui.moveRel(self.distance * direction, 0, duration=0.1)
                pyautogui.moveRel(-self.distance * direction, 0, duration=0.1)
                direction *= -1
                count += 1
                self.signal.message.emit(f"Mouse move #{count}: {direction}")
            elif self.mode == "hybrid":
                pyautogui.moveRel(self.distance * direction, 0, duration=0.1)
                pyautogui.moveRel(-self.distance * direction, 0, duration=0.1)
                direction *= -1
                count += 1
                msg = f"Hybrid #{count}: mouse"
                if count % self.key_frequency == 0:
                    pyautogui.press(self.key)
                    msg += f" + key ({self.key})"
                self.signal.message.emit(msg)
            time.sleep(self.interval)

class JiggleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.setWindowTitle("JavaJiggle")
        self.setWindowIcon(QIcon(":/assets/JavaJiggle_icon.ico"))  # uses embedded icon
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #2e3440;
                color: #d8dee9;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background-color: #5e81ac;
                color: white;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #4c566a;
            }
            QComboBox, QSpinBox, QLineEdit, QTextEdit {
                background-color: #3b4252;
                color: #eceff4;
                border: 1px solid #4c566a;
                border-radius: 3px;
                padding: 2px 5px;
            }
            QLabel {
                margin-top: 6px;
            }
            QPushButton:hover {
                background-color: #81a1c1;
            }
            QMenuBar {
                background-color: #3b4252;
            }

            QMenuBar::item {
                background: transparent;
                padding: 4px 10px;
            }

            QMenuBar::item:selected {
                background: #81a1c1;
            }

            QMenu {
                background-color: #3b4252;
                color: #d8dee9;
            }

            QMenu::item:selected {
                background-color: #81a1c1;
                color: #2e3440;
            }
        """)

        self.thread = None
        self.signal = OutputSignal()
        self.signal.message.connect(self.append_output)

        # Get app path to load config
        if getattr(sys, 'frozen', False):
            # Running in a PyInstaller bundle
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))

        self.config_path = os.path.join(app_path, "config.ini")
        self.settings = self.load_config()

        self.layout = QVBoxLayout()
        self.init_ui()
        central_widget.setLayout(self.layout)

    def load_config(self):
        config = configparser.ConfigParser()
        if not os.path.exists(self.config_path):
            config["Settings"] = {
                "key": "capslock",
                "interval": "2",
                "mode": "hybrid",
                "mousedistance": "1",
                "keyfrequency": "5"
            }
            with open(self.config_path, "w") as configfile:
                config.write(configfile)
        else:
            config.read(self.config_path)
        return config["Settings"]

    def save_config(self):
        config = configparser.ConfigParser()
        config["Settings"] = {
            "key": self.key_input.text(),
            "interval": str(self.interval_spin.value()),
            "mode": self.mode_combo.currentText(),
            "mousedistance": str(self.mouse_spin.value()),
            "keyfrequency": str(self.freq_spin.value())
        }
        with open(self.config_path, "w") as configfile:
            config.write(configfile)

    def init_ui(self):
        self.init_menu()
        self.mode_combo = self.labeled_combo(self.layout, "Mode", ["keypress", "mouse", "hybrid"])
        self.mode_combo.setCurrentText(self.settings.get("mode", "hybrid"))

        self.key_input = self.labeled_input(self.layout, "Key", self.settings.get("key", "shift"))

        self.interval_spin = self.labeled_spinbox(self.layout, "Interval (seconds)", int(self.settings.get("interval", 2)), 1, 9999)
        self.mouse_spin = self.labeled_spinbox(self.layout, "Mouse Distance (px)", int(self.settings.get("mousedistance", 1)), 1, 1000)
        self.freq_spin = self.labeled_spinbox(self.layout, "Key Frequency (for hybrid)", int(self.settings.get("keyfrequency", 5)), 1, 1000)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(120)
        self.console_output.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.console_output.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.console_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        
        self.layout.addWidget(QLabel("Console Output:"))
        self.layout.addWidget(self.console_output)
        self.console_output.setStyleSheet("margin-bottom: 30px;")

        # Start and stop buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start (Ctrl+S)")
        self.start_button.setCursor(Qt.PointingHandCursor)
        self.start_button.setShortcut("Ctrl+S")
        self.start_button.setToolTip("Start (Ctrl+S)")
        self.start_button.clicked.connect(self.start_simulation)

        self.stop_button = QPushButton("Stop (Ctrl+X)")
        self.stop_button.setCursor(Qt.PointingHandCursor)
        self.stop_button.setShortcut("Ctrl+X")
        self.stop_button.setToolTip("Stop (Ctrl+X)")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_simulation)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        self.layout.addLayout(button_layout)
        self.layout.addStretch()

    def labeled_combo(self, layout, label_text, options):
        label = QLabel(label_text)
        combo = QComboBox()
        combo.addItems(options)
        layout.addWidget(label)
        layout.addWidget(combo)
        return combo

    def labeled_input(self, layout, label_text, default_value):
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setText(default_value)
        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field

    def labeled_spinbox(self, layout, label_text, default, minimum, maximum):
        label = QLabel(label_text)
        spinbox = QSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setValue(default)
        layout.addWidget(label)
        layout.addWidget(spinbox)
        return spinbox

    def init_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")
        help_menu = menubar.addMenu("Help")

        # File menu
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help menu
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Add pointer cursor
        self.menuBar().setCursor(Qt.PointingHandCursor)
        for action in self.menuBar().actions():
            action.menu().setCursor(Qt.PointingHandCursor)

    def show_about(self):
        box = QMessageBox(self)
        box.setWindowTitle("About JavaJiggle")
        box.setWindowIcon(QIcon(":/assets/JavaJiggle_icon.ico"))

        # HTML with inline image and content
        box.setText("""
            <div style="font-family: 'Segoe UI', sans-serif; font-size: 10pt; text-align: center;">
                <img src=":/assets/JavaJiggle_Icon.png" width="64" height="64" style="margin-bottom: 10px;" />

                <h2 style="margin: 0;">JavaJiggle</h2>
                <p style="margin: 2px 0;"><b>Version:</b> 1.0</p>

                <p><i>JavaJiggle</i> keeps your system alert with just the right amount of jitter.</p>

                <p>Like a strong cup of joe, it gently nudges your mouse or keyboard to keep your status active,
                screen awake, and vibe productive.</p>

                <p>Whether you're grinding through code, sitting in long meetings, or just need your screen to stay
                alive — <b>JavaJiggle</b> works silently in the background, doing tiny movements with big impact.</p>

                <hr style="margin: 12px 0;">

                <p style="font-size: 11pt;"><b><i>Tiny movements. Big uptime.</i></b></p>

                <hr style="margin: 12px 0;">

                <p style="color: #888;">© 2025 Tyler Willis</p>
            </div>
        """)

        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()

        # Show the box and apply pointer cursor to its buttons
        box.show()
        for btn in box.findChildren(QPushButton):
            btn.setCursor(Qt.PointingHandCursor)

    def append_output(self, message):
        self.console_output.append(message)

    def start_simulation(self):
        self.console_output.clear()
        self.save_config()
        mode = self.mode_combo.currentText()
        key = self.key_input.text().strip().lower()
        interval = self.interval_spin.value()
        distance = self.mouse_spin.value()
        key_freq = self.freq_spin.value()

        self.thread = JiggleThread(mode, key, interval, distance, key_freq, self.signal)
        self.thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_simulation(self):
        if self.thread:
            self.thread.stop()
            self.thread.join()
            self.thread = None
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

import signal

def handle_interrupt(signum, frame):
    QApplication.quit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_interrupt)
    app = QApplication(sys.argv)
    window = JiggleGUI()
    window.show()
    sys.exit(app.exec_())

import subprocess

# Generate the resource file
print("Generating resources_rc.py...")
subprocess.run(["pyrcc5", "resources.qrc", "-o", "resources_rc.py"], check=True)

# Build the executable
print("Building JavaJiggle.exe...")
subprocess.run([
    "pyinstaller",
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--icon=assets/JavaJiggle_icon.ico",
    "--version-file=version.txt",
    "--name=JavaJiggle",
    "gui.py"
], check=True)

print("Building JavaJiggleCli.exe...")
subprocess.run([
    "pyinstaller",
    "--noconfirm",
    "--onefile",
    "--icon=assets/JavaJiggle_icon.ico",
    "--version-file=version.txt",
    "--name=JavaJiggleCli",
    "cli.py"
], check=True)

"""
build_exe.py — Genera un ejecutable standalone con PyInstaller

Uso:
    pip install pyinstaller
    python build_exe.py

Resultado: dist/ArduCheck.exe
"""

import PyInstaller.__main__
import os
import shutil

# Limpiar builds anteriores
if os.path.exists("build"):
    shutil.rmtree("build")
if os.path.exists("dist"):
    shutil.rmtree("dist")

print("=" * 60)
print("ArduCheck - Generando ejecutable...")
print("=" * 60)

PyInstaller.__main__.run([
    "gui/app_v2.py",
    "--name=ArduCheck",
    "--onefile",              # Un solo archivo .exe
    "--windowed",             # Sin consola (GUI)
    "--clean",
    "--add-data=core;core",
    "--add-data=gui/tabs;gui/tabs",
    "--add-data=gui/theme;gui/theme",
    "--add-data=gui/widgets;gui/widgets",
    "--add-data=firmware;firmware",
    "--hidden-import=serial",
    "--hidden-import=serial.tools.list_ports",
    "--hidden-import=serial.tools.list_ports_windows",
    "--hidden-import=usb.core",
    "--hidden-import=usb.util",
    "--hidden-import=usb.legacy",
    "--collect-all=serial",
    "--collect-all=usb",
])

print()
print("=" * 60)
print("Generacion completa!")
print("Ejecutable en: dist/ArduCheck.exe")
print("=" * 60)

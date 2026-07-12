"""
build_exe.py — Genera un ejecutable standalone con PyInstaller
"""

import PyInstaller.__main__
import os
import shutil

# Ir al directorio del proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Limpiar
for f in ["build", "dist", "ArduCheck.spec"]:
    if os.path.exists(f):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)

print("Generando ArduCheck.exe...")

PyInstaller.__main__.run([
    "--name=ArduCheck",
    "--onefile",
    "--windowed",
    "--clean",
    "--paths=.",
    "--hidden-import=serial",
    "--hidden-import=serial.tools.list_ports",
    "--hidden-import=serial.tools.list_ports_windows",
    "--hidden-import=usb.core",
    "--hidden-import=usb.util",
    "gui/app_v2.py",
])

print("Listo! Ejecutable en dist/ArduCheck.exe")

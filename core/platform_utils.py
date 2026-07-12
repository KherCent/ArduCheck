"""
core/platform_utils.py

Utilidades multiplataforma para ArduCheck.
Maneja detección de SO, paths de herramientas externas,
permisos de puerto serie y detección del prefijo de dispositivo.
"""

from __future__ import annotations
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def get_system() -> str:
    """Devuelve 'windows', 'linux' o 'darwin'."""
    return platform.system().lower()


def get_serial_port_prefix() -> str:
    """Prefijo del dispositivo serie según el SO."""
    system = get_system()
    if system == "windows":
        return "COM"
    return "/dev/tty"


def is_windows() -> bool:
    return get_system() == "windows"


def is_unix() -> bool:
    return get_system() in ("linux", "darwin")


def get_tool_name(tool: str) -> str:
    """Nombre del ejecutable según el SO (con .exe en Windows)."""
    if is_windows() and not tool.endswith(".exe"):
        return f"{tool}.exe"
    return tool


def find_tool(name: str, extra_paths: Optional[list] = None) -> Optional[str]:
    """Busca una herramienta en el PATH o en rutas extra comunes.
    
    Args:
        name: nombre base del ejecutable (ej. "arduino-cli", "avrdude").
        extra_paths: rutas adicionales donde buscar.
    
    Returns:
        Ruta absoluta al ejecutable o None si no se encuentra.
    """
    # 1) Con el sufijo correcto según SO
    correct_name = get_tool_name(name)
    found = shutil.which(correct_name)
    if found:
        return found

    # 2) Sin sufijo por si acaso ya lo tenía
    if correct_name != name:
        found = shutil.which(name)
        if found:
            return found

    # 3) Rutas extra comunes en Unix
    if extra_paths is None:
        extra_paths = [
            os.path.expanduser("~/.local/bin"),
            "/usr/local/bin",
            "/opt/homebrew/bin",
            "/opt/bin",
            "/usr/bin",
            "/bin",
        ]
        if get_system() == "windows":
            extra_paths = [
                os.path.expanduser("~\\AppData\\Local\\Arduino15\\packages\\arduino\\tools"),
                "C:\\Program Files\\Arduino\\tools",
                "C:\\Program Files (x86)\\Arduino\\tools",
                "C:\\Program Files\\Arduino CLI",
            ]

    for base in extra_paths:
        if not os.path.isdir(base):
            continue
        # Búsqueda recursiva limitada (2 niveles) para herramientas en subcarpetas
        for root, dirs, files in os.walk(base):
            depth = root[len(base):].count(os.sep)
            if depth > 2:
                dirs.clear()
                continue
            if correct_name in files:
                return os.path.join(root, correct_name)
            if name in files and not correct_name.endswith(".exe"):
                # Evitar falsos positivos si buscamos "avrdude" y encontro "avrdude.conf"
                pass

    return None


def require_dialout_membership() -> Tuple[bool, str]:
    """Verifica si el usuario actual tiene permisos para acceder al puerto serie.
    
    En Linux/macOS, los puertos serie suelen requerir membresía al grupo
    'dialout' (Linux) o 'uucp' (macOS).
    
    Returns:
        (ok, hint): ok=True si tiene permisos, hint=mensaje con instrucciones.
    """
    system = get_system()

    if system == "windows":
        return True, ""

    # Linux: verificar grupo dialout
    if system == "linux":
        try:
            groups = subprocess.check_output(
                ["groups"], text=True, timeout=5
            ).strip()
            if "dialout" in groups or "uucp" in groups:
                return True, ""
            # El usuario no está en dialout
            username = os.environ.get("USER", os.environ.get("USERNAME", "tu_usuario"))
            return False, (
                f"El usuario '{username}' no tiene permisos de acceso al puerto serie.\n"
                f"Para solucionarlo, ejecuta:\n\n"
                f"  sudo usermod -a -G dialout {username}\n\n"
                f"Luego cierra sesión y vuelve a iniciarla, o ejecuta:\n"
                f"  newgrp dialout"
            )
        except Exception:
            return False, (
                "No se pudo verificar los permisos del puerto serie.\n"
                "Asegúrate de estar en el grupo 'dialout' (Linux) o 'uucp' (macOS)."
            )

    # macOS: verificar grupo uucp o dialout
    if system == "darwin":
        try:
            groups = subprocess.check_output(
                ["groups"], text=True, timeout=5
            ).strip()
            if "uucp" in groups or "dialout" in groups:
                return True, ""
            username = os.environ.get("USER", "")
            return False, (
                f"El usuario '{username}' no tiene permisos de acceso al puerto serie.\n"
                f"Para solucionarlo, ejecuta:\n\n"
                f"  sudo usermod -a -G uucp {username}\n\n"
                f"Otra opción (si no funciona):\n"
                f"  sudo dscl -a . -append /Groups/uucp GroupMembership {username}\n\n"
                f"Luego cierra sesión y vuelve a iniciarla."
            )
        except Exception:
            return False, (
                "No se pudo verificar los permisos del puerto serie en macOS.\n"
                "Intenta agregar tu usuario al grupo 'uucp' o 'dialout'."
            )

    return True, ""


def check_port_permissions(port: str) -> Tuple[bool, str]:
    """Verifica si se puede abrir un puerto serie.
    
    Args:
        port: ruta del dispositivo (ej. "COM3" o "/dev/ttyUSB0").
    
    Returns:
        (ok, message): ok=True si se puede abrir, message=razón si no.
    """
    import serial
    system = get_system()

    # Verificar primero pertenencia a grupo en Unix
    if system in ("linux", "darwin"):
        dialout_ok, dialout_hint = require_dialout_membership()
        if not dialout_ok:
            return False, dialout_hint

    # Intentar abrir brevemente el puerto
    try:
        with serial.Serial(port, 9600, timeout=1) as ser:
            pass
        return True, ""
    except serial.SerialException as e:
        err = str(e).lower()
        if "permission" in err or "acceso denegado" in err:
            _, dialout_hint = require_dialout_membership()
            if dialout_hint:
                return False, dialout_hint
            return False, (
                f"No se pudo abrir '{port}'.\n"
                f"Verifica que el puerto no esté siendo usado por otro programa."
            )
        elif "no such file" in err or "does not exist" in err:
            return False, f"El puerto '{port}' no existe o la placa no está conectada."
        else:
            return False, f"No se pudo abrir '{port}': {e}"
    except OSError as e:
        return False, f"Error del sistema al abrir '{port}': {e}"
    except Exception as e:
        return False, f"Error inesperado al abrir '{port}': {e}"


def get_arduino_cli_path() -> Optional[str]:
    """Busca arduino-cli en el PATH."""
    return find_tool("arduino-cli")


def get_avrdude_path() -> Optional[str]:
    """Busca avrdude en el PATH o en carpetas comunes de Arduino."""
    # En Windows, arduino-cli incluye avrdude dentro de su propia carpeta de tools
    # Buscar en las carpetas de usuario de Arduino
    base_paths = []
    system = get_system()
    if system == "windows":
        home = os.path.expanduser("~")
        base_paths = [
            os.path.join(home, "AppData", "Local", "Arduino15", "packages", "arduino", "tools", "avr-gcc"),
            os.path.join(home, "AppData", "Local", "Arduino15", "packages", "arduino", "tools", "avr-binutils", "bin"),
            "C:\\Program Files\\Arduino\\hardware\\tools\\avr\\bin",
            "C:\\Program Files (x86)\\Arduino\\hardware\\tools\\avr\\bin",
        ]
    elif system == "linux":
        base_paths = [
            "/usr/bin",
            "/usr/local/bin",
            os.path.expanduser("~/.local/bin"),
        ]
    elif system == "darwin":
        base_paths = [
            "/usr/local/bin",
            "/opt/homebrew/bin",
            os.path.expanduser("~/Library/Arduino15/packages/arduino/tools/avr-gcc"),
        ]

    return find_tool("avrdude", extra_paths=base_paths)


def get_esptool_path() -> Optional[str]:
    """Busca esptool.py o esptool en el PATH."""
    # esptool.py es más común en Linux/macOS, esptool.exe en Windows
    for name in ["esptool.py", "esptool"]:
        found = find_tool(name)
        if found:
            return found
    return None


def get_picotool_path() -> Optional[str]:
    """Busca picotool en el PATH."""
    return find_tool("picotool")


def get_bossac_path() -> Optional[str]:
    """Busca bossac en el PATH."""
    return find_tool("bossac")


if __name__ == "__main__":
    print(f"SO: {get_system()}")
    print(f"Prefijo serie: {get_serial_port_prefix()}")
    print(f"arduino-cli: {get_arduino_cli_path() or 'NO ENCONTRADO'}")
    print(f"avrdude: {get_avrdude_path() or 'NO ENCONTRADO'}")
    print(f"esptool: {get_esptool_path() or 'NO ENCONTRADO'}")
    dialout_ok, hint = require_dialout_membership()
    if dialout_ok:
        print("Permisos de puerto serie: OK")
    else:
        print(f"Permisos de puerto serie: DENEGADOS\n{hint}")

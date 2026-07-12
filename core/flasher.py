"""
core/flasher.py

Compila y sube el sketch de auto-test al Arduino usando arduino-cli.
Si arduino-cli no está instalado, devuelve False y el diagnóstico
puede seguir funcionando con el sketch que ya esté cargado.

Multiplataforma: busca arduino-cli en el PATH y en rutas comunes
de cada sistema operativo usando platform_utils.
"""

from __future__ import annotations
import subprocess
import os
from pathlib import Path
from typing import Optional, Tuple

from .platform_utils import find_tool, is_windows


SKETCH_PATH = Path(__file__).resolve().parent.parent / "firmware" / "diagnostic_sketch" / "diagnostic_sketch.ino"

# FQBN (Fully Qualified Board Name) por tipo de placa
FQBN_BY_TYPE = {
    "uno":            "arduino:avr:uno",
    "nano":           "arduino:avr:nano",
    "mega":           "arduino:avr:mega",
    "mega2560":       "arduino:avr:mega",
    "mega_old":       "arduino:avr:mega",       # 1280 -> mismo fqbn
    "leonardo":       "arduino:avr:leonardo",
    "micro":          "arduino:avr:micro",
    "uno_or_mega":    "arduino:avr:uno",        # por defecto
    "unknown":        "arduino:avr:uno",
    # Arquitecturas adicionales
    "esp32":          "esp32:esp32:esp32",
    "esp8266":        "esp8266:esp8266:d1_mini",
    "rp2040":         "rp2040:rp2040:connect",
    "samd":           "arduino:samd:arduino_zero_native",
    "nrf52":          "arduino:nrf52:nano_33_ble",
    "stm32":          "arduino:stm32:Nucleo_64",
}


def _get_arduino_cli_path() -> Optional[str]:
    """Busca arduino-cli en el PATH o rutas comunes multiplataforma."""
    return find_tool("arduino-cli")


def _get_arduino_cli_install_hint() -> str:
    """Mensaje de instalación de arduino-cli según el SO."""
    if is_windows():
        return (
            "arduino-cli no encontrado. Instálalo con:\n"
            "  winget install ArduinoSA.CLI\n"
            "Luego ejecuta:\n"
            "  arduino-cli core install arduino:avr"
        )
    elif os.uname().sysname == "Darwin":
        return (
            "arduino-cli no encontrado. Instálalo con:\n"
            "  brew install arduino-cli/arduino-cli/arduino-cli\n"
            "Luego ejecuta:\n"
            "  arduino-cli core install arduino:avr"
        )
    else:  # Linux
        return (
            "arduino-cli no encontrado. Instálalo con:\n"
            "  curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh\n"
            "Luego ejecuta:\n"
            "  arduino-cli core install arduino:avr"
        )


def compile_sketch(fqbn: str = "arduino:avr:uno") -> Tuple[bool, str]:
    """Compila el sketch sin subirlo. Útil para verificar antes de flashear."""
    cli = _get_arduino_cli_path()
    if not cli:
        return False, _get_arduino_cli_install_hint()
    if not SKETCH_PATH.exists():
        return False, f"Sketch no encontrado: {SKETCH_PATH}"
    cmd = [cli, "compile", "--fqbn", fqbn, str(SKETCH_PATH)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if proc.returncode == 0:
            return True, proc.stdout
        return False, proc.stderr or proc.stdout
    except subprocess.TimeoutExpired:
        return False, "Timeout al compilar (120 s)."
    except Exception as e:
        return False, f"Error ejecutando arduino-cli: {e}"


def upload_sketch(port: str, board_type: str = "uno") -> Tuple[bool, str]:
    """Compila y sube el sketch al Arduino en el puerto indicado."""
    cli = _get_arduino_cli_path()
    if not cli:
        return False, _get_arduino_cli_install_hint()
    fqbn = FQBN_BY_TYPE.get(board_type, "arduino:avr:uno")
    cmd = [
        cli, "compile",
        "--upload",
        "--fqbn", fqbn,
        "--port", port,
        str(SKETCH_PATH),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if proc.returncode == 0:
            return True, "Sketch subido correctamente."
        return False, proc.stderr or proc.stdout
    except subprocess.TimeoutExpired:
        return False, "Timeout al subir el sketch (180 s)."
    except Exception as e:
        return False, f"Error ejecutando arduino-cli: {e}"


def is_available() -> bool:
    """Devuelve True si arduino-cli está instalado y funcional."""
    return _get_arduino_cli_path() is not None


# Alias para uso desde fuera del módulo
is_flasher_available = is_available

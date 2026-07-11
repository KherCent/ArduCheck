"""
core/flasher.py

Compila y sube el sketch de auto-test al Arduino usando arduino-cli.
Si arduino-cli no está instalado, devuelve False y el diagnóstico
puede seguir funcionando con el sketch que ya esté cargado.
"""

from __future__ import annotations
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple


SKETCH_PATH = Path(__file__).resolve().parent.parent / "firmware" / "diagnostic_sketch.ino"

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
}


def find_arduino_cli() -> Optional[str]:
    return shutil.which("arduino-cli")


def install_arduino_cli_hint() -> str:
    return (
        "arduino-cli no encontrado. Instálalo con:\n"
        "  winget install ArduinoSA.CLI\n"
        "Luego ejecuta:\n"
        "  arduino-cli core install arduino:avr"
    )


def compile_sketch(fqbn: str = "arduino:avr:uno") -> Tuple[bool, str]:
    """Compila el sketch sin subirlo. Útil para verificar antes de flashear."""
    cli = find_arduino_cli()
    if not cli:
        return False, install_arduino_cli_hint()
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
    cli = find_arduino_cli()
    if not cli:
        return False, install_arduino_cli_hint()
    fqbn = FQBN_BY_TYPE.get(board_type, "arduino:avr:uno")
    cmd = [
        cli, "upload",
        "--fqbn", fqbn,
        "--port", port,
        "--verify",                  # verifica después de subir
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
    return find_arduino_cli() is not None

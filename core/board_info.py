"""
core/board_info.py

Información sobre el chip AVR conectado.
Lee la firma (signature) y, si es posible, los fuses vía avrdude/arduino-cli.
"""

from __future__ import annotations
import subprocess
import shutil
from dataclasses import dataclass, field
from typing import List, Optional


# Firmas AVR conocidas: (vendor, part, rev) -> (nombre, arch, flash_b, ram_b, eeprom_b)
KNOWN_SIGNATURES = {
    # ---- ATmega328P/PB ----
    (0x1E, 0x95, 0x14): ("ATmega328P",      "avr",  32768,  2048, 1024),
    (0x1E, 0x95, 0x0F): ("ATmega328",       "avr",  32768,  2048, 1024),
    (0x1E, 0x95, 0x16): ("ATmega328PB",     "avr",  32768,  2048, 1024),
    (0x1E, 0x95, 0x17): ("ATmega328P-AU",   "avr",  32768,  2048, 1024),
    (0x1E, 0x95, 0x15): ("ATmega328P",      "avr",  32768,  2048, 1024),
    # ---- ATmega2560/1280 ----
    (0x1E, 0x98, 0x01): ("ATmega2560",      "avr", 262144,  8192, 4096),
    (0x1E, 0x98, 0x10): ("ATmega1280",      "avr", 131072,  8192, 4096),
    (0x1E, 0x98, 0x04): ("ATmega2560RFR2",  "avr", 262144,  8192, 4096),
    (0x1E, 0x98, 0x02): ("ATmega2561",      "avr", 262144,  8192, 4096),
    # ---- ATmega168/88 ----
    (0x1E, 0x94, 0x06): ("ATmega168",       "avr",   8192,  1024,  512),
    (0x1E, 0x94, 0x0B): ("ATmega168P",     "avr",   8192,  1024,  512),
    (0x1E, 0x93, 0x0A): ("ATmega88",       "avr",   4096,  1024,  512),
    (0x1E, 0x93, 0x0F): ("ATmega88P",      "avr",   4096,  1024,  512),
    # ---- ATmega32U4 ----
    (0x1E, 0x96, 0x02): ("ATmega32U4",     "avr",  32768,  2560, 1024),
    (0x1E, 0x94, 0x88): ("ATmega16U4",     "avr",  16384,  2048,  512),
    # ---- ATmega32U2 ----
    (0x1E, 0xA7, 0x03): ("ATmega32U2",     "avr",  32768,  2048, 1024),
    (0x1E, 0xA8, 0x01): ("ATmega16U2",     "avr",  16384,  1024,  512),
    # ---- ATmega8A ----
    (0x1E, 0x93, 0x07): ("ATmega8A",       "avr",   8192,  1024,  512),
    (0x1E, 0x93, 0x01): ("ATmega8",        "avr",   8192,  1024,  512),
    # ---- ATmega4809 ----
    (0x1E, 0x96, 0x51): ("ATmega4809",     "avr",  49152,  6144, 256),
    (0x1E, 0x96, 0x50): ("ATmega4808",     "avr",  49152,  6144, 256),
    (0x1E, 0x96, 0x52): ("ATmega4809",     "avr",  49152,  6144, 256),
    # ---- AT90USB ----
    (0x1E, 0x96, 0x82): ("AT90USB1286",    "avr", 131072,  8192, 4096),
    (0x1E, 0x96, 0x83): ("AT90USB1287",    "avr", 131072,  8192, 4096),
    (0x1E, 0x94, 0x81): ("AT90USB646",     "avr",  65536,  4096, 2048),
    (0x1E, 0x94, 0x82): ("AT90USB647",     "avr",  65536,  4096, 2048),
    # ---- ATtiny ----
    (0x1E, 0x93, 0x0C): ("ATtiny85",       "avr",   8192,   512,  512),
    (0x1E, 0x93, 0x0B): ("ATtiny84",       "avr",   8192,   512,  512),
    (0x1E, 0x91, 0x0E): ("ATtiny167",      "avr",  16384,   512,  512),
    (0x1E, 0x93, 0x08): ("ATtiny84A",      "avr",   8192,   512,  512),
    (0x1E, 0x91, 0x06): ("ATtiny2313",     "avr",   2048,   128,  128),
    (0x1E, 0x91, 0x0A): ("ATtiny4313",     "avr",   4096,   256,  256),
    (0x1E, 0x92, 0x08): ("ATtiny25",       "avr",   2048,   128,  128),
    (0x1E, 0x93, 0x09): ("ATtiny45",       "avr",   4096,   256,  256),
    (0x1E, 0x93, 0x0D): ("ATtiny261",      "avr",   2048,   128,  128),
    # ---- MK20/MK64/MK66 (Teensy 3.x) ----
    (0x04, 0x20, 0x00): ("MK20DX128",      "avr", 131072,  16384, 2048),
    (0x04, 0x20, 0x40): ("MK20DX256",      "avr", 262144,  65536, 2048),
    (0x04, 0x20, 0x80): ("MK64FX512",      "avr", 524288,  196608, 2048),
    (0x04, 0x20, 0xC0): ("MK66FX1M0",      "avr", 1048576, 262144, 4096),
    (0x04, 0x20, 0xC2): ("MK66NX1M0",      "avr", 1048576, 262144, 4096),
    (0x04, 0x20, 0xFF): ("MKL26Z64",       "avr",  65536,  16384, 2048),
    # ---- IMXRT (Teensy 4.x) ----
    (0x04, 0x2B, 0x00): ("IMXRT1062",      "avr", 16777216, 1048576, 4096),
    (0x04, 0x2B, 0x80): ("IMXRT1064",      "avr", 16777216, 1048576, 4096),
    # ---- SAMD21 ----
    (0x1E, 0x95, 0x01): ("ATSAMD21G18",    "samd", 262144,  32768, 16384),
    (0x1E, 0x95, 0x00): ("ATSAMD21E18",    "samd", 262144,  32768, 16384),
    (0x1E, 0x95, 0x1A): ("ATSAMD21J18",    "samd", 262144,  32768, 16384),
    # ---- SAMD51 ----
    (0x1E, 0x96, 0xA0): ("ATSAMD51J19",    "samd", 524288,  196608, 16384),
    (0x1E, 0x96, 0xA1): ("ATSAMD51J20",    "samd", 1048576, 196608, 16384),
    (0x1E, 0x96, 0xA2): ("ATSAMD51N20",    "samd", 1048576, 196608, 16384),
    (0x1E, 0x96, 0xA3): ("ATSAMD51P20",    "samd", 1048576, 196608, 16384),
    # ---- nRF52 ----
    (0x5A, 0x52, 0x29): ("nRF52832",       "nrf52", 524288,  65536, 4096),
    (0x5A, 0x52, 0x2A): ("nRF52840",        "nrf52", 1048576, 262144, 4096),
}


@dataclass
class BoardInfo:
    chip: str = "Desconocido"
    board_type: str = "unknown"
    signature: tuple = field(default_factory=tuple)
    flash_bytes: int = 0
    ram_bytes: int = 0    # type: ignore
    eeprom_bytes: int = 0
    fuses: dict = field(default_factory=dict)
    read_via: str = ""   # "avrdude", "arduino-cli", "sketch", "unknown"

    def to_dict(self):
        return {
            "chip": self.chip,
            "board_type": self.board_type,
            "signature": " ".join(f"{b:02X}" for b in self.signature),
            "flash_bytes": self.flash_bytes,
            "ram_bytes": self.ram_bytes,
            "eeprom_bytes": self.eeprom_bytes,
            "fuses": self.fuses,
            "read_via": self.read_via,
        }


def _find_tool(name: str) -> Optional[str]:
    """Busca una herramienta en el PATH."""
    return shutil.which(name)


def read_signature_via_avrdude(port: str, baud: int = 115200) -> BoardInfo:
    """Lee la firma del chip usando avrdude directamente."""
    info = BoardInfo()
    info.read_via = "avrdude"
    avrdude = _find_tool("avrdude")
    if not avrdude:
        raise FileNotFoundError("avrdude no esta instalado o no esta en PATH")
    cmd = [
        avrdude,
        "-c", "arduino",
        "-p", "m328p",        # asumimos Uno por defecto; el caller puede ajustar
        "-P", port,
        "-b", str(baud),
        "-U", "signature:r:-:h",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
    # Parseamos la firma hexadecimal del stdout
    sig_bytes: List[int] = []
    for line in proc.stdout.splitlines():
        line = line.strip()
        if all(c in "0123456789abcdefABCDEF" for c in line) and len(line) == 6:
            try:
                sig_bytes = [int(line[i:i+2], 16) for i in (0, 2, 4)]
                break
            except ValueError:
                continue
    if len(sig_bytes) == 3:
        info.signature = tuple(sig_bytes)
        if tuple(sig_bytes) in KNOWN_SIGNATURES:
            chip, board, fl, ram, eep = KNOWN_SIGNATURES[tuple(sig_bytes)]
            info.chip, info.board_type = chip, board
            info.flash_bytes, info.ram_bytes, info.eeprom_bytes = fl, ram, eep
        else:
            info.chip = f"Desconocido (sig 0x{''.join(f'{b:02X}' for b in sig_bytes)})"
    return info


def probe_port(port: str) -> BoardInfo:
    """Intenta identificar el chip usando avrdude.
    Si no está disponible, devuelve un BoardInfo vacío."""
    try:
        return read_signature_via_avrdude(port)
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
        info = BoardInfo()
        info.read_via = f"error: {type(e).__name__}: {e}"
        return info

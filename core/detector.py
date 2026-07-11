"""
core/detector.py

Deteccion de placas Arduino y compatibles conectadas por USB.
Escanea los puertos seriales disponibles e identifica:
1. VID/PID contra la base de datos usb_ident (100+ entradas)
2. Descripcion USB mediante heuristica board_heuristic
Compatible con Arduino oficial, clones chinos (CH340/CH341/CH9102),
FTDI, CP210x, PL2303, MCP2200, ESP32/ESP8266 nativos,
Teensy, Seeed, SparkFun, Adafruit, RobotDyn, dfrobot, y mas.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

import serial.tools.list_ports

from .usb_ident import (
    lookup, guess_by_description,
    ARCH_AVR, ARCH_SAMD, ARCH_RP2040, ARCH_ESP32,
    ARCH_ESP8266, ARCH_STM32, ARCH_NRF52, ARCH_UNKNOWN,
    USBProfile,
)
from .board_heuristic import identify, BoardHeuristic


@dataclass
class DetectedBoard:
    """Representa una placa detectada."""
    port: str
    description: str = ""
    hwid: str = ""
    vid: Optional[int] = None
    pid: Optional[int] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    guessed_name: str = "Desconocida"
    guessed_type: str = "unknown"   # avr | samd | rp2040 | esp32 | esp8266 | stm32 | nrf52 | unknown
    is_arduino_like: bool = False
    usb_profile: Optional[USBProfile] = None
    heuristic: Optional[BoardHeuristic] = None
    extra: dict = field(default_factory=dict)

    @property
    def arch(self) -> str:
        """Arquitectura del MCU principal."""
        if self.usb_profile:
            return self.usb_profile.arch
        if self.heuristic:
            return self.heuristic.arch
        return "unknown"

    def to_dict(self):
        return {
            "port": self.port,
            "description": self.description,
            "hwid": self.hwid,
            "vid": f"{self.vid:04X}" if self.vid else None,
            "pid": f"{self.pid:04X}" if self.pid else None,
            "serial": self.serial_number,
            "manufacturer": self.manufacturer,
            "product": self.product,
            "guessed_name": self.guessed_name,
            "guessed_type": self.guessed_type,
            "arch": self.arch,
            "is_arduino_like": self.is_arduino_like,
        }


class ArduinoDetector:
    """Escanea el sistema en busca de placas Arduino o compatibles."""

    @staticmethod
    def _parse_hwid(hwid: str):
        """Extrae VID y PID del string hwid que entrega pyserial."""
        vid = pid = None
        if not hwid:
            return vid, pid
        for token in hwid.split():
            token = token.upper()
            if token.startswith("VID="):
                try:
                    vid = int(token.split("=")[1], 16)
                except ValueError:
                    pass
            elif token.startswith("PID="):
                try:
                    pid = int(token.split("=")[1], 16)
                except ValueError:
                    pass
        return vid, pid

    @classmethod
    def _identify_board(cls, info) -> DetectedBoard:
        """Identifica una placa a partir de la info del puerto."""
        vid, pid = cls._parse_hwid(info.hwid or "")
        description = info.description or ""
        manufacturer = getattr(info, "manufacturer", None) or ""
        product = getattr(info, "product", None) or ""

        # 1) Buscar en base de datos VID/PID
        usb_profile: Optional[USBProfile] = None
        if vid is not None and pid is not None:
            usb_profile = lookup(vid, pid)

        # 2) Si no se encontro, usar heuristica por descripcion
        heuristic: Optional[BoardHeuristic] = None
        guessed_name = "Desconocida"
        guessed_type = "unknown"
        is_arduino_like = False

        if usb_profile:
            guessed_name = usb_profile.name
            guessed_type = usb_profile.arch
            is_arduino_like = usb_profile.is_arduino_brand
        else:
            # Intentar heuristica
            combined = " ".join([description, manufacturer, product])
            heuristic = identify(combined, manufacturer)
            if heuristic:
                guessed_name = heuristic.name
                guessed_type = heuristic.arch
                is_arduino_like = False  # heuristics son clones
            else:
                # Fallback: buscar en patrones simples de descripcion
                name_guess = guess_by_description(combined)
                if name_guess:
                    guessed_name = name_guess
                    # Inferir arquitectura del nombre
                    nl = guessed_name.lower()
                    if any(x in nl for x in ["esp32", "esp32-s", "esp32-c", "esp32-h"]):
                        guessed_type = "esp32"
                    elif "esp8266" in nl or "nodemcu" in nl or "wemos" in nl:
                        guessed_type = "esp8266"
                    elif "rp2040" in nl or "pico" in nl:
                        guessed_type = "rp2040"
                    elif any(x in nl for x in ["samd", "mkr", "zero"]):
                        guessed_type = "samd"
                    elif "nrf" in nl or "ble" in nl:
                        guessed_type = "nrf52"
                    elif "stm32" in nl:
                        guessed_type = "stm32"
                    elif any(x in nl for x in ["atmega", "attiny", "uno", "mega", "nano", "leonardo", "micro"]):
                        guessed_type = "avr"
                        is_arduino_like = True
                    else:
                        guessed_type = "unknown"

        return DetectedBoard(
            port=info.device,
            description=description,
            hwid=info.hwid or "",
            vid=vid,
            pid=pid,
            serial_number=getattr(info, "serial_number", None),
            manufacturer=manufacturer,
            product=product,
            guessed_name=guessed_name,
            guessed_type=guessed_type,
            is_arduino_like=is_arduino_like,
            usb_profile=usb_profile,
            heuristic=heuristic,
        )

    @classmethod
    def scan(cls, filter_arduino_only: bool = False) -> List[DetectedBoard]:
        """Devuelve todas las placas detectadas en los puertos seriales."""
        results: List[DetectedBoard] = []
        for info in serial.tools.list_ports.comports():
            board = cls._identify_board(info)
            if filter_arduino_only and not board.is_arduino_like:
                continue
            results.append(board)
        return results

    @classmethod
    def find_first(cls, only_arduino: bool = True) -> Optional[DetectedBoard]:
        """Devuelve la primera placa compatible encontrada o None."""
        boards = cls.scan()
        for b in boards:
            if only_arduino and not b.is_arduino_like:
                continue
            return b
        return None

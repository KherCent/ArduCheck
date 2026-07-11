"""Modulo core: logica principal de diagnostico de Arduino."""
from .detector import ArduinoDetector, DetectedBoard
from .board_info import BoardInfo, KNOWN_SIGNATURES, probe_port, read_signature_via_avrdude
from .parser import DiagnosticParser, TestRecord
from .runner import ArduinoDiagnostic, DiagnosticResult
from .watcher import HotplugWatcher, get_default_watcher
from .flasher import upload_sketch, compile_sketch, is_available as is_flasher_available
# Nuevos modulos de deteccion universal
from .usb_ident import (
    USBProfile, lookup, guess_by_description,
    ARCH_AVR, ARCH_SAMD, ARCH_RP2040, ARCH_ESP32,
    ARCH_ESP8266, ARCH_STM32, ARCH_NRF52, ARCH_UNKNOWN,
)
from .board_heuristic import (
    BoardHeuristic, identify, arch_to_sketch_folder, arch_to_uploader,
)

__all__ = [
    # Detector
    "ArduinoDetector",
    "DetectedBoard",
    # Board info
    "BoardInfo",
    "KNOWN_SIGNATURES",
    "probe_port",
    "read_signature_via_avrdude",
    # Parser y runner
    "DiagnosticParser",
    "TestRecord",
    "ArduinoDiagnostic",
    "DiagnosticResult",
    # Watcher
    "HotplugWatcher",
    "get_default_watcher",
    # Flasher
    "upload_sketch",
    "compile_sketch",
    "is_flasher_available",
    # USB identification
    "USBProfile",
    "lookup",
    "guess_by_description",
    # Heuristic
    "BoardHeuristic",
    "identify",
    "arch_to_sketch_folder",
    "arch_to_uploader",
    # Constantes de arquitectura
    "ARCH_AVR",
    "ARCH_SAMD",
    "ARCH_RP2040",
    "ARCH_ESP32",
    "ARCH_ESP8266",
    "ARCH_STM32",
    "ARCH_NRF52",
    "ARCH_UNKNOWN",
]

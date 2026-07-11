"""
core/board_heuristic.py

Heuristica para identificar placas Arduino y compatibles
cuando el VID/PID no esta en la base de datos,
usando la descripcion USB del fabricante.

Esto permite identificar placas por su nombre de producto
sin necesidad de VID/PID conocidos.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Optional


# Arquitecturas soportadas
ARCH_AVR     = "avr"
ARCH_SAMD    = "samd"
ARCH_RP2040  = "rp2040"
ARCH_ESP32   = "esp32"
ARCH_ESP8266 = "esp8266"
ARCH_STM32   = "stm32"
ARCH_NRF52   = "nrf52"
ARCH_UNKNOWN = "unknown"


@dataclass
class BoardHeuristic:
    name: str
    mcu: str
    arch: str
    flash_kb: int
    ram_kb: int
    sketch_baud: int


# Tabla de heuristicas por patron de descripcion
# Cada entrada: (regex_compilada, BoardHeuristic)
BOARD_PATTERNS: list = [

    # ============ ARDUINO OFICIAL ============
    (re.compile(r"arduino\s+uno", re.I), BoardHeuristic(
        "Arduino Uno", "ATmega328P", ARCH_AVR, 32, 2, 115200)),
    (re.compile(r"arduino\s+mega\s*2560", re.I), BoardHeuristic(
        "Arduino Mega 2560", "ATmega2560", ARCH_AVR, 256, 8, 115200)),
    (re.compile(r"arduino\s+mega", re.I), BoardHeuristic(
        "Arduino Mega (genérico)", "ATmega2560", ARCH_AVR, 256, 8, 115200)),
    (re.compile(r"arduino\s+nano", re.I), BoardHeuristic(
        "Arduino Nano", "ATmega328P", ARCH_AVR, 32, 2, 57600)),
    (re.compile(r"arduino\s+leonardo", re.I), BoardHeuristic(
        "Arduino Leonardo", "ATmega32U4", ARCH_AVR, 32, 2, 57600)),
    (re.compile(r"arduino\s+micro", re.I), BoardHeuristic(
        "Arduino Micro", "ATmega32U4", ARCH_AVR, 32, 2, 57600)),
    (re.compile(r"arduino\s+pro\s*mini", re.I), BoardHeuristic(
        "Arduino Pro Mini", "ATmega328P", ARCH_AVR, 32, 2, 57600)),
    (re.compile(r"arduino\s+mini", re.I), BoardHeuristic(
        "Arduino Mini", "ATmega328P", ARCH_AVR, 32, 2, 57600)),
    (re.compile(r"arduino\s+diecimila", re.I), BoardHeuristic(
        "Arduino Diecimila", "ATmega168", ARCH_AVR, 16, 1, 19200)),
    (re.compile(r"arduino\s+ng", re.I), BoardHeuristic(
        "Arduino NG", "ATmega168", ARCH_AVR, 16, 1, 19200)),
    (re.compile(r"arduino\s+duemilanove", re.I), BoardHeuristic(
        "Arduino Duemilanove", "ATmega168", ARCH_AVR, 16, 1, 57600)),
    (re.compile(r"arduino\s+uno\s*r3", re.I), BoardHeuristic(
        "Arduino Uno R3", "ATmega328P", ARCH_AVR, 32, 2, 115200)),
    (re.compile(r"arduino\s+fio", re.I), BoardHeuristic(
        "Arduino Fio", "ATmega328P", ARCH_AVR, 32, 2, 57600)),
    (re.compile(r"arduino\s+esplora", re.I), BoardHeuristic(
        "Arduino Esplora", "ATmega32U4", ARCH_AVR, 32, 2, 57600)),
    (re.compile(r"arduino\s+gemma", re.I), BoardHeuristic(
        "Arduino Gemma", "ATtiny85", ARCH_AVR, 8, 0, 9600)),
    (re.compile(r"arduino\s+lilypad", re.I), BoardHeuristic(
        "Arduino LilyPad", "ATmega168", ARCH_AVR, 16, 1, 57600)),
    (re.compile(r"arduino\s+101", re.I), BoardHeuristic(
        "Arduino 101", "Intel Curie", ARCH_UNKNOWN, 196, 24, 115200)),
    (re.compile(r"arduino\s+zero", re.I), BoardHeuristic(
        "Arduino Zero", "ATSAMD21G18", ARCH_SAMD, 256, 32, 115200)),
    (re.compile(r"arduino\s+mkr\s*1000", re.I), BoardHeuristic(
        "Arduino MKR1000", "ATSAMD21G18", ARCH_SAMD, 256, 32, 115200)),
    (re.compile(r"arduino\s+mkr\s*(fox|gsm|nb|zero|fox)", re.I), BoardHeuristic(
        "Arduino MKR", "ATSAMD21G18", ARCH_SAMD, 256, 32, 115200)),
    (re.compile(r"arduino\s+mkr\s*wifi\s*1010", re.I), BoardHeuristic(
        "Arduino MKR WiFi 1010", "ATSAMD21G18", ARCH_SAMD, 256, 32, 115200)),
    (re.compile(r"arduino\s+mkr\s*vidor", re.I), BoardHeuristic(
        "Arduino MKR Vidor 4000", "ATSAMD21G18+FPGA", ARCH_SAMD, 256, 32, 115200)),
    (re.compile(r"arduino\s+nano\s*33\s*iot", re.I), BoardHeuristic(
        "Arduino Nano 33 IoT", "ATSAMD21G18", ARCH_SAMD, 256, 32, 115200)),
    (re.compile(r"arduino\s+nano\s*33\s*ble", re.I), BoardHeuristic(
        "Arduino Nano 33 BLE", "nRF52840", ARCH_NRF52, 1024, 256, 115200)),
    (re.compile(r"arduino\s+nano\s*33\s*ble\s*sense", re.I), BoardHeuristic(
        "Arduino Nano 33 BLE Sense", "nRF52840", ARCH_NRF52, 1024, 256, 115200)),
    (re.compile(r"arduino\s+nano\s*rp2040", re.I), BoardHeuristic(
        "Arduino Nano RP2040 Connect", "RP2040", ARCH_RP2040, 16384, 264, 1200)),
    (re.compile(r"arduino\s+nano\s*esp32", re.I), BoardHeuristic(
        "Arduino Nano ESP32", "ESP32-S3", ARCH_ESP32, 4096, 512, 115200)),
    (re.compile(r"arduino\s+nano\s*every", re.I), BoardHeuristic(
        "Arduino Nano Every", "ATmega4809", ARCH_AVR, 48, 6, 115200)),
    (re.compile(r"arduino\s+portenta", re.I), BoardHeuristic(
        "Arduino Portenta H7", "STM32H747", ARCH_STM32, 8192, 1024, 115200)),
    (re.compile(r"arduino\s+giga", re.I), BoardHeuristic(
        "Arduino Giga", "STM32H747", ARCH_STM32, 8192, 1024, 115200)),
    (re.compile(r"arduino\s+(itsybitsy|feather|metro|trinket|qtpy|gemma)",
                 re.I), BoardHeuristic(
        "Arduino-compatiple Adafruit", "desconocido", ARCH_UNKNOWN, 0, 0, 115200)),

    # ============ ESP8266 ============
    (re.compile(r"nodemcu", re.I), BoardHeuristic(
        "NodeMCU (ESP8266)", "ESP8266", ARCH_ESP8266, 4096, 160, 115200)),
    (re.compile(r"esp8266", re.I), BoardHeuristic(
        "ESP8266", "ESP8266", ARCH_ESP8266, 4096, 160, 115200)),
    (re.compile(r"wemos\s*d1", re.I), BoardHeuristic(
        "Wemos D1 Mini (ESP8266)", "ESP8266", ARCH_ESP8266, 4096, 160, 115200)),
    (re.compile(r"lolind1", re.I), BoardHeuristic(
        "Lolin D1 Mini (ESP8266)", "ESP8266", ARCH_ESP8266, 4096, 160, 115200)),
    (re.compile(r"esp-12e", re.I), BoardHeuristic(
        "ESP-12E (ESP8266)", "ESP8266", ARCH_ESP8266, 4096, 160, 115200)),
    (re.compile(r"esp-12f", re.I), BoardHeuristic(
        "ESP-12F (ESP8266)", "ESP8266", ARCH_ESP8266, 4096, 160, 115200)),

    # ============ ESP32 ============
    (re.compile(r"esp32\s*-?\s*s3", re.I), BoardHeuristic(
        "ESP32-S3", "ESP32-S3", ARCH_ESP32, 8192, 512, 115200)),
    (re.compile(r"esp32\s*-?\s*c3", re.I), BoardHeuristic(
        "ESP32-C3", "ESP32-C3", ARCH_ESP32, 4096, 400, 115200)),
    (re.compile(r"esp32\s*-?\s*c6", re.I), BoardHeuristic(
        "ESP32-C6", "ESP32-C6", ARCH_ESP32, 4096, 512, 115200)),
    (re.compile(r"esp32\s*-?\s*s2", re.I), BoardHeuristic(
        "ESP32-S2", "ESP32-S2", ARCH_ESP32, 4096, 320, 115200)),
    (re.compile(r"esp32\s*-?\s*h2", re.I), BoardHeuristic(
        "ESP32-H2", "ESP32-H2", ARCH_ESP32, 2048, 256, 115200)),
    (re.compile(r"esp32", re.I), BoardHeuristic(
        "ESP32", "ESP32", ARCH_ESP32, 4096, 512, 115200)),
    (re.compile(r"m5stack", re.I), BoardHeuristic(
        "M5Stack (ESP32)", "ESP32", ARCH_ESP32, 4096, 512, 115200)),
    (re.compile(r"t-display", re.I), BoardHeuristic(
        "T-Display (ESP32)", "ESP32", ARCH_ESP32, 4096, 512, 115200)),
    (re.compile(r"lilygo", re.I), BoardHeuristic(
        "LilyGo (ESP32/ESP8266)", "ESP32", ARCH_ESP32, 4096, 512, 115200)),
    (re.compile(r"wt32", re.I), BoardHeuristic(
        "WT32-ETH01 (ESP32)", "ESP32", ARCH_ESP32, 4096, 512, 115200)),

    # ============ RP2040 ============
    (re.compile(r"rp2040", re.I), BoardHeuristic(
        "RP2040", "RP2040", ARCH_RP2040, 16384, 264, 1200)),
    (re.compile(r"raspberry\s+pi\s+pico", re.I), BoardHeuristic(
        "Raspberry Pi Pico", "RP2040", ARCH_RP2040, 16384, 264, 1200)),
    (re.compile(r"pico\s*w", re.I), BoardHeuristic(
        "Raspberry Pi Pico W", "RP2040", ARCH_RP2040, 16384, 264, 1200)),
    (re.compile(r"arduino\s+nano\s+rp2040", re.I), BoardHeuristic(
        "Arduino Nano RP2040 Connect", "RP2040", ARCH_RP2040, 16384, 264, 1200)),
    (re.compile(r"adafruit\s+(feather|itsybitsy|metro)\s*rp2040", re.I), BoardHeuristic(
        "Adafruit RP2040", "RP2040", ARCH_RP2040, 16384, 264, 1200)),
    (re.compile(r"sparkfun\s+rp2040", re.I), BoardHeuristic(
        "SparkFun RP2040", "RP2040", ARCH_RP2040, 16384, 264, 1200)),
    (re.compile(r"seeed\s+.*rp2040", re.I), BoardHeuristic(
        "Seeeduino RP2040", "RP2040", ARCH_RP2040, 16384, 264, 1200)),
    (re.compile(r"xiao\s+rp2040", re.I), BoardHeuristic(
        "Seeed XIAO RP2040", "RP2040", ARCH_RP2040, 16384, 264, 1200)),
    (re.compile(r"cytron\s+rp2040", re.I), BoardHeuristic(
        "CYTRON RP2040", "RP2040", ARCH_RP2040, 16384, 264, 1200)),

    # ============ SAMD (Zero, MKR, Nano 33) ============
    (re.compile(r"sam\s*d21", re.I), BoardHeuristic(
        "SAMD21 (Arduino Zero/MKR/Nano 33)", "ATSAMD21G18", ARCH_SAMD, 256, 32, 115200)),
    (re.compile(r"sam\s*d51", re.I), BoardHeuristic(
        "SAMD51", "ATSAMD51", ARCH_SAMD, 512, 192, 115200)),
    (re.compile(r"samd", re.I), BoardHeuristic(
        "SAMD (Arduino MKR/Zero)", "ATSAMD21G18", ARCH_SAMD, 256, 32, 115200)),
    (re.compile(r"atsamd21", re.I), BoardHeuristic(
        "ATSAMD21", "ATSAMD21G18", ARCH_SAMD, 256, 32, 115200)),
    (re.compile(r"atsamd51", re.I), BoardHeuristic(
        "ATSAMD51", "ATSAMD51", ARCH_SAMD, 512, 192, 115200)),

    # ============ nRF52 (Nano 33 BLE) ============
    (re.compile(r"nrf52840", re.I), BoardHeuristic(
        "nRF52840", "nRF52840", ARCH_NRF52, 1024, 256, 115200)),
    (re.compile(r"nrf52832", re.I), BoardHeuristic(
        "nRF52832", "nRF52832", ARCH_NRF52, 512, 64, 115200)),
    (re.compile(r"ble\s*sense", re.I), BoardHeuristic(
        "Nano 33 BLE Sense", "nRF52840", ARCH_NRF52, 1024, 256, 115200)),

    # ============ STM32 ============
    (re.compile(r"stm32h7", re.I), BoardHeuristic(
        "STM32H7 (Portenta H7)", "STM32H747", ARCH_STM32, 8192, 1024, 115200)),
    (re.compile(r"stm32f4", re.I), BoardHeuristic(
        "STM32F4", "STM32F405", ARCH_STM32, 1024, 192, 115200)),
    (re.compile(r"stm32f7", re.I), BoardHeuristic(
        "STM32F7", "STM32F746", ARCH_STM32, 2048, 512, 115200)),
    (re.compile(r"stm32f1", re.I), BoardHeuristic(
        "STM32F1 (BluePill)", "STM32F103C8", ARCH_STM32, 64, 20, 115200)),
    (re.compile(r"stm32", re.I), BoardHeuristic(
        "STM32", "STM32", ARCH_STM32, 512, 128, 115200)),

    # ============ TEENSY ============
    (re.compile(r"teensy\s*4\.?1", re.I), BoardHeuristic(
        "Teensy 4.1", "IMXRT1062", ARCH_AVR, 7936, 1024, 115200)),
    (re.compile(r"teensy\s*4\.?0", re.I), BoardHeuristic(
        "Teensy 4.0", "IMXRT1062", ARCH_AVR, 1984, 512, 115200)),
    (re.compile(r"teensy\s*3\.?6", re.I), BoardHeuristic(
        "Teensy 3.6", "MK66FX1M0", ARCH_AVR, 256, 256, 115200)),
    (re.compile(r"teensy\s*3\.?5", re.I), BoardHeuristic(
        "Teensy 3.5", "MK64FX512", ARCH_AVR, 512, 192, 115200)),
    (re.compile(r"teensy\s*3\.?2", re.I), BoardHeuristic(
        "Teensy 3.2", "MK20DX256", ARCH_AVR, 256, 64, 115200)),
    (re.compile(r"teensy\s*3\.?1", re.I), BoardHeuristic(
        "Teensy 3.1", "MK20DX256", ARCH_AVR, 256, 64, 115200)),
    (re.compile(r"teensy\s*3\.?0", re.I), BoardHeuristic(
        "Teensy 3.0", "MK20DX128", ARCH_AVR, 128, 32, 115200)),
    (re.compile(r"teensy\s*lc", re.I), BoardHeuristic(
        "Teensy LC", "MKL26Z64", ARCH_AVR, 64, 8, 115200)),
    (re.compile(r"teensy\s*2\.?0", re.I), BoardHeuristic(
        "Teensy 2.0", "ATmega32U4", ARCH_AVR, 32, 2, 57600)),
    (re.compile(r"teensy\s*\+\+", re.I), BoardHeuristic(
        "Teensy++ 2.0", "AT90USB1286", ARCH_AVR, 128, 8, 57600)),
    (re.compile(r"teensy", re.I), BoardHeuristic(
        "Teensy", "desconocido", ARCH_AVR, 256, 64, 115200)),

    # ============ CLONES / FABRICANTES ============
    (re.compile(r"sparkfun", re.I), BoardHeuristic(
        "SparkFun (Arduino-compatibles)", "ATmega328P", ARCH_AVR, 32, 2, 115200)),
    (re.compile(r"adafruit", re.I), BoardHeuristic(
        "Adafruit (Arduino-compatibles)", "desconocido", ARCH_UNKNOWN, 0, 0, 115200)),
    (re.compile(r"pololu", re.I), BoardHeuristic(
        "Pololu (Arduino-compatibles)", "ATmega32U4", ARCH_AVR, 32, 2, 115200)),
    (re.compile(r"digispark", re.I), BoardHeuristic(
        "Digispark (ATtiny85)", "ATtiny85", ARCH_AVR, 8, 0, 115200)),
    (re.compile(r"robotdyn", re.I), BoardHeuristic(
        "RobotDyn (Arduino-compatibles)", "ATmega328P", ARCH_AVR, 32, 2, 115200)),
    (re.compile(r"dfrobot", re.I), BoardHeuristic(
        "DFRobot (Arduino-compatibles)", "ATmega328P", ARCH_AVR, 32, 2, 115200)),
    (re.compile(r"makerfabs", re.I), BoardHeuristic(
        "Makerfabs (Arduino-compatibles)", "ESP32", ARCH_ESP32, 4096, 512, 115200)),
    (re.compile(r"seeed", re.I), BoardHeuristic(
        "Seeed Studio (Arduino-compatibles)", "desconocido", ARCH_UNKNOWN, 0, 0, 115200)),
    (re.compile(r"cytron", re.I), BoardHeuristic(
        "CYTRON (Arduino-compatibles)", "desconocido", ARCH_UNKNOWN, 0, 0, 115200)),
    (re.compile(r"elecrow", re.I), BoardHeuristic(
        "Elecrow (Arduino-compatibles)", "desconocido", ARCH_UNKNOWN, 0, 0, 115200)),
    (re.compile(r"keywish", re.I), BoardHeuristic(
        "KeyWish (Arduino-compatibles)", "desconocido", ARCH_UNKNOWN, 0, 0, 115200)),
    (re.compile(r"funny", re.I), BoardHeuristic(
        "FunTech (Arduino-compatibles)", "desconocido", ARCH_UNKNOWN, 0, 0, 115200)),
    (re.compile(r"kl100", re.I), BoardHeuristic(
        "KL100 (Keyestudio)", "ATmega328P", ARCH_AVR, 32, 2, 115200)),

    # ============ CONVERTIDORES USB-SERIAL (identificados solo por chip) ============
    (re.compile(r"ch340", re.I), BoardHeuristic(
        "USB-Serial CH340 (clon chino)", "CH340", ARCH_AVR, 0, 0, 115200)),
    (re.compile(r"ch341", re.I), BoardHeuristic(
        "USB-Serial CH341 (clon chino)", "CH341", ARCH_AVR, 0, 0, 115200)),
    (re.compile(r"ch9102", re.I), BoardHeuristic(
        "USB-Serial CH9102 (clon chino)", "CH9102", ARCH_AVR, 0, 0, 115200)),
    (re.compile(r"pl2303", re.I), BoardHeuristic(
        "USB-Serial PL2303 (Prolific)", "PL2303", ARCH_AVR, 0, 0, 115200)),
    (re.compile(r"cp210", re.I), BoardHeuristic(
        "USB-Serial CP210x (Silicon Labs)", "CP210x", ARCH_AVR, 0, 0, 115200)),
    (re.compile(r"ft232", re.I), BoardHeuristic(
        "USB-Serial FT232 (FTDI)", "FT232R", ARCH_AVR, 0, 0, 115200)),
    (re.compile(r"ft2232", re.I), BoardHeuristic(
        "USB-Serial FT2232 (FTDI)", "FT2232", ARCH_AVR, 0, 0, 115200)),
    (re.compile(r"ftdi", re.I), BoardHeuristic(
        "USB-Serial FTDI", "FTDI", ARCH_AVR, 0, 0, 115200)),
    (re.compile(r"mcp2200", re.I), BoardHeuristic(
        "USB-Serial MCP2200 (Microchip)", "MCP2200", ARCH_AVR, 0, 0, 115200)),

    # ============ FALLBACKS ============
    (re.compile(r"atmeg", re.I), BoardHeuristic(
        "MCU AVR (Arduino-compatibles)", "ATmega", ARCH_AVR, 32, 2, 115200)),
    (re.compile(r"attiny", re.I), BoardHeuristic(
        "ATtiny (Arduino-compatibles)", "ATtiny", ARCH_AVR, 8, 0, 9600)),
    (re.compile(r"usb serial", re.I), BoardHeuristic(
        "USB Serial genérico", "desconocido", ARCH_UNKNOWN, 0, 0, 115200)),
    (re.compile(r"usb device", re.I), BoardHeuristic(
        "USB genérico", "desconocido", ARCH_UNKNOWN, 0, 0, 115200)),
]


def identify(description: str, manufacturer: Optional[str] = None) -> Optional[BoardHeuristic]:
    """Identifica una placa a partir de la descripcion y fabricante.

    Busca primero en description, luego en manufacturer.
    Devuelve None si no se reconoce nada.
    """
    candidates: list = []

    def _search(text: str):
        for pattern, heuristic in BOARD_PATTERNS:
            if pattern.search(text):
                candidates.append(heuristic)
                break

    if description:
        _search(description)
    if manufacturer:
        _search(manufacturer)

    if not candidates:
        return None
    # Devolver el primero (mas especifico) que coincida
    return candidates[0]


def arch_to_sketch_folder(arch: str) -> Optional[str]:
    """Devuelve la ruta relativa del sketch de auto-test segun arquitectura."""
    mapping = {
        ARCH_AVR:     "firmware/avr/diagnostic_sketch.ino",
        ARCH_SAMD:    "firmware/samd/diagnostic_sketch.ino",
        ARCH_RP2040:  "firmware/rp2040/diagnostic_sketch.ino",
        ARCH_ESP32:   "firmware/esp32/diagnostic_sketch.ino",
        ARCH_ESP8266: "firmware/esp8266/diagnostic_sketch.ino",
        ARCH_STM32:   "firmware/stm32/diagnostic_sketch.ino",
        ARCH_NRF52:   "firmware/nrf52/diagnostic_sketch.ino",
    }
    return mapping.get(arch)


def arch_to_uploader(arch: str) -> Optional[str]:
    """Devuelve el nombre de la herramienta para subir sketches."""
    mapping = {
        ARCH_AVR:     "avrdude",
        ARCH_SAMD:    "bossac",
        ARCH_RP2040:  "picotool",
        ARCH_ESP32:   "esptool.py",
        ARCH_ESP8266: "esptool.py",
        ARCH_STM32:   "stm32flash",
        ARCH_NRF52:   "nrfjprog",
    }
    return mapping.get(arch)

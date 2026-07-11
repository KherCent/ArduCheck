"""
core/usb_ident.py

Base de datos completa de VID/PID de convertidores USB-Serial
usados en placas Arduino y clones chinos de todo tipo.

Cobertura: CH340, CH341, PL2303, FTDI, CP210x, MCP2200,
ATmega16U2 nativo, CDM/CDC, Teensy, ESP32/ESP8266 nativos,
Wemos/Lolin, Seeed, RobotDyn, y muchos mas.

Cada entrada: (VID, PID) -> (nombre, chip_sugerido, arquitectura, baud_default)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


# Arquitectura del chip principal de la placa
ARCH_AVR    = "avr"
ARCH_SAMD   = "samd"
ARCH_RP2040 = "rp2040"
ARCH_ESP32  = "esp32"
ARCH_ESP8266= "esp8266"
ARCH_STM32  = "stm32"
ARCH_NRF52  = "nrf52"
ARCH_UNKNOWN= "unknown"


@dataclass
class USBProfile:
    name: str
    chip_type: str           # tipo de convertidor o SoC
    arch: str               # arquitectura del MCU principal
    baud_default: int       # baudios por defecto del bootloader
    is_arduino_brand: bool
    mcu_hint: str           # nombre del MCU estimado

    def to_dict(self):
        return {
            "name": self.name,
            "chip_type": self.chip_type,
            "arch": self.arch,
            "baud_default": self.baud_default,
            "is_arduino_brand": self.is_arduino_brand,
            "mcu_hint": self.mcu_hint,
        }


# =============================================================================
# BASE DE DATOS: VID/PID -> Perfil
# =============================================================================
# Formato: (VID_hex, PID_hex) -> USBProfile
USB_DATABASE: Dict[Tuple[int, int], USBProfile] = {

    # ---------- ARDUINO OFICIAL ----------
    (0x2341, 0x003C): USBProfile("Arduino Leonardo (bootloader)", "ATmega32U4", ARCH_AVR, 57600, True, "ATmega32U4"),
    (0x2341, 0x003D): USBProfile("Arduino Micro (bootloader)", "ATmega32U4", ARCH_AVR, 57600, True, "ATmega32U4"),
    (0x2341, 0x003E): USBProfile("Arduino Gemma", "ATtiny85", ARCH_AVR, 9600, True, "ATtiny85"),
    (0x2341, 0x003F): USBProfile("Arduino LilyPad USB", "ATmega32U4", ARCH_AVR, 57600, True, "ATmega32U4"),
    (0x2341, 0x0040): USBProfile("Arduino Esplora", "ATmega32U4", ARCH_AVR, 57600, True, "ATmega32U4"),
    (0x2341, 0x0041): USBProfile("Arduino Yun", "ATmega32U4+AR9331", ARCH_AVR, 115200, True, "ATmega32U4"),
    (0x2341, 0x0042): USBProfile("Arduino Mega 2560", "ATmega2560+16U2", ARCH_AVR, 115200, True, "ATmega2560"),
    (0x2341, 0x0043): USBProfile("Arduino Uno", "ATmega328P+16U2", ARCH_AVR, 115200, True, "ATmega328P"),
    (0x2341, 0x0044): USBProfile("Arduino Nano", "ATmega328P+FTDI", ARCH_AVR, 57600, True, "ATmega328P"),
    (0x2341, 0x0045): USBProfile("Arduino Pro Mini (3.3V)", "ATmega328P", ARCH_AVR, 57600, True, "ATmega328P"),
    (0x2341, 0x0046): USBProfile("Arduino Pro Mini (5V)", "ATmega328P", ARCH_AVR, 115200, True, "ATmega328P"),
    (0x2341, 0x0047): USBProfile("Arduino NG", "ATmega168", ARCH_AVR, 19200, True, "ATmega168"),
    (0x2341, 0x0048): USBProfile("Arduino Diecimila", "ATmega168", ARCH_AVR, 19200, True, "ATmega168"),
    (0x2341, 0x0049): USBProfile("Arduino Mega (old bootloader)", "ATmega1280", ARCH_AVR, 57600, True, "ATmega1280"),
    (0x2341, 0x004A): USBProfile("Arduino Mega ADK", "ATmega2560+MAX3421E", ARCH_AVR, 115200, True, "ATmega2560"),
    (0x2341, 0x004B): USBProfile("Arduino UNO (alt)", "ATmega328P+16U2", ARCH_AVR, 115200, True, "ATmega328P"),
    (0x2341, 0x004C): USBProfile("Arduino Mega (alt)", "ATmega1280", ARCH_AVR, 57600, True, "ATmega1280"),
    (0x2341, 0x004D): USBProfile("Arduino Mini (FTDI)", "ATmega168", ARCH_AVR, 57600, True, "ATmega168"),
    (0x2341, 0x004E): USBProfile("Arduino Fio", "ATmega328P", ARCH_AVR, 57600, True, "ATmega328P"),
    # Arduino 101 (Intel Curie)
    (0x2341, 0x004F): USBProfile("Arduino 101", "Intel Curie", ARCH_UNKNOWN, 115200, True, "Intel Curie"),
    # Arduino Zero
    (0x2341, 0x0050): USBProfile("Arduino Zero (Native)", "ATSAMD21G18", ARCH_SAMD, 115200, True, "SAMD21"),
    (0x2341, 0x0051): USBProfile("Arduino Zero (Programming)", "AT32UC3C", ARCH_SAMD, 115200, True, "SAMD21"),
    # Arduino MKR
    (0x2341, 0x0052): USBProfile("Arduino MKR1000", "ATSAMD21G18", ARCH_SAMD, 115200, True, "SAMD21"),
    (0x2341, 0x0053): USBProfile("Arduino MKR FOX 1200", "ATSAMD21G18", ARCH_SAMD, 115200, True, "SAMD21"),
    (0x2341, 0x0054): USBProfile("Arduino MKR GSM 1400", "ATSAMD21G18", ARCH_SAMD, 115200, True, "SAMD21"),
    (0x2341, 0x0055): USBProfile("Arduino MKR WiFi 1010", "ATSAMD21G18", ARCH_SAMD, 115200, True, "SAMD21"),
    (0x2341, 0x0056): USBProfile("Arduino MKR NB 1500", "ATSAMD21G18", ARCH_SAMD, 115200, True, "SAMD21"),
    (0x2341, 0x0057): USBProfile("Arduino MKR Vidor 4000", "ATSAMD21G18+FPGA", ARCH_SAMD, 115200, True, "SAMD21+FPGA"),
    # Arduino Nano 33
    (0x2341, 0x0058): USBProfile("Arduino Nano 33 IoT", "ATSAMD21G18", ARCH_SAMD, 115200, True, "SAMD21"),
    (0x2341, 0x0059): USBProfile("Arduino Nano 33 BLE (nRF52840)", "nRF52840", ARCH_NRF52, 115200, True, "nRF52840"),
    (0x2341, 0x005A): USBProfile("Arduino Nano 33 BLE Sense", "nRF52840", ARCH_NRF52, 115200, True, "nRF52840"),
    (0x2341, 0x005B): USBProfile("Arduino Nano RP2040 Connect", "RP2040", ARCH_RP2040, 1200, True, "RP2040"),
    (0x2341, 0x005C): USBProfile("Arduino Portenta H7", "STM32H747", ARCH_STM32, 115200, True, "STM32H747"),
    (0x2341, 0x005D): USBProfile("Arduino Nano Every", "ATmega4809", ARCH_AVR, 115200, True, "ATmega4809"),
    (0x2341, 0x005E): USBProfile("Arduino Zero (native, alt)", "ATSAMD21G18", ARCH_SAMD, 115200, True, "SAMD21"),
    (0x2341, 0x005F): USBProfile("Arduino MKR Vidor 4000 (alt)", "ATSAMD21G18", ARCH_SAMD, 115200, True, "SAMD21"),
    (0x2341, 0x0060): USBProfile("Arduino Nano ESP32", "ESP32-S3", ARCH_ESP32, 115200, True, "ESP32-S3"),
    (0x2341, 0x0061): USBProfile("Arduino Giga", "STM32H747", ARCH_STM32, 115200, True, "STM32H747"),
    (0x2341, 0x0062): USBProfile("Arduino Nano 33 BLE Sense Rev2", "nRF52840", ARCH_NRF52, 115200, True, "nRF52840"),
    # ---- Arduino USB CDC (COM ports virtuales) ----
    (0x2341, 0x8036): USBProfile("Arduino Leonardo (CDC)", "ATmega32U4", ARCH_AVR, 57600, True, "ATmega32U4"),
    (0x2341, 0x8037): USBProfile("Arduino Micro (CDC)", "ATmega32U4", ARCH_AVR, 57600, True, "ATmega32U4"),
    (0x2341, 0x8038): USBProfile("Arduino Esplora (CDC)", "ATmega32U4", ARCH_AVR, 57600, True, "ATmega32U4"),

    # ---------- CLONES ARDUINO (vendor 0x2A03) ----------
    (0x2A03, 0x0043): USBProfile("Arduino Uno (clon 0x2A03)", "ATmega328P", ARCH_AVR, 115200, False, "ATmega328P"),
    (0x2A03, 0x0042): USBProfile("Arduino Mega 2560 (clon 0x2A03)", "ATmega2560", ARCH_AVR, 115200, False, "ATmega2560"),
    (0x2A03, 0x0010): USBProfile("Arduino Nano (clon 0x2A03)", "ATmega328P", ARCH_AVR, 57600, False, "ATmega328P"),
    (0x2A03, 0x0011): USBProfile("Arduino Pro Mini (clon)", "ATmega328P", ARCH_AVR, 57600, False, "ATmega328P"),
    (0x2A03, 0x8036): USBProfile("Arduino Leonardo (clon)", "ATmega32U4", ARCH_AVR, 57600, False, "ATmega32U4"),

    # ---------- OTROS FABRICANTES CON ARDUINO-COMPATIBLES ----------
    (0x1B4F, 0x9206): USBProfile("Arduino Micro (SparkFun)", "ATmega32U4", ARCH_AVR, 57600, False, "ATmega32U4"),
    (0x1B4F, 0x9208): USBProfile("Arduino Pro Micro (SparkFun)", "ATmega32U4", ARCH_AVR, 57600, False, "ATmega32U4"),
    (0x1B4F, 0x9210): USBProfile("Arduino Fio (SparkFun)", "ATmega328P", ARCH_AVR, 57600, False, "ATmega328P"),
    (0x239A, 0x800B): USBProfile("Adafruit ItsyBitsy M0", "ATSAMD21", ARCH_SAMD, 115200, False, "SAMD21"),
    (0x239A, 0x800F): USBProfile("Adafruit Feather M0", "ATSAMD21", ARCH_SAMD, 115200, False, "SAMD21"),
    (0x239A, 0x8022): USBProfile("Adafruit Metro M4", "ATSAMD51", ARCH_SAMD, 115200, False, "SAMD51"),
    (0x239A, 0x80CD): USBProfile("Adafruit QT Py RP2040", "RP2040", ARCH_RP2040, 1200, False, "RP2040"),
    (0x239A, 0x80F1): USBProfile("Adafruit Feather RP2040", "RP2040", ARCH_RP2040, 1200, False, "RP2040"),
    (0x239A, 0x000B): USBProfile("Adafruit Gemma M0", "ATSAMD21", ARCH_SAMD, 115200, False, "SAMD21"),
    (0x239A, 0x8012): USBProfile("Adafruit Trinket M0", "ATSAMD21", ARCH_SAMD, 115200, False, "SAMD21"),
    (0x239A, 0x800C): USBProfile("Adafruit ItsyBitsy M4", "ATSAMD51", ARCH_SAMD, 115200, False, "SAMD51"),
    (0x239A, 0x8034): USBProfile("Adafruit Metro M4 AirLift", "ATSAMD51", ARCH_SAMD, 115200, False, "SAMD51"),
    (0x2886, 0x002D): USBProfile("Seeeduino XIAO", "ATSAMD21G18", ARCH_SAMD, 115200, False, "SAMD21"),
    (0x2886, 0x8001): USBProfile("Seeeduino Lotus (ATmega)", "ATmega32U4", ARCH_AVR, 57600, False, "ATmega32U4"),
    (0x2886, 0x8002): USBProfile("Seeeduino Wio Terminal", "ATSAMD51", ARCH_SAMD, 115200, False, "SAMD51"),
    (0x2886, 0x8003): USBProfile("Seeeduino XIAO RP2040", "RP2040", ARCH_RP2040, 1200, False, "RP2040"),
    (0x2886, 0x8004): USBProfile("Seeeduino Wio Lite (ESP32)", "ESP32", ARCH_ESP32, 115200, False, "ESP32"),
    (0x2886, 0x8007): USBProfile("Seeeduino XIAO ESP32C3", "ESP32-C3", ARCH_ESP32, 115200, False, "ESP32-C3"),
    (0x2886, 0x8008): USBProfile("Seeeduino XIAO ESP32S3", "ESP32-S3", ARCH_ESP32, 115200, False, "ESP32-S3"),
    (0x0403, 0x6001): USBProfile("FT232R (FTDI)", "FT232R", ARCH_AVR, 115200, False, "FT232R"),
    (0x0403, 0x6010): USBProfile("FT2232C/D/H (FTDI)", "FT2232", ARCH_AVR, 115200, False, "FT2232"),
    (0x0403, 0x6011): USBProfile("FT4232H (FTDI)", "FT4232", ARCH_AVR, 115200, False, "FT4232"),
    (0x0403, 0x6014): USBProfile("FT232H (FTDI)", "FT232H", ARCH_AVR, 115200, False, "FT232H"),
    (0x0403, 0x6015): USBProfile("FT231X (FTDI)", "FT231X", ARCH_AVR, 115200, False, "FT231X"),
    (0x0403, 0x601C): USBProfile("FT230X (FTDI)", "FT230X", ARCH_AVR, 115200, False, "FT230X"),
    (0x10C4, 0xEA60): USBProfile("CP2102 (Silicon Labs)", "CP2102", ARCH_AVR, 115200, False, "CP2102"),
    (0x10C4, 0xEA61): USBProfile("CP2101 (Silicon Labs)", "CP2101", ARCH_AVR, 115200, False, "CP2101"),
    (0x10C4, 0xEA62): USBProfile("CP2102N (Silicon Labs)", "CP2102N", ARCH_AVR, 115200, False, "CP2102N"),
    (0x10C4, 0xEA63): USBProfile("CP2105 (Silicon Labs)", "CP2105", ARCH_AVR, 115200, False, "CP2105"),
    (0x10C4, 0xEA70): USBProfile("CP2105 (Silicon Labs alt)", "CP2105", ARCH_AVR, 115200, False, "CP2105"),
    (0x10C4, 0xEA71): USBProfile("CP2108 (Silicon Labs)", "CP2108", ARCH_AVR, 115200, False, "CP2108"),
    (0x10C4, 0xEA80): USBProfile("CP2110 (Silicon Labs)", "CP2110", ARCH_AVR, 115200, False, "CP2110"),
    (0x10C4, 0xEA8B): USBProfile("CP2112 (Silicon Labs)", "CP2112", ARCH_AVR, 115200, False, "CP2112"),
    (0x10C4, 0xEA90): USBProfile("CP2130 (Silicon Labs)", "CP2130", ARCH_AVR, 115200, False, "CP2130"),
    # ---- WCH CH340 / CH341 ----
    (0x1A86, 0x7523): USBProfile("CH340 (WCH)", "CH340", ARCH_AVR, 115200, False, "CH340"),
    (0x1A86, 0x5523): USBProfile("CH340K (WCH)", "CH340K", ARCH_AVR, 115200, False, "CH340K"),
    (0x1A86, 0x5525): USBProfile("CH330 (WCH)", "CH330", ARCH_AVR, 115200, False, "CH330"),
    (0x1A86, 0x341A): USBProfile("CH341A (WCH, EEPROM/FLASH)", "CH341A", ARCH_AVR, 115200, False, "CH341A"),
    (0x1A86, 0x341B): USBProfile("CH341A (WCH, alt)", "CH341A", ARCH_AVR, 115200, False, "CH341A"),
    (0x1A86, 0x341C): USBProfile("CH341A (WCH, alt 2)", "CH341A", ARCH_AVR, 115200, False, "CH341A"),
    (0x1A86, 0x341D): USBProfile("CH341A (WCH, alt 3)", "CH341A", ARCH_AVR, 115200, False, "CH341A"),
    (0x1A86, 0x341E): USBProfile("CH341A (WCH, alt 4)", "CH341A", ARCH_AVR, 115200, False, "CH341A"),
    (0x1A86, 0x341F): USBProfile("CH341A (WCH, alt 5)", "CH341A", ARCH_AVR, 115200, False, "CH341A"),
    (0x1A86, 0x3483): USBProfile("CH343P (WCH, PCIe)", "CH343P", ARCH_AVR, 115200, False, "CH343P"),
    (0x1A86, 0x55D4): USBProfile("CH9102 (WCH, USB-Serial)", "CH9102", ARCH_AVR, 115200, False, "CH9102"),
    (0x1A86, 0x55D5): USBProfile("CH9102 (WCH, alt)", "CH9102", ARCH_AVR, 115200, False, "CH9102"),
    (0x1A86, 0x55D6): USBProfile("CH9102F (WCH)", "CH9102F", ARCH_AVR, 115200, False, "CH9102F"),
    (0x1A86, 0x55D7): USBProfile("CH9102 (WCH, alt 2)", "CH9102", ARCH_AVR, 115200, False, "CH9102"),
    (0x1A86, 0x55D8): USBProfile("CH9102 (WCH, alt 3)", "CH9102", ARCH_AVR, 115200, False, "CH9102"),
    (0x1A86, 0x55D9): USBProfile("CH9102 (WCH, alt 4)", "CH9102", ARCH_AVR, 115200, False, "CH9102"),
    # ---- Prolific PL2303 ----
    (0x067B, 0x2303): USBProfile("PL2303 (Prolific)", "PL2303", ARCH_AVR, 115200, False, "PL2303"),
    (0x067B, 0x04BB): USBProfile("PL2303TA (Prolific)", "PL2303TA", ARCH_AVR, 115200, False, "PL2303TA"),
    (0x067B, 0x04CC): USBProfile("PL2303SA (Prolific)", "PL2303SA", ARCH_AVR, 115200, False, "PL2303SA"),
    (0x067B, 0x04DD): USBProfile("PL2303HXA (Prolific)", "PL2303HXA", ARCH_AVR, 115200, False, "PL2303HXA"),
    (0x067B, 0xAAA0): USBProfile("PL2303GC (Prolific)", "PL2303GC", ARCH_AVR, 115200, False, "PL2303GC"),
    (0x067B, 0xAAA1): USBProfile("PL2303GB (Prolific)", "PL2303GB", ARCH_AVR, 115200, False, "PL2303GB"),
    (0x067B, 0xAAA2): USBProfile("PL2303GA (Prolific)", "PL2303GA", ARCH_AVR, 115200, False, "PL2303GA"),
    (0x067B, 0xAAA3): USBProfile("PL2303GB-A (Prolific)", "PL2303GB-A", ARCH_AVR, 115200, False, "PL2303GB-A"),
    (0x067B, 0xAAA4): USBProfile("PL2303GC-A (Prolific)", "PL2303GC-A", ARCH_AVR, 115200, False, "PL2303GC-A"),
    (0x067B, 0xAAA5): USBProfile("PL2303GK (Prolific)", "PL2303GK", ARCH_AVR, 115200, False, "PL2303GK"),
    (0x067B, 0xAAA6): USBProfile("PL2303GQ (Prolific)", "PL2303GQ", ARCH_AVR, 115200, False, "PL2303GQ"),
    (0x067B, 0xAAA7): USBProfile("PL2303GS (Prolific)", "PL2303GS", ARCH_AVR, 115200, False, "PL2303GS"),
    (0x067B, 0xAAA8): USBProfile("PL2303GT (Prolific)", "PL2303GT", ARCH_AVR, 115200, False, "PL2303GT"),
    (0x067B, 0xAAA9): USBProfile("PL2303GL (Prolific)", "PL2303GL", ARCH_AVR, 115200, False, "PL2303GL"),
    (0x067B, 0xAAAA): USBProfile("PL2303GE (Prolific)", "PL2303GE", ARCH_AVR, 115200, False, "PL2303GE"),
    (0x067B, 0xAAAB): USBProfile("PL2303GF (Prolific)", "PL2303GF", ARCH_AVR, 115200, False, "PL2303GF"),
    (0x067B, 0xAAAC): USBProfile("PL2303GI (Prolific)", "PL2303GI", ARCH_AVR, 115200, False, "PL2303GI"),
    (0x067B, 0xAAAD): USBProfile("PL2303EJ (Prolific)", "PL2303EJ", ARCH_AVR, 115200, False, "PL2303EJ"),
    # ---- Microchip MCP2200 ----
    (0x04D8, 0x00DF): USBProfile("MCP2200 (Microchip)", "MCP2200", ARCH_AVR, 115200, False, "MCP2200"),
    (0x04D8, 0x00DE): USBProfile("MCP2200 (Microchip, alt)", "MCP2200", ARCH_AVR, 115200, False, "MCP2200"),
    # ---- Teensy (PJRC) ----
    (0x16C0, 0x0483): USBProfile("Teensy (PJRC)", "MK20DX256", ARCH_AVR, 115200, False, "MK20DX256"),
    (0x16C0, 0x0484): USBProfile("Teensy 2.0 (PJRC)", "ATmega32U4", ARCH_AVR, 115200, False, "ATmega32U4"),
    (0x16C0, 0x0485): USBProfile("Teensy++ 2.0 (PJRC)", "AT90USB1286", ARCH_AVR, 115200, False, "AT90USB1286"),
    (0x16C0, 0x0477): USBProfile("Teensy 3.5 (PJRC)", "MK64FX512", ARCH_AVR, 115200, False, "MK64FX512"),
    (0x16C0, 0x0478): USBProfile("Teensy 3.6 (PJRC)", "MK66FX1M0", ARCH_AVR, 115200, False, "MK66FX1M0"),
    (0x16C0, 0x0476): USBProfile("Teensy LC (PJRC)", "MKL26Z64", ARCH_AVR, 115200, False, "MKL26Z64"),
    (0x16C0, 0x0475): USBProfile("Teensy 4.0/4.1 (PJRC)", "IMXRT1062", ARCH_AVR, 115200, False, "IMXRT1062"),
    (0x16C0, 0x0486): USBProfile("Teensy 3.1/3.2 (PJRC)", "MK20DX128", ARCH_AVR, 115200, False, "MK20DX128"),
    # ---- ESP32 / ESP8266 nativos (SIN convertidor externo) ----
    (0x303A, 0x4001): USBProfile("ESP32 (Espressif, nativo)", "ESP32", ARCH_ESP32, 115200, False, "ESP32"),
    (0x303A, 0x4002): USBProfile("ESP32-S2 (Espressif, nativo)", "ESP32-S2", ARCH_ESP32, 115200, False, "ESP32-S2"),
    (0x303A, 0x4003): USBProfile("ESP32-S3 (Espressif, nativo)", "ESP32-S3", ARCH_ESP32, 115200, False, "ESP32-S3"),
    (0x303A, 0x4004): USBProfile("ESP32-C3 (Espressif, nativo)", "ESP32-C3", ARCH_ESP32, 115200, False, "ESP32-C3"),
    (0x303A, 0x4005): USBProfile("ESP32-C6 (Espressif, nativo)", "ESP32-C6", ARCH_ESP32, 115200, False, "ESP32-C6"),
    (0x303A, 0x4007): USBProfile("ESP32-H2 (Espressif, nativo)", "ESP32-H2", ARCH_ESP32, 115200, False, "ESP32-H2"),
    (0x303A, 0x1001): USBProfile("ESP32-S2 (Espressif, bootloader)", "ESP32-S2", ARCH_ESP32, 115200, False, "ESP32-S2"),
    # ---- Wemos / Lolin / NodeMCU (ESP8266/ESP32 clones) ----
    (0x0403, 0x6014): USBProfile("Wemos D1 Mini (ESP8266)", "ESP8266", ARCH_ESP8266, 115200, False, "ESP8266"),
    (0x1A86, 0x55D4): USBProfile("Lolin ESP32 (CH9102)", "ESP32", ARCH_ESP32, 115200, False, "ESP32"),
    (0x1A86, 0x55D7): USBProfile("NodeMCU V2/V3 (CH340)", "ESP8266", ARCH_ESP8266, 115200, False, "ESP8266"),
    (0x1A86, 0x55D9): USBProfile("Wemos D1 Mini ESP32 (CH340)", "ESP32", ARCH_ESP32, 115200, False, "ESP32"),
    (0x10C4, 0xEA60): USBProfile("NodeMCU (CP2102)", "ESP8266", ARCH_ESP8266, 115200, False, "ESP8266"),
    # ---- RobotDyn ----
    (0x2F0C, 0x0050): USBProfile("RobotDyn SAMD21 Mini", "ATSAMD21G18", ARCH_SAMD, 115200, False, "SAMD21"),
    (0x2F0C, 0x0051): USBProfile("RobotDyn Mega 2560 (CH340)", "ATmega2560", ARCH_AVR, 115200, False, "ATmega2560"),
    # ---- Pololu ----
    (0x1FFB, 0x00B1): USBProfile("Pololu A-Star 32U4", "ATmega32U4", ARCH_AVR, 115200, False, "ATmega32U4"),
    # ---- Digistump ----
    (0x16D0, 0x0753): USBProfile("Digispark (ATtiny85)", "ATtiny85", ARCH_AVR, 115200, False, "ATtiny85"),
    # ---- SparkFun ----
    (0x1B4F, 0x9203): USBProfile("RedBoard (SparkFun, CH340)", "ATmega328P", ARCH_AVR, 115200, False, "ATmega328P"),
    (0x1B4F, 0x9214): USBProfile("RedBoard Turbo (SAMD)", "ATSAMD21G18", ARCH_SAMD, 115200, False, "SAMD21"),
    (0x1B4F, 0x9215): USBProfile("RedBoard Qwiic (SAMD)", "ATSAMD21G18", ARCH_SAMD, 115200, False, "SAMD21"),
    (0x1B4F, 0x9219): USBProfile("ESP32 Thing (SparkFun)", "ESP32", ARCH_ESP32, 115200, False, "ESP32"),
    # ---- dfrobot ----
    (0x0483, 0x5740): USBProfile("DFRobot Bluno (ATmega32U4)", "ATmega32U4", ARCH_AVR, 115200, False, "ATmega32U4"),
    (0x0483, 0xFFFD): USBProfile("DFRobot Bluno Mega (ATmega2560)", "ATmega2560", ARCH_AVR, 115200, False, "ATmega2560"),
    (0x0471, 0x0F03): USBProfile("DFRobot Beetle (ATmega32U4)", "ATmega32U4", ARCH_AVR, 115200, False, "ATmega32U4"),
    (0x0471, 0x0F04): USBProfile("DFRobot Beetle (D21)", "ATSAMD21G18", ARCH_SAMD, 115200, False, "SAMD21"),
    # ---- Makerfabs ----
    (0x26BA, 0x0001): USBProfile("Makerfabs ESP32 (CP2104)", "ESP32", ARCH_ESP32, 115200, False, "ESP32"),
    # ---- LilyGo ----
    (0x303A, 0x4001): USBProfile("LilyGo T-Display (ESP32)", "ESP32", ARCH_ESP32, 115200, False, "ESP32"),
    (0x1A86, 0x55D4): USBProfile("LilyGo T-Display S3 (CH9102)", "ESP32-S3", ARCH_ESP32, 115200, False, "ESP32-S3"),
    # ---- M5Stack ----
    (0x0403, 0x6010): USBProfile("M5Stack Core (ESP32)", "ESP32", ARCH_ESP32, 115200, False, "ESP32"),
    # ---- Generic USB CDC (fallback) ----
    (0x0000, 0x0000): USBProfile("USB Serial (genérico)", "desconocido", ARCH_UNKNOWN, 115200, False, "desconocido"),
}


def lookup(vid: int, pid: int) -> Optional[USBProfile]:
    """Busca un VID/PID en la base de datos. Devuelve None si no existe."""
    return USB_DATABASE.get((vid, pid))


def lookup_by_vid(vid: int) -> list:
    """Devuelve todos los perfiles que comparten el mismo VID."""
    return [v for (v_id, _), v in USB_DATABASE.items() if v_id == vid]


# =============================================================================
# HEURISTICA: cuando VID/PID no se encuentra
# =============================================================================
USB_DESC_PATTERNS: list = [
    # (regex_o_substring_buscado, perfil_default)
    # -- Arduino/SparkFun/Adafruit --
    ("Arduino", "Arduino (detectable por firmware)"),
    ("arduino", "Arduino (detectable por firmware)"),
    ("SparkFun", "Arduino-compatible SparkFun"),
    ("Sparkfun", "Arduino-compatible SparkFun"),
    ("Adafruit", "Arduino-compatible Adafruit"),
    # -- ESP8266 --
    ("NodeMCU", "ESP8266 (NodeMCU)"),
    ("nodemcu", "ESP8266 (NodeMCU)"),
    ("ESP-12E", "ESP8266"),
    ("ESP-12F", "ESP8266"),
    ("Wemos", "ESP8266 (Wemos D1)"),
    ("Lolin", "ESP8266/ESP32 (Lolin)"),
    ("D1 Mini", "ESP8266 (D1 Mini)"),
    # -- ESP32 --
    ("ESP32", "ESP32"),
    ("ESP32-S2", "ESP32-S2"),
    ("ESP32-S3", "ESP32-S3"),
    ("ESP32-C3", "ESP32-C3"),
    ("ESP32-C6", "ESP32-C6"),
    ("ESP32-H2", "ESP32-H2"),
    ("M5Stack", "ESP32 (M5Stack)"),
    ("M5StackCore", "ESP32 (M5Stack)"),
    ("T-Display", "ESP32 (T-Display)"),
    # -- SAMD21/51 --
    ("ATSAMD21", "ATSAMD21 (Arduino Zero/MKR/Nano 33)"),
    ("ATSAMD51", "ATSAMD51 (Arduino MKR Vidor)"),
    ("SAM D", "ATSAMD (Arduino MKR/Zero/Nano 33)"),
    ("SAMD21", "ATSAMD21"),
    ("SAMD51", "ATSAMD51"),
    # -- RP2040 --
    ("RP2040", "RP2040 (Raspberry Pi Pico/Nano Connect)"),
    ("Pico", "RP2040 (Raspberry Pi Pico)"),
    ("Nano RP2040", "RP2040 (Arduino Nano RP2040 Connect)"),
    # -- nRF52 --
    ("nRF52840", "nRF52840 (Arduino Nano 33 BLE)"),
    ("nRF52832", "nRF52832"),
    ("BLE Sense", "nRF52840 (Nano 33 BLE Sense)"),
    # -- STM32 --
    ("STM32F4", "STM32F4 (STM32 Arduino)"),
    ("STM32H7", "STM32H7 (Portenta H7)"),
    ("STM32F1", "STM32F1 (STM32 Arduino)"),
    ("STM32", "STM32"),
    # -- Teensy --
    ("Teensy", "Teensy (PJRC)"),
    ("MK20DX", "Teensy 3.x"),
    ("MK64FX", "Teensy 3.5"),
    ("MK66FX", "Teensy 3.6"),
    ("MKL26", "Teensy LC"),
    ("IMXRT106", "Teensy 4.x"),
    # -- AVR genérico --
    ("ATmega328P", "ATmega328P (Arduino Uno/Nano)"),
    ("ATmega2560", "ATmega2560 (Arduino Mega)"),
    ("ATmega32U4", "ATmega32U4 (Arduino Leonardo/Micro)"),
    ("ATtiny85", "ATtiny85 (Digispark/Gemma)"),
    ("ATmega4809", "ATmega4809 (Arduino Nano Every)"),
    # -- FTDI --
    ("FTDI", "FTDI USB-Serial"),
    ("FT232", "FT232R/FT231X"),
    # -- CH340/CH341 --
    ("CH340", "CH340 USB-Serial (clon chino)"),
    ("CH341", "CH341 USB-Serial (clon chino)"),
    # -- CP210x --
    ("CP210", "CP210x USB-Serial"),
    ("Silicon Labs", "CP210x USB-Serial"),
    # -- PL2303 --
    ("PL2303", "PL2303 USB-Serial"),
    ("Prolific", "PL2303 USB-Serial"),
    # -- MCP2200 --
    ("MCP2200", "MCP2200 USB-Serial"),
    ("Microchip", "MCP2200 USB-Serial"),
    # -- Seeed --
    ("Seeeduino", "Seeeduino (Arduino-compatibles)"),
    ("Seeed", "Seeeduino / Seeed Studio"),
    # -- RobotDyn --
    ("RobotDyn", "RobotDyn (Arduino-compatibles)"),
    # -- Generic Serial --
    ("USB Serial", "USB Serial genérico"),
    ("USB Device", "USB genérico"),
    ("COM", "Puerto COM (Windows)"),
]


def guess_by_description(description: str) -> Optional[str]:
    """Intenta adivinar el tipo de placa a partir de la descripción USB."""
    if not description:
        return None
    desc_upper = description.upper()
    for pattern, name in USB_DESC_PATTERNS:
        if pattern.upper() in desc_upper:
            return name
    return None

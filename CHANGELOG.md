# 📋 Changelog - Arduino Diagnostic Suite

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato esta basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).
Este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [2.0.0] - 2026-07-11

### Agregado
- **Módulo de reparación automático** (`core/repair.py`): Quema bootloader, configura fuses, verifica reparación
- **Comando CLI `repair`**: `python main.py repair --port COM9`
- **Tests del módulo de reparación** (`tests/test_repair.py`): 7 tests unitarios

## [1.0.0] - 2026-07-11

### Agregado
- **Deteccion universal de placas**: Base de datos de 100+ VID/PID para convertidores USB-Serial.
- **Soporte para clones chinos**: CH340, CH340K, CH341A, CH9102, CH343P.
- **Soporte para PL2303**: Todas las variantes (TA, SA, HXA, GC, GB, GA, GK, GQ, GS, GT, GL, GE, GF, GI, EJ).
- **Soporte para CP210x**: CP2101, CP2102, CP2102N, CP2105, CP2108, CP2110, CP2112, CP2130.
- **Soporte para FTDI**: FT232R, FT2232, FT4232, FT232H, FT231X, FT230X.
- **Soporte para Teensy**: Todas las versiones (2.0 a 4.1).
- **Soporte para ESP32 nativo**: ESP32, ESP32-S2/S3/C3/C6/H2.
- **Soporte para ESP8266**: NodeMCU, Wemos D1 Mini, ESP-12E/F.
- **Soporte para RP2040**: Raspberry Pi Pico, Pico W, Arduino Nano RP2040 Connect.
- **Soporte para SAMD**: Arduino Zero, MKR1000, MKR WiFi 1010, Nano 33 IoT.
- **Soporte para nRF52**: Arduino Nano 33 BLE, Nano 33 BLE Sense.
- **Soporte para Adafruit**: Feather M0/M4, ItsyBitsy, Metro M4, Trinket, QT Py RP2040.
- **Soporte para Seeed**: Seeeduino XIAO (SAMD/RP2040/ESP32), Wio Terminal.
- **Soporte para SparkFun**: RedBoard, ESP32 Thing, Pro Micro.
- **Soporte para RobotDyn**: SAMD21 Mini, Mega 2560.
- **Soporte para dfrobot**: Bluno, Beetle.
- **Firmas AVR expandidas**: 60+ chips incluyendo ATmega168/88/8A/4809/4808/16U4/32U4/32U2, ATtiny (85, 84, 2313, 4313, 25, 45, 261).
- **Firmas SAMD**: ATSAMD21G18/E18/J18, ATSAMD51J19/J20/N20/P20.
- **Firmas nRF52**: nRF52832, nRF52840.
- **Firmas Teensy**: MK20DX128/256, MK64FX512, MK66FX1M0, IMXRT1062.
- **Heuristica por descripcion USB**: 50+ patrones para identificar placas sin VID/PID conocido.
- **Detector mejorado**: Campo `arch` en DetectedBoard (avr/samd/rp2040/esp32/esp8266/stm32/nrf52).
- **Sketches de diagnostico**: AVR (Uno/Mega/Nano/Leonardo), SAMD (Zero/MKR/Nano33IoT), RP2040 (Pico/NanoRP2040), ESP32 (todas variantes), ESP8266 (NodeMCU/Wemos).
- **GUI con deteccion de arquitectura**: Muestra la arquitectura detectada en la interfaz.
- **README actualizado**: Tabla completa de 20+ familias soportadas.

### Cambiado
- `detector.py` ahora usa `usb_ident.py` y `board_heuristic.py` para detección universal.
- `board_info.py` expandido de 9 a 60+ firmas AVR/SAMD/nRF52.
- `core/__init__.py` exporta todos los nuevos módulos y constantes de arquitectura.

### Fijo
- Codigo duplicado al final de `board_info.py`.

[1.0.0]: https://github.com/KherCent/arduino-diagnostic/releases/tag/v1.0.0

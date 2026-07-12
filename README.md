# 🔧 ArduCheck

**Universal diagnostic tool for Arduino and compatible boards.**  
Detects, identifies, and verifies the functional status of boards across all families.

[![Download ArduCheck](https://img.shields.io/badge/Download-ArduCheck.exe-brightgreen?style=for-the-badge)](https://github.com/KherCent/ArduCheck/releases/latest/download/ArduCheck.exe)
[![Release](https://img.shields.io/github/v/release/KherCent/ArduCheck?style=flat)](https://github.com/KherCent/ArduCheck/releases)
[![Stars](https://img.shields.io/github/stars/KherCent/ArduCheck?style=flat)](https://github.com/KherCent/ArduCheck/stargazers)

**Español** | [English Version](README.md) *(You are here)* | [Leer en Español](README.es.md)

---

## ✅ Supported Architectures

| Family | Boards | Architecture | Microcontroller |
|---|---|---|---|
| **Official Arduino** | Uno, Mega 2560, Nano, Leonardo, Micro, Pro Mini, LilyPad | AVR | ATmega328P/2560/32U4 |
| **Modern Arduino** | Zero, MKR1000, MKR WiFi 1010, Nano 33 IoT | SAMD | ATSAMD21G18 |
| **Arduino BLE** | Nano 33 BLE, Nano 33 BLE Sense | nRF52 | nRF52840 |
| **Arduino RP2040** | Nano RP2040 Connect | RP2040 | RP2040 |
| **Arduino ESP32** | Nano ESP32 | ESP32 | ESP32-S3 |
| **Arduino STM32** | Portenta H7, Giga | STM32 | STM32H747 |
| **Chinese Clones** | CH340, CH340G, CH340K, CH341A, CH9102 | AVR | ATmega |
| **FTDI** | FT232R, FT231X, FT230X | AVR | - |
| **Silicon Labs** | CP2102, CP2102N, CP2105, CP2108 | AVR | - |
| **Prolific** | PL2303 (all variants) | AVR | - |
| **Microchip** | MCP2200 | AVR | - |
| **ESP8266** | NodeMCU, Wemos D1 Mini, ESP-12E/F | ESP8266 | Xtensa LX106 |
| **ESP32 Clones** | M5Stack, LilyGo T-Display, ESP32-S2/S3/C3/C6/H2 | ESP32 | Tensilica/RISC-V |
| **Teensy** | Teensy 2.0 to 4.1 (all) | ARM | MK20/IMXRT |
| **Adafruit** | Feather M0/M4, ItsyBitsy, Metro M4, Trinket, QT Py | SAMD/RP2040 | ATSAMD / RP2040 |
| **SparkFun** | RedBoard, ESP32 Thing, Pro Micro | AVR/ESP32 | ATmega/ESP32 |
| **Seeed** | Seeeduino XIAO, Wio Terminal | SAMD/RP2040/ESP32 | ATSAMD / RP2040 |
| **RobotDyn** | SAMD21 Mini, Mega 2560 | SAMD/AVR | ATSAMD21 / ATmega2560 |
| **dfrobot** | Bluno, Beetle | AVR/SAMD | ATmega32U4 / ATSAMD21 |
| **Raspberry Pi** | Pico, Pico W | RP2040 | RP2040 |
| **Generic STM32** | BluePill, STM32F4, STM32F7 | STM32 | STM32F103/405/746 |

> **100+ VID/PID** known and USB description heuristics for unknown clones.

---

## 🎯 What it does

1. **Automatically detects** any board connected via USB (COM ports).
2. **Identifies** the board: VID/PID + USB description + chip signature.
3. **Reads** information: manufacturer, serial number, bootloader baudrate.
4. **Detects architecture** (AVR / SAMD / RP2040 / ESP32 / ESP8266 / STM32 / nRF52).
5. **Uploads** an architecture-specific self-test sketch (via `arduino-cli`).
6. **Runs** functional tests: LED, digital/analog pins, ADC, PWM, EEPROM, I2C, SPI, memory.
7. **Reports** verdict: ✅ GOOD / ⚠️ WARNING / ❌ BAD.
8. **Repairs** automatically: corrupt bootloader, misconfigured fuses, missing drivers.

---

## 🔧 Automatic Repair

```bash
# Repair the bootloader of a board
python main.py repair --port COM9

# If diagnostics fail with "not in sync" or "resp=0x00":
# → Automatically burns Optiboot (Uno) or stk500v2 (Mega)
# → Sets fuses correctly
# → Verifies the repair
```

**Automatically repairable issues:**
| Issue | Solution |
|---|---|
| Corrupt Bootloader | Burn bootloader using avrdude |
| Incorrect Fuses | Restore factory values |
| Port not responding | Retry at alternative baudrates |
| Missing CH340 Driver | Installation instructions |

---

## 📦 Installation

```cmd
cd arduino-diagnostic
pip install -r requirements.txt
```

For full self-test (automatically upload sketch):
```cmd
winget install ArduinoSA.CLI
```
or download from: https://arduino.github.io/arduino-cli/latest/installation/

---

## 🚀 Quick Start

### Interactive Menu
```cmd
run.bat
```

### Direct CLI
```cmd
python main.py scan                     :: list detected boards with architecture
python main.py diagnose --port COM3     :: full diagnostic
python main.py watch                    :: real-time hot-plug monitor
python main.py install                  :: verify tools
```

### GUI
```cmd
run_gui.bat
```

---

## 🏗️ Project Structure

```
arduino-diagnostic/
├── firmware/               # Self-test sketches by architecture
│   ├── avr/                # ATmega328P/2560 (Uno, Mega, Nano, Leonardo)
│   ├── samd/              # ATSAMD21 (Zero, MKR, Nano 33 IoT)
│   ├── rp2040/            # RP2040 (Pico, Nano RP2040 Connect)
│   ├── esp32/             # ESP32 (all variants)
│   └── esp8266/           # ESP8266 (NodeMCU, Wemos D1 Mini)
├── core/                  # Python Logic
│   ├── detector.py         # Port scan + VID/PID identification
│   ├── board_info.py      # AVR/SAMD/nRF52 signatures (60+ chips)
│   ├── usb_ident.py        # 100+ VID/PID database
│   ├── board_heuristic.py  # USB description identification
│   ├── parser.py           # Sketch results parser
│   ├── runner.py           # Diagnostic coordinator
│   ├── flasher.py          # Upload via arduino-cli
│   └── watcher.py          # USB hot-plug monitor
├── gui/
│   └── app.py              # Tkinter GUI with auto-refresh
├── tests/
│   └── test_smoke.py       # Automated tests
├── docs/
├── main.py                 # CLI + interactive menu
├── run.bat                 # Console launcher
├── run_gui.bat             # GUI launcher
├── requirements.txt
└── README.md
```

---

## 🧪 Diagnostic Plan

### PHASE 1 — Detection (without uploading anything)
1. Scan active COM ports.
2. Extract VID/PID from HWID.
3. Search in `usb_ident.py` database (100+ VID/PID).
4. If not found, use `board_heuristic.py` (USB description).
5. Infer architecture (AVR / SAMD / RP2040 / ESP32 / ESP8266 / STM32 / nRF52).

### PHASE 2 — Chip Identification
6. If AVR: read signature via avrdude (60+ known signatures).
7. If SAMD: query USB descriptor.
8. If ESP32/ESP8266: read chip ID via Serial.

### PHASE 3 — Self-test (requires uploading sketch)
9. Select sketch based on detected architecture.
10. Upload via arduino-cli (or esptool for ESP).
11. Run functional tests.
12. Collect results over Serial.

### PHASE 4 — Verdict
- ✅ **GOOD**: passes all critical tests.
- ⚠️ **WARNING**: passes critical, fails on specific pins or low voltage.
- ❌ **BAD**: fails signature, communication, bootloader or memory.

---

## 📋 Verdict Criteria

| Test | If fails → |
|---|---|
| Chip signature not recognized (AVR) | ❌ BAD |
| No response on Serial | ❌ BAD |
| Corrupted bootloader | ❌ BAD |
| Pin 13 LED does not turn on | ⚠️ WARNING |
| Digital pin burnt | ⚠️ WARNING |
| ADC gives erratic values | ⚠️ WARNING |
| EEPROM fails (AVR) | ❌ BAD |
| Voltage < 4.5V | ⚠️ WARNING |
| Heap/free memory too low | ⚠️ WARNING |
| I2C no response (no peripherals) | ✅ OK |

---

## 🛠️ Troubleshooting

- **"COM Port not found"**: install driver depending on your converter:
  - CH340/CH341: https://www.wch.cn/downloads/CH341SER_ZIP.html
  - FTDI: https://ftdichip.com/drivers/
  - CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- **"Programmer is not responding"**: missing bootloader or faulty USB cable.
- **Permission denied (Linux/macOS)**: `sudo usermod -a -G dialout $USER` and reconnect.
- **avrdude not found**: install `arduino-cli` and make sure it is in your PATH.

---

## 📚 References

- [pyserial](https://pyserial.readthedocs.io)
- [pyusb](https://github.com/pyusb/pyusb)
- [arduino-cli](https://arduino.github.io/arduino-cli/)
- [avrdude](https://www.nongnu.org/avrdude/)
- [esptool.py](https://github.com/espressif/esptool)
- [bossac (SAMD)](https://github.com/shumatech/BOSSA)
- [USB-IF VID List](https://www.usb.org/developers)

---

## 🧭 Roadmap

- [x] Universal VID/PID database (100+ entries)
- [x] Expanded AVR/SAMD/nRF52 signatures (60+ chips)
- [x] USB description heuristics
- [x] Sketches per architecture (AVR, SAMD, RP2040, ESP32, ESP8266)
- [x] Improved detector with detected architecture
- [ ] Improved flasher (bossac, esptool, picotool by architecture)
- [ ] Smoke tests for new databases
- [ ] nRF52 support (Nano 33 BLE) - diagnostic sketch
- [ ] STM32 support (Portenta) - diagnostic sketch

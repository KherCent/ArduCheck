# 🔧 ArduCheck

**Herramienta universal para diagnosticar placas Arduino y compatibles.**  
Detecta, identifica y verifica el estado de funcionamiento de placas de todas las familias.

[English Version](README.md) | **Español**

---

## ✅ Arquitecturas soportadas

| Familia | Placas | Arquitectura | Microcontrolador |
|---|---|---|---|
| **Arduino oficial** | Uno, Mega 2560, Nano, Leonardo, Micro, Pro Mini, LilyPad | AVR | ATmega328P/2560/32U4 |
| **Arduino modernos** | Zero, MKR1000, MKR WiFi 1010, Nano 33 IoT | SAMD | ATSAMD21G18 |
| **Arduino BLE** | Nano 33 BLE, Nano 33 BLE Sense | nRF52 | nRF52840 |
| **Arduino RP2040** | Nano RP2040 Connect | RP2040 | RP2040 |
| **Arduino ESP32** | Nano ESP32 | ESP32 | ESP32-S3 |
| **Arduino STM32** | Portenta H7, Giga | STM32 | STM32H747 |
| **Clones chinos** | CH340, CH340G, CH340K, CH341A, CH9102 | AVR | ATmega |
| **FTDI** | FT232R, FT231X, FT230X | AVR | - |
| **Silicon Labs** | CP2102, CP2102N, CP2105, CP2108 | AVR | - |
| **Prolific** | PL2303 (todas variantes) | AVR | - |
| **Microchip** | MCP2200 | AVR | - |
| **ESP8266** | NodeMCU, Wemos D1 Mini, ESP-12E/F | ESP8266 | Xtensa LX106 |
| **ESP32 clones** | M5Stack, LilyGo T-Display, ESP32-S2/S3/C3/C6/H2 | ESP32 | Tensilica/RISC-V |
| **Teensy** | Teensy 2.0 a 4.1 (todas) | ARM | MK20/IMXRT |
| **Adafruit** | Feather M0/M4, ItsyBitsy, Metro M4, Trinket, QT Py | SAMD/RP2040 | ATSAMD/ RP2040 |
| **SparkFun** | RedBoard, ESP32 Thing, Pro Micro | AVR/ESP32 | ATmega/ESP32 |
| **Seeed** | Seeeduino XIAO, Wio Terminal | SAMD/RP2040/ESP32 | ATSAMD/ RP2040 |
| **RobotDyn** | SAMD21 Mini, Mega 2560 | SAMD/AVR | ATSAMD21/ ATmega2560 |
| **dfrobot** | Bluno, Beetle | AVR/SAMD | ATmega32U4/ATSAMD21 |
| **Raspberry Pi** | Pico, Pico W | RP2040 | RP2040 |
| **STM32 genérico** | BluePill, STM32F4, STM32F7 | STM32 | STM32F103/405/746 |

> **100+ VID/PID** conocidos y heurística por descripción USB para clones desconocidos.

---

## 🎯 ¿Qué hace?

1. **Detecta** automáticamente cualquier placa conectada por USB (puertos COM).
2. **Identifica** la placa: VID/PID + descripción USB + firma del chip.
3. **Lee** información: fabricante, número de serie, baudrate del bootloader.
4. **Detecta la arquitectura** (AVR / SAMD / RP2040 / ESP32 / ESP8266 / STM32 / nRF52).
5. **Carga** un sketch de auto-test específico para la arquitectura (vía `arduino-cli`).
6. **Ejecuta** pruebas funcionales: LED, pines digitales/analógicos, ADC, PWM, EEPROM, I2C, SPI, memoria.
7. **Reporta** veredicto: ✅ BUENO / ⚠️ ADVERTENCIA / ❌ MALO.
8. **Repara** automáticamente: bootloader corrupto, fuses mal configurados, drivers faltantes.

---

## 🔧 Reparación Automática

```bash
# Reparar bootloader de una placa
python main.py repair --port COM9

# Si el diagnóstico falla con "not in sync" o "resp=0x00":
# → Quema automáticamente Optiboot (Uno) o stk500v2 (Mega)
# → Configura los fuses correctamente
# → Verifica la reparación
```

**Fallas reparables automáticamente:**
| Problema | Solución |
|---|---|
| Bootloader corrupto | Quemar bootloader con avrdude |
| Fuses mal seteados | Restaurar valores de fábrica |
| Puerto no responde | Reintentar a baudrates alternativos |
| Driver CH340 faltante | Instrucciones de instalación |

---

## 📦 Instalación

```cmd
cd arduino-diagnostic
pip install -r requirements.txt
```

Para auto-test completo (subir sketch automáticamente):
```cmd
winget install ArduinoSA.CLI
```
o descarga desde: https://arduino.github.io/arduino-cli/latest/installation/

---

## 🚀 Uso rápido

### Menú interactivo
```cmd
run.bat
```

### CLI directa
```cmd
python main.py scan                     :: lista placas detectadas con arquitectura
python main.py diagnose --port COM3     :: diagnostico completo
python main.py watch                    :: monitor hot-plug en tiempo real
python main.py install                  :: verificar herramientas
```

### GUI
```cmd
run_gui.bat
```

---

## 🏗️ Estructura del proyecto

```
arduino-diagnostic/
├── firmware/               # Sketches de auto-test por arquitectura
│   ├── diagnostic_sketch/  # ATmega328P/2560 (Uno, Mega, Nano, Leonardo)
│   ├── samd/               # ATSAMD21 (Zero, MKR, Nano 33 IoT)
│   ├── rp2040/             # RP2040 (Pico, Nano RP2040 Connect)
│   ├── esp32/              # ESP32 (todas las variantes)
│   ├── esp8266/            # ESP8266 (NodeMCU, Wemos D1 Mini)
│   ├── nrf52/              # nRF52840 (Nano 33 BLE)
│   └── stm32/              # STM32 (Portenta, BluePill)
├── core/                   # Lógica Python
│   ├── __init__.py          # Exports públicos del paquete
│   ├── detector.py          # Escaneo de puertos + identificación VID/PID
│   ├── board_info.py        # Firmas AVR/SAMD/nRF52 (60+ chips)
│   ├── usb_ident.py         # Base de datos de 100+ VID/PID
│   ├── board_heuristic.py   # Identificación por descripción USB
│   ├── parser.py            # Parseo de resultados del sketch
│   ├── runner.py            # Coordinador del diagnóstico
│   ├── flasher.py           # Upload vía arduino-cli
│   ├── repair.py            # Reparación automática de bootloader
│   ├── bootloader_check.py  # Verificación de bootloader
│   ├── exporter.py          # Exportación de reportes
│   ├── platform_utils.py    # Utilidades multiplataforma
│   └── watcher.py           # Monitor hot-plug USB
├── gui/                    # Interfaz gráfica
│   ├── app.py               # GUI principal (v1)
│   ├── app_v2.py            # GUI mejorada (v2)
│   ├── tabs/                # Pestañas de la GUI
│   │   ├── tab_diagnostico.py
│   │   └── tab_reparar.py
│   ├── theme/               # Temas visuales
│   └── widgets/             # Widgets personalizados
├── tests/                  # Tests automatizados
│   ├── test_smoke.py        # Tests de humo generales
│   ├── test_repair.py       # Tests del módulo repair
│   └── test_watcher.py      # Tests del watcher
├── docs/
├── main.py                 # CLI + menú interactivo
├── run.bat                 # Launcher consola (Windows)
├── run.sh                  # Launcher consola (Linux/macOS)
├── run_gui.bat             # Launcher GUI (Windows)
├── run_gui.sh              # Launcher GUI (Linux/macOS)
├── requirements.txt
├── pyproject.toml          # Configuración del paquete Python
└── README.md
```

---

## 🧪 Plan de diagnóstico

### FASE 1 — Detección (sin cargar nada)
1. Escanear puertos COM activos.
2. Extraer VID/PID del HWID.
3. Buscar en base de datos `usb_ident.py` (100+ VID/PID).
4. Si no se encuentra, usar heurística `board_heuristic.py` (descripción USB).
5. Inferir arquitectura (AVR / SAMD / RP2040 / ESP32 / ESP8266 / STM32 / nRF52).

### FASE 2 — Identificación del chip
6. Si AVR: leer firma vía avrdude (60+ firmas conocidas).
7. Si SAMD: consultar descriptor USB.
8. Si ESP32/ESP8266: leer chip ID vía Serial.

### FASE 3 — Auto-test (requiere cargar sketch)
9. Seleccionar sketch según arquitectura detectada.
10. Subir vía arduino-cli (o esptool para ESP).
11. Ejecutar tests funcionales.
12. Recoger resultados por Serial.

### FASE 4 — Veredicto
- ✅ **BUENO**: pasa todas las pruebas críticas.
- ⚠️ **ADVERTENCIA**: pasa críticas, falla en pines específicos o voltaje bajo.
- ❌ **MALO**: falla en firma, comunicación, bootloader o memoria.

---

## 📋 Criterios de veredicto

| Test | Si falla → |
|---|---|
| Firma del chip no reconocida (AVR) | ❌ MALO |
| No responde en Serial | ❌ MALO |
| Bootloader corrupto | ❌ MALO |
| LED pin 13 no enciende | ⚠️ ADVERTENCIA |
| Algún pin digital quemado | ⚠️ ADVERTENCIA |
| ADC da valores erráticos | ⚠️ ADVERTENCIA |
| EEPROM falla (AVR) | ❌ MALO |
| Voltaje < 4.5V | ⚠️ ADVERTENCIA |
| Heap/free memory muy bajo | ⚠️ ADVERTENCIA |
| I2C sin respuesta (sin periféricos) | ✅ OK |

---

## 🛠️ Solución de problemas

- **"Puerto COM no encontrado"**: instala el driver según tu convertidor:
  - CH340/CH341: https://www.wch.cn/downloads/CH341SER_ZIP.html
  - FTDI: https://ftdichip.com/drivers/
  - CP210x: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers
- **"Programmer is not responding"**: bootloader ausente o cable USB defectuoso.
- **Permission denied (Linux/macOS)**: `sudo usermod -a -G dialout $USER` y reconectar.
- **avrdude no encontrado**: instala `arduino-cli` y asegúrate de que esté en el PATH.

---

## 📚 Referencias

- [pyserial](https://pyserial.readthedocs.io)
- [pyusb](https://github.com/pyusb/pyusb)
- [arduino-cli](https://arduino.github.io/arduino-cli/)
- [avrdude](https://www.nongnu.org/avrdude/)
- [esptool.py](https://github.com/espressif/esptool)
- [bossac (SAMD)](https://github.com/shumatech/BOSSA)
- [USB-IF VID List](https://www.usb.org/developers)

---

## 🧭 Roadmap

- [x] Base de datos VID/PID universal (100+ entradas)
- [x] Firmas AVR/SAMD/nRF52 expandidas (60+ chips)
- [x] Heurística por descripción USB
- [x] Sketches por arquitectura (AVR, SAMD, RP2040, ESP32, ESP8266, nRF52, STM32)
- [x] Detector mejorado con arquitectura detectada
- [x] Módulo de reparación automática de bootloader (`repair.py`)
- [ ] Flasher mejorado (bossac, esptool, picotool por arquitectura)
- [ ] Tests de smoke extendidos para bases de datos VID/PID y firmas
- [x] Soporte para nRF52 (Nano 33 BLE) - sketch de diagnóstico
- [x] Soporte para STM32 (Portenta) - sketch de diagnóstico

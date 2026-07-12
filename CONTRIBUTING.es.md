# 🤝 Guía de Contribución - ArduCheck

¡Gracias por tu interés en contribuir a **ArduCheck**! Este proyecto es de código abierto y está mantenido por **KherCent**. Tu ayuda es fundamental para mejorar el diagnóstico de hardware en todo el ecosistema de Arduino.

Al participar en este proyecto, te comprometes a seguir nuestro [Código de Conducta](CODE_OF_CONDUCT.md).

[English Version](CONTRIBUTING.md) | **Español**

---

## 🗂️ ¿Cómo puedo contribuir?

### 1. Reportar Errores (Bugs)
Si encuentras un error o un comportamiento inesperado:
1. Revisa la lista de [Issues del proyecto](https://github.com/KherCent/ArduCheck/issues) para asegurarte de que no haya sido reportado previamente.
2. Si es nuevo, abre un Issue usando nuestra plantilla de **Bug Report**.
3. Asegúrate de incluir:
   - Sistema operativo (Windows, Linux, macOS).
   - Placa de Arduino exacta y si es original o clon (ej. CH340).
   - Log completo del terminal o captura de la GUI.
   - Pasos detallados para reproducir el error.

### 2. Proponer Nuevas Funciones o Arquitecturas
Queremos diagnosticar tantas placas como sea posible. Si deseas proponer soporte para una nueva placa, chip o arquitectura:
1. Abre un Issue usando la plantilla **Feature Request**.
2. Explica qué placas se beneficiarían y, si es posible, proporciona los IDs de USB (`VID:PID`) y la firma del chip.

### 3. Contribuir con Código (Pull Requests)
¡Nos encantan las Pull Requests (PR)! Para contribuir con código, sigue este flujo de trabajo:

1. **Haz un Fork** del repositorio a tu propia cuenta.
2. **Clona** tu fork localmente:
   ```bash
   git clone https://github.com/TU-USUARIO/ArduCheck.git
   cd arduino-diagnostic
   ```
3. **Instala las dependencias**:
   ```bash
   pip install -r requirements.txt
   pip install pytest ruff black mypy  # dev dependencies
   ```
4. **Crea una rama (branch)** descriptiva para tus cambios:
   ```bash
   git checkout -b feature/mi-nueva-funcion
   # o para correcciones
   git checkout -b fix/correccion-de-bug
   ```
5. **Realiza tus cambios** y asegúrate de seguir las pautas de estilo.
6. **Prueba tus cambios**:
   - Ejecuta los tests: `python -m unittest discover tests`
   - Ejecuta linting: `ruff check core/ gui/ main.py`
   - Ejecuta type checking: `mypy core/ gui/ main.py`
   - Si modificaste el firmware, asegúrate de que compila correctamente usando `arduino-cli`.
7. **Haz commit** de tus cambios de forma limpia y clara.
8. **Sube tus cambios** a tu fork y abre una **Pull Request** hacia la rama `main` del repositorio oficial.

---

## 🎨 Pautas de Estilo y Código

### Python (Host CLI & GUI)
- Usamos **Ruff** + **Black** para formateo y linting.
- Type hints son requeridos en todas las funciones y métodos públicos.
- Usa comentarios cuando la lógica sea compleja.
- Mantén la compatibilidad multiplataforma (Windows/Linux/macOS).

### Firmware C/C++ (Sketches en `firmware/`)
- El código del firmware debe ser lo más ligero y eficiente posible.
- Evita el uso de librerías externas que no puedan instalarse fácilmente desde el gestor oficial de librerías de Arduino.
- Estructura la salida Serial de forma consistente para que pueda ser parseada por `core/parser.py`.

---

## 🔧 Guía Técnica: Agregar Nuevo Hardware

### Agregar un nuevo VID:PID USB (reconocimiento de placa)

Agrega el VID:PID a `core/usb_ident.py`:

```python
USB_IDS = [
    # ... entradas existentes ...
    ("0x1234", "0x5678", "Marca", "Nombre Producto", "chinese", "avr"),
]
```

Campos: `VID`, `PID`, `Fabricante`, `Producto`, `Tipo Driver`, `Arquitectura`

**Códigos de arquitectura**: `avr`, `samd`, `rp2040`, `esp32`, `esp8266`, `stm32`, `nrf52`

### Agregar una nueva firma de chip (AVR/SAMD)

Agrega la firma a `core/board_info.py`:

```python
KNOWN_SIGNATURES = {
    # ... entradas existentes ...
    (0x1E, 0x95, 0x14): ("ATmega328P", "avr", 32768, 2048, 1024),
    #            ^bytes de firma^  ^nombre^ ^arch^ ^flash^ ^ram^ ^eeprom^
}
```

La firma es leída por avrdude directamente del chip.

### Agregar heurística por descripción USB (para placas sin VID:PID conocido)

Agrega un patrón regex a `core/board_heuristic.py`:

```python
HEURISTICS = [
    # ... entradas existentes ...
    (re.compile(r"Arduino.*Nano", re.I), "Arduino Nano", "avr", "nano"),
]
```

### Agregar un nuevo sketch de diagnóstico

1. Crea una nueva carpeta en `firmware/` (ej. `firmware/esp32/`)
2. Escribe el sketch siguiendo este protocolo de salida:

```cpp
// Formato de salida de diagnóstico (parseado por core/parser.py)
Serial.println("$ID,<nombre_placa>,<nombre_chip>");
Serial.println("$VCC,<milivoltios>");
Serial.println("$LED,1");        // Test LED: 1=pass, 0=fail
Serial.println("$DIGPIN,<pin>,<0|1>");  // Test pin digital
Serial.println("$ADC,<pin>,<0-1023>");   // Lectura ADC
Serial.println("$DONE,<codigo>"); // 0=OK, 1=WARN, 2=FAIL
```

3. Actualiza `core/flasher.py` para incluir la nueva arquitectura.

### Agregar una nueva herramienta de flasheo (bossac, esptool, picotool)

1. Agrega el buscador de ruta de la herramienta en `core/platform_utils.py`:
```python
def get_bossac_path() -> Optional[str]:
    """Busca el binario bossac para upload SAMD."""
    return find_tool("bossac") or _search_common_paths(...)
```

2. Expórtalo desde `core/__init__.py`.

3. Actualiza `core/flasher.py` para detectar la arquitectura y llamar a la herramienta correcta.

---

## 🧪 Pruebas

Ejecutar todos los tests:
```bash
python -m unittest discover tests
```

Ejecutar con cobertura:
```bash
pytest --cov=core --cov=gui --cov-report=html
```

Ejecutar linting:
```bash
ruff check core/ gui/ main.py
ruff format --check core/ gui/ main.py
```

Ejecutar type checking:
```bash
mypy core/ gui/ main.py
```

### Agregar nuevos tests
- Los tests van en `tests/`
- Nombre: `test_<modulo>.py`
- Clase de test: `Test<NombreModulo>`
- Métodos de test: `test_<descripcion>`
- Usa `unittest.mock.patch` para simular puertos seriales y hardware.

---

## 📦 Compilar el Ejecutable

```bash
pip install pyinstaller
pyinstaller ArduCheck.spec
```

El `.exe` estará en `dist/ArduCheck/`.

---

¿Tienes alguna pregunta? No dudes en abrir un hilo de discusión o contactar al mantenedor del proyecto, **KherCent**. ¡Feliz código!

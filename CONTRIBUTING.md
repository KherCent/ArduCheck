# 🤝 Contributing Guidelines - ArduCheck

Thank you for your interest in contributing to **ArduCheck**! This project is open-source and is maintained by **KherCent**. Your support is essential to improve hardware diagnostics across the entire Arduino ecosystem.

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

**English** | [Leer en Español](CONTRIBUTING.es.md)

---

## 🗂️ How Can I Contribute?

### 1. Reporting Bugs
If you find a bug or unexpected behavior:
1. Search the [Project Issues](https://github.com/KherCent/ArduCheck/issues) to make sure it hasn't been reported yet.
2. If it is new, open a new Issue using our **Bug Report** template.
3. Be sure to include:
   - Operating system (Windows, Linux, macOS).
   - Exact Arduino board model and whether it is original or a clone (e.g., CH340).
   - Full terminal log or GUI screenshot.
   - Detailed steps to reproduce the error.

### 2. Proposing New Features or Architectures
We want to diagnose as many boards as possible. If you want to propose support for a new board, chip, or architecture:
1. Open a new Issue using the **Feature Request** template.
2. Explain which boards would benefit and, if possible, provide the USB IDs (`VID:PID`) and the chip signature.

### 3. Contributing Code (Pull Requests)
We love Pull Requests (PRs)! To contribute code, follow this workflow:

1. **Fork** the repository to your own account.
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ArduCheck.git
   cd arduino-diagnostic
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest ruff black mypy  # dev dependencies
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/my-new-feature
   # or for bug fixes
   git checkout -b fix/bug-fix
   ```
5. **Make your changes** and ensure they follow style guidelines (see below).
6. **Test your changes**:
   - Run automated tests: `python -m unittest discover tests`
   - Run linting: `ruff check core/ gui/ main.py`
   - Run type checking: `mypy core/ gui/ main.py`
   - If you modified the firmware, make sure it compiles correctly using `arduino-cli`.
7. **Commit** your changes cleanly.
8. **Push** your changes to your fork and open a **Pull Request** targeting the `main` branch of the official repository.

---

## 🎨 Code and Style Guidelines

### Python (Host CLI & GUI)
- We use **Ruff** + **Black** for formatting and linting.
- Type hints are required for all public functions and class methods.
- Comment code where logic is complex.
- Maintain cross-platform compatibility (Windows/Linux/macOS).
- All imports go at the top of the file.

### Firmware C/C++ (Sketches in `firmware/`)
- Firmware code should be as lightweight and efficient as possible.
- Avoid using external libraries that cannot be easily installed from the official Arduino Library Manager.
- Structure test outputs consistently so they can be easily parsed by `core/parser.py`.

---

## 🔧 Technical Guide: Adding New Hardware

### Adding a new USB VID:PID (board recognition)

Add the VID:PID to `core/usb_ident.py`:

```python
USB_IDS = [
    # ... existing entries ...
    ("0x1234", "0x5678", "Brand Name", "Product Name", "chinese", "avr"),
]
```

Fields: `VID`, `PID`, `Manufacturer`, `Product`, `Driver Type`, `Architecture`

**Architecture codes**: `avr`, `samd`, `rp2040`, `esp32`, `esp8266`, `stm32`, `nrf52`

### Adding a new chip signature (AVR/SAMD)

Add the signature to `core/board_info.py`:

```python
KNOWN_SIGNATURES = {
    # ... existing entries ...
    (0x1E, 0x95, 0x14): ("ATmega328P", "avr", 32768, 2048, 1024),
    #              ^signature bytes^  ^name^ ^arch^ ^flash^ ^ram^ ^eeprom^
}
```

The signature is read by avrdude from the chip.

### Adding a USB description heuristic (for boards without known VID:PID)

Add a regex pattern to `core/board_heuristic.py`:

```python
HEURISTICS = [
    # ... existing entries ...
    (re.compile(r"Arduino.*Nano", re.I), "Arduino Nano", "avr", "nano"),
]
```

### Adding a new diagnostic sketch

1. Create a new folder under `firmware/` (e.g., `firmware/esp32/`)
2. Write the sketch following this output protocol:

```cpp
// Diagnostic output format (parsed by core/parser.py)
Serial.println("$ID,<board_name>,<chip_name>");
Serial.println("$VCC,<millivolts>");
Serial.println("$LED,1");        // LED test: 1=pass, 0=fail
Serial.println("$DIGPIN,<pin>,<0|1>");  // Digital pin test
Serial.println("$ADC,<pin>,<0-1023>");   // ADC reading
Serial.println("$DONE,<code>"); // 0=OK, 1=WARN, 2=FAIL
```

3. Update `core/flasher.py` to include the new architecture in the upload logic.

### Adding a new flasher tool (bossac, esptool, picotool)

1. Add the tool path finder to `core/platform_utils.py`:
```python
def get_bossac_path() -> Optional[str]:
    """Find bossac binary for SAMD upload."""
    return find_tool("bossac") or _search_common_paths(...)
```

2. Export it from `core/__init__.py`.

3. Update `core/flasher.py` to detect the architecture and call the appropriate tool.

---

## 🧪 Testing

Run all tests:
```bash
python -m unittest discover tests
```

Run with coverage:
```bash
pytest --cov=core --cov=gui --cov-report=html
```

Run linting:
```bash
ruff check core/ gui/ main.py
ruff format --check core/ gui/ main.py
```

Run type checking:
```bash
mypy core/ gui/ main.py
```

### Adding new tests
- Tests go in `tests/`
- Naming: `test_<module>.py`
- Test class: `Test<ModuleName>`
- Test methods: `test_<description>`
- Use `unittest.mock.patch` to mock serial ports and hardware.

---

## 📦 Building the Executable

```bash
pip install pyinstaller
pyinstaller ArduCheck.spec
```

The `.exe` will be in `dist/ArduCheck/`.

---

Have any questions? Feel free to start a discussion or contact the maintainer, **KherCent**. Happy coding!

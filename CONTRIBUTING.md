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
   cd ArduCheck
   ```
3. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/my-new-feature
   # or for bug fixes
   git checkout -b fix/bug-fix
   ```
4. **Make your changes** and ensure they follow style guidelines.
5. **Test your changes**:
   - Run automated tests: `python -m unittest tests/test_smoke.py`
   - If you modified the firmware, make sure it compiles correctly using `arduino-cli`.
6. **Commit** your changes cleanly.
7. **Push** your changes to your fork and open a **Pull Request** targeting the `main` branch of the official repository.

---

## 🎨 Code and Style Guidelines

### Python (Host CLI & GUI)
- We follow the **PEP 8** style guide.
- Comment code where logic is complex.
- Maintain cross-platform compatibility (avoid OS-specific calls that aren't portable).

### Firmware C/C++ (Sketches in `firmware/`)
- Firmware code should be as lightweight and efficient as possible.
- Avoid using external libraries that cannot be easily installed from the official Arduino Library Manager.
- Structure test outputs consistently so they can be easily parsed by `core/parser.py`.

---

Have any questions? Feel free to start a discussion or contact the maintainer, **KherCent**. Happy coding!

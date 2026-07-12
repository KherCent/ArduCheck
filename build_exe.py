"""
build_exe.py — Genera un ejecutable standalone con PyInstaller

Uso:
    python build_exe.py

Requiere:
    pip install pyinstaller pyserial pyusb reportlab

Nota: para que el ejecutable sea más pequeño, el script
copia ArduCheck.spec (que ya tiene los excludes optimizados)
al directorio actual antes de compilar.
"""

import os
import shutil
import subprocess
import sys

# Ir al directorio del proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Limpiar anteriores
for f in ["build", "dist"]:
    if os.path.exists(f):
        if os.path.isdir(f):
            shutil.rmtree(f)
        else:
            os.remove(f)

# Copiar el spec optimizado si no existe ya
SPEC_FILE = "ArduCheck.spec"
if not os.path.exists(SPEC_FILE):
    print(f"ADVERTENCIA: {SPEC_FILE} no encontrado.")
    print("Generando spec básico...")
else:
    print(f"Usando spec optimizado: {SPEC_FILE}")

print("Generando ArduCheck.exe...")
print("  - Excluye módulos innecesarios (numpy, pandas, PyQt5, etc.)")
print("  - Usa --strip para reducir tamaño")
print("  - Usa --upx para compresión adicional")
print("  - Nivel de optimización: 1 (elimina assert/__debug__)")

# Ejecutar PyInstaller
result = subprocess.run(
    [sys.executable, "-m", "PyInstaller", "--clean", SPEC_FILE],
    capture_output=False,
)

if result.returncode != 0:
    print("ERROR: PyInstaller falló.")
    sys.exit(1)

exe_path = os.path.join("dist", "ArduCheck.exe")
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"\n¡Listo! Ejecutable en: {exe_path}")
    print(f"Tamaño: {size_mb:.2f} MB")
else:
    print("\nERROR: El ejecutable no se generó.")
    sys.exit(1)

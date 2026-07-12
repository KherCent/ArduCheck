#!/usr/bin/env bash
# ===============================================
# ArduCheck — Launcher consola (Linux/macOS)
# ===============================================
set -e

cd "$(dirname "$0")"

# Verificar Python 3
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 no está instalado o no está en PATH."
    echo "Instala Python 3.10+ desde https://python.org"
    echo "En macOS: brew install python"
    echo "En Linux (Debian/Ubuntu): sudo apt install python3 python3-pip"
    echo "En Linux (Fedora): sudo dnf install python3"
    exit 1
fi

# Verificar dependencias (pyserial, pyusb)
MISSING=""
for pkg in pyserial pyusb; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        MISSING="$MISSING $pkg"
    fi
done

if [ -n "$MISSING" ]; then
    echo "Instalando dependencias:$MISSING"
    pip3 install --user -q$pkg || sudo pip3 install -q$pkg
fi

# Verificar arduino-cli (opcional)
if ! command -v arduino-cli &>/dev/null; then
    echo ""
    echo "[INFO] arduino-cli no encontrado en PATH."
    echo "Para subir sketches automáticamente, instálalo con:"
    echo "  Linux:  curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh"
    echo "  macOS:  brew install arduino-cli/arduino-cli/arduino-cli"
    echo "  Luego ejecuta: arduino-cli core install arduino:avr"
    echo ""
fi

echo ""
echo "===================================================="
echo " ArduCheck  -  Modo consola"
echo "===================================================="
echo ""
echo "Comandos disponibles:"
echo "  1) Escanear puertos"
echo "  2) Diagnosticar primera placa detectada"
echo "  3) Diagnosticar un puerto específico"
echo "  4) Ver instrucciones de instalación"
echo "  5) Salir"
echo ""

read -p "Elige una opción: " opc

case "$opc" in
    1) python3 main.py scan ;;
    2) python3 main.py diagnose ;;
    3)
        read -p "Puerto (ej. /dev/ttyUSB0): " port
        python3 main.py diagnose --port "$port"
        ;;
    4) python3 main.py install ;;
    5) exit 0 ;;
    *) echo "Opción no válida." ;;
esac

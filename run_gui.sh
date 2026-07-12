#!/usr/bin/env bash
# ===============================================
# ArduCheck — Launcher GUI (Linux/macOS)
# ===============================================
set -e

cd "$(dirname "$0")"

# Verificar Python 3
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 no está instalado o no está en PATH."
    echo "Instala Python 3.10+ desde https://python.org"
    exit 1
fi

# Verificar tkinter (incluido en Python estándar, pero verificar)
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "ERROR: tkinter no está disponible."
    echo "En Linux (Debian/Ubuntu): sudo apt install python3-tk"
    echo "En Linux (Fedora): sudo dnf install python3-tkinter"
    echo "En macOS: brew install python-tk (desde python)"
    exit 1
fi

# Verificar dependencias
for pkg in pyserial pyusb; do
    if ! python3 -c "import $pkg" 2>/dev/null; then
        echo "Instalando $pkg..."
        pip3 install --user -q $pkg || sudo pip3 install -q $pkg
    fi
done

echo "Iniciando GUI de ArduCheck..."
python3 main.py gui

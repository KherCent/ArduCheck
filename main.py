"""
main.py — CLI de diagnóstico Arduino

Uso:
    python main.py scan                  -> lista placas detectadas
    python main.py diagnose --port COM3  -> diagnóstico completo en ese puerto
    python main.py gui                   -> abre la GUI Tkinter
    python main.py install               -> muestra instrucciones para instalar arduino-cli
"""

from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Permitir ejecutar desde cualquier directorio
sys.path.insert(0, str(Path(__file__).parent))

from core import ArduinoDetector, ArduinoDiagnostic


def cmd_scan(args):
    boards = ArduinoDetector.scan()
    if not boards:
        print("No se detectaron puertos seriales.")
        return
    print(f"{'Puerto':<10} {'Identificacion':<35} {'VID:PID':<14} {'Arduino?'}")
    print("-" * 80)
    for b in boards:
        vid_pid = f"{b.vid:04X}:{b.pid:04X}" if b.vid and b.pid else "????"
        flag = "[SI]" if b.is_arduino_like else "    "
        print(f"{b.port:<10} {b.guessed_name:<35} {vid_pid:<14} {flag}")
    print()
    print(f"Total: {len(boards)} puerto(s) - {sum(1 for b in boards if b.is_arduino_like)} compatible(s) Arduino")


def cmd_diagnose(args):
    port = args.port
    if not port:
        # autodetección
        board = ArduinoDetector.find_first(only_arduino=False)
        if not board:
            print("No hay puertos seriales disponibles. Conecta un Arduino.")
            sys.exit(1)
        port = board.port
        print(f"Usando puerto autodetectado: {port} ({board.guessed_name})")
    diag = ArduinoDiagnostic(port=port, baud=args.baud, timeout=args.timeout)
    result = diag.run_full_diagnostic()
    print()
    print("=" * 70)
    print(result.summary)
    print("=" * 70)
    print(f"Puerto:    {result.port}")
    print(f"Placa:     {result.board}")
    print(f"Chip:      {result.chip}")
    print(f"Veredicto: {result.verdict}  (score {result.score}/100)")
    print()
    if result.details:
        print("[OK] Detalles:")
        for d in result.details:
            print(f"   - {d}")
    if result.warnings:
        print("\n[WARN] Advertencias:")
        for w in result.warnings:
            print(f"   - {w}")
    if result.errors:
        print("\n[FAIL] Errores:")
        for e in result.errors:
            print(f"   - {e}")
    print()
    sys.exit(0 if result.verdict == "GOOD" else (2 if result.verdict == "WARN" else 3))


def cmd_gui(args):
    from gui.app import launch_gui
    launch_gui()


def cmd_watch(args):
    """Modo consola: monitor de conexion en caliente."""
    from core.watcher import get_default_watcher

    print("=" * 70)
    print(" WATCHER - Conexion en caliente de Arduino")
    print(" Conecta/desconecta placas y veras los eventos aqui.")
    print(" Pulsa Ctrl+C para salir.")
    print("=" * 70)
    print()

    def on_connected(b):
        arduino = "[Arduino]" if b.is_arduino_like else ""
        print(f"  >> CONECTADO   {b.port:<10} {b.guessed_name:<30} {arduino}")

    def on_disconnected(port):
        print(f"  << DESCONECTADO {port}")

    w = get_default_watcher()
    w.add_connected_handler(on_connected)
    w.add_disconnected_handler(on_disconnected)
    w.start()

    # Mostrar estado inicial
    boards = w.current_boards
    print(f"Estado inicial: {len(boards)} puerto(s).")
    for b in boards:
        arduino = "[Arduino]" if b.is_arduino_like else ""
        print(f"  * {b.port:<10} {b.guessed_name:<30} {arduino}")
    print()
    print("Esperando eventos... (Ctrl+C para salir)")
    print()

    try:
        while True:
            import time
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nDeteniendo watcher...")
        w.stop()
        print("OK.")


def cmd_install(args):
    print("=" * 70)
    print(" INSTALACIÓN DE DEPENDENCIAS OPCIONALES")
    print("=" * 70)
    print()
    print("1) arduino-cli (recomendado, para subir el sketch de auto-test):")
    print("   winget install ArduinoSA.CLI")
    print("   o descarga: https://arduino.github.io/arduino-cli/latest/installation/")
    print()
    print("   Luego instala el core AVR:")
    print("   arduino-cli core install arduino:avr")
    print()
    print("2) Driver CH340 (para muchos clones chinos):")
    print("   https://www.wch-ic.com/downloads/CH341SER_EXE.html")
    print()
    print("3) Dependencias Python (ya instaladas):")
    print("   pip install pyserial pyusb")
    print()


def main():
    p = argparse.ArgumentParser(description="Arduino Diagnostic Tool")
    sub = p.add_subparsers(dest="cmd")

    p_scan = sub.add_parser("scan", help="Escanear puertos seriales")

    p_diag = sub.add_parser("diagnose", help="Diagnosticar una placa")
    p_diag.add_argument("--port", help="Puerto (p.ej. COM3, /dev/ttyUSB0)")
    p_diag.add_argument("--baud", type=int, default=115200)
    p_diag.add_argument("--timeout", type=float, default=60.0)

    p_gui = sub.add_parser("gui", help="Abrir interfaz grafica")
    sub.add_parser("install", help="Mostrar instrucciones de instalacion")
    sub.add_parser("watch", help="Monitor de conexion en caliente (Ctrl+C para salir)")

    args = p.parse_args()
    if args.cmd == "scan":
        cmd_scan(args)
    elif args.cmd == "diagnose":
        cmd_diagnose(args)
    elif args.cmd == "gui":
        cmd_gui(args)
    elif args.cmd == "install":
        cmd_install(args)
    elif args.cmd == "watch":
        cmd_watch(args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()

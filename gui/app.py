"""
gui/app.py - Interfaz grafica Tkinter para diagnostico Arduino
Incluye deteccion automatica de hot-plug USB.
"""

from __future__ import annotations
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    ArduinoDetector, ArduinoDiagnostic,
    HotplugWatcher, get_default_watcher,
    upload_sketch, is_flasher_available,
)


class DiagnosticGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ArduCheck")
        self.root.geometry("920x680")
        self.root.minsize(820, 620)

        self.event_queue: "queue.Queue" = queue.Queue()
        self.boards_cache = []
        self._verdict_label: ttk.Label = None

        self._build_ui()
        self.root.after(200, self._poll_queue)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Inicia watcher de hot-plug
        self.watcher = get_default_watcher()
        self.watcher.add_connected_handler(self._on_board_connected)
        self.watcher.add_disconnected_handler(self._on_board_disconnected)
        self.watcher.start()
        self.set_status("Watcher activo. Conecta un Arduino y aparecera aqui automaticamente.")

        # Escanear al inicio
        self.root.after(500, self.scan_boards)

    # ---------- UI ----------
    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        top = ttk.Frame(self.root, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Button(top, text="Escanear placas", command=self.scan_boards).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Diagnosticar seleccion", command=self.run_diagnostic).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Subir sketch + Diagnosticar",
                   command=self.run_upload_and_diagnose).pack(side=tk.LEFT, padx=4)
        self.auto_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Auto-diagnosticar al conectar",
                        variable=self.auto_var).pack(side=tk.LEFT, padx=12)
        ttk.Button(top, text="Salir", command=self._on_close).pack(side=tk.RIGHT, padx=4)

        main = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left = ttk.Frame(main)
        main.add(left, weight=1)
        ttk.Label(left, text="Placas detectadas", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        cols = ("port", "name", "vidpid", "arduino")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=12)
        self.tree.heading("port", text="Puerto")
        self.tree.heading("name", text="Identificacion")
        self.tree.heading("vidpid", text="VID:PID")
        self.tree.heading("arduino", text="Arduino?")
        self.tree.column("port", width=100)
        self.tree.column("name", width=260)
        self.tree.column("vidpid", width=100)
        self.tree.column("arduino", width=60, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=4)

        right = ttk.Frame(main)
        main.add(right, weight=2)

        self.verdict_var = tk.StringVar(value="-")
        self.score_var = tk.StringVar(value="")
        self.board_var = tk.StringVar(value="-")
        self.chip_var = tk.StringVar(value="-")
        self.vcc_var = tk.StringVar(value="-")

        header = ttk.Frame(right)
        header.pack(fill=tk.X)
        self._verdict_label = ttk.Label(header, textvariable=self.verdict_var,
                                        font=("Segoe UI", 22, "bold"))
        self._verdict_label.pack(side=tk.LEFT, padx=8)
        ttk.Label(header, textvariable=self.score_var, font=("Segoe UI", 14)).pack(side=tk.LEFT, padx=8)

        info = ttk.Frame(right)
        info.pack(fill=tk.X, pady=4)
        for label, var in [("Placa:", self.board_var), ("Chip:", self.chip_var),
                           ("Voltaje:", self.vcc_var)]:
            row = ttk.Frame(info)
            row.pack(anchor=tk.W, padx=8, pady=2)
            ttk.Label(row, text=label, width=12, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
            ttk.Label(row, textvariable=var).pack(side=tk.LEFT)

        ttk.Label(right, text="Detalle del diagnostico",
                  font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(8, 0))
        self.log = scrolledtext.ScrolledText(right, wrap=tk.WORD, font=("Consolas", 10), height=18)
        self.log.pack(fill=tk.BOTH, expand=True, pady=4)

        self.status_var = tk.StringVar(value="Listo.")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN,
                  anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- Watcher callbacks ----------
    def _on_board_connected(self, board):
        self.event_queue.put(("connected", board))

    def _on_board_disconnected(self, port):
        self.event_queue.put(("disconnected", port))

    # ---------- Helpers ----------
    def log_line(self, msg: str):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)

    def set_status(self, msg: str):
        self.status_var.set(msg)

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for b in self.boards_cache:
            vid_pid = f"{b.vid:04X}:{b.pid:04X}" if b.vid and b.pid else "????"
            flag = "[SI]" if b.is_arduino_like else ""
            self.tree.insert("", tk.END, iid=b.port,
                             values=(b.port, b.guessed_name, vid_pid, flag))

    # ---------- Comandos ----------
    def scan_boards(self):
        self.boards_cache = ArduinoDetector.scan()
        self._refresh_tree()
        self.set_status(f"{len(self.boards_cache)} puerto(s) detectado(s).")
        self.log_line(f"[scan] {len(self.boards_cache)} puerto(s) encontrado(s).")

    def _handle_connected(self, board):
        self.log_line(f"[hotplug] CONECTADO  -> {board.port}  ({board.guessed_name})")
        self.scan_boards()
        if self.auto_var.get() and board.is_arduino_like:
            self.set_status(f"Auto-diagnosticando {board.port}...")
            threading.Thread(target=self._diag_worker,
                             args=(board.port, board.guessed_type), daemon=True).start()

    def _handle_disconnected(self, port):
        self.log_line(f"[hotplug] DESCONECTADO -> {port}")
        self.scan_boards()

    def run_diagnostic(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sin seleccion", "Selecciona primero un puerto de la lista.")
            return
        port = sel[0]
        # buscar board_type si esta en cache
        board_type = "uno"
        for b in self.boards_cache:
            if b.port == port:
                board_type = b.guessed_type or "uno"
                break
        self.set_status(f"Diagnosticando {port}...")
        self._reset_result_panel()
        threading.Thread(target=self._diag_worker, args=(port, board_type), daemon=True).start()

    def run_upload_and_diagnose(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sin seleccion", "Selecciona primero un puerto de la lista.")
            return
        port = sel[0]
        board_type = "uno"
        for b in self.boards_cache:
            if b.port == port:
                board_type = b.guessed_type or "uno"
                break
        if not is_flasher_available():
            messagebox.showwarning(
                "arduino-cli no instalado",
                "Para subir el sketch automaticamente instala arduino-cli:\n"
                "  winget install ArduinoSA.CLI\n"
                "  arduino-cli core install arduino:avr\n\n"
                "Continuare con el diagnostico sin subir sketch."
            )
        else:
            self.set_status(f"Subiendo sketch a {port}...")
            self._reset_result_panel()
            threading.Thread(target=self._upload_and_diag_worker,
                             args=(port, board_type), daemon=True).start()

    def _diag_worker(self, port: str, board_type: str = "uno"):
        try:
            diag = ArduinoDiagnostic(port=port, baud=115200, timeout=60)
            res = diag.run_full_diagnostic()
            self.event_queue.put(("done", res))
        except Exception as e:
            self.event_queue.put(("error", e))

    def _upload_and_diag_worker(self, port: str, board_type: str):
        try:
            ok, msg = upload_sketch(port, board_type)
            self.event_queue.put(("upload_result", (ok, msg, port, board_type)))
            if ok:
                time.sleep(3)  # esperar a que la placa termine el reset
                self._diag_worker(port, board_type)
        except Exception as e:
            self.event_queue.put(("error", e))

    def _reset_result_panel(self):
        self.verdict_var.set("...")
        self.score_var.set("")
        self.board_var.set("-")
        self.chip_var.set("-")
        self.vcc_var.set("-")
        self._set_verdict_color("#555")

    def _set_verdict_color(self, color):
        try:
            if self._verdict_label is not None:
                self._verdict_label.configure(foreground=color)
        except Exception:
            pass

    def _poll_queue(self):
        try:
            while True:
                kind, payload = self.event_queue.get_nowait()
                if kind == "connected":
                    self._handle_connected(payload)
                elif kind == "disconnected":
                    self._handle_disconnected(payload)
                elif kind == "done":
                    self._render_result(payload)
                elif kind == "upload_result":
                    ok, msg, port, bt = payload
                    if ok:
                        self.log_line(f"[upload] OK en {port}: {msg}")
                    else:
                        self.log_line(f"[upload] FALLO en {port}: {msg}")
                elif kind == "error":
                    messagebox.showerror("Error", f"Fallo:\n{payload}")
                    self.set_status("Error.")
                    self.verdict_var.set("ERROR")
                    self._set_verdict_color("#c0182c")
        except queue.Empty:
            pass
        self.root.after(200, self._poll_queue)

    def _render_result(self, res):
        emoji = {"GOOD": "[OK] BUENO", "WARN": "[WARN] ALERTA",
                 "FAIL": "[FAIL] MALO"}.get(res.verdict, "?")
        color = {"GOOD": "#0a8f3c", "WARN": "#cc8b00",
                 "FAIL": "#c0182c"}.get(res.verdict, "#000")
        self.verdict_var.set(emoji)
        self._set_verdict_color(color)
        self.score_var.set(f"score {res.score}/100")
        self.board_var.set(res.board)
        self.chip_var.set(res.chip)
        self.vcc_var.set(f"{res.report.vcc_mv/100:.2f} V"
                         if res.report and res.report.vcc_mv else "-")
        self.log_line("")
        self.log_line("=" * 60)
        self.log_line(res.summary)
        self.log_line("=" * 60)
        if res.details:
            self.log_line("[OK] Detalles:")
            for d in res.details:
                self.log_line(f"   - {d}")
        if res.warnings:
            self.log_line("[WARN] Advertencias:")
            for w in res.warnings:
                self.log_line(f"   - {w}")
        if res.errors:
            self.log_line("[FAIL] Errores:")
            for e in res.errors:
                self.log_line(f"   - {e}")
        self.set_status(f"Diagnostico finalizado: {res.verdict}")

    def _on_close(self):
        try:
            self.watcher.stop()
        except Exception:
            pass
        self.root.destroy()


def launch_gui():
    root = tk.Tk()
    DiagnosticGUI(root)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()

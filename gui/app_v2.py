"""
gui/app_v2.py — ArduCheck GUI v2 con sistema de pestañas
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# Permite imports absolutos desde el paquete 'core'
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import ArduinoDetector, get_default_watcher
from gui.theme import get_theme, set_theme, LIGHT_THEME, DARK_THEME
from gui.tabs.tab_diagnostico import TabDiagnostico
from gui.tabs.tab_reparar import TabReparar


class ArduCheckGUI:
    """GUI principal con sistema de pestañas."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ArduCheck v2.0")
        self.root.geometry("1100x750")
        self.root.minsize(900, 650)

        self.boards_cache = []
        self.selected_port = tk.StringVar(value="")
        self.theme_name = tk.StringVar(value="light")

        self._build_ui()
        self._start_watcher()

        # Escanear al inicio
        self.root.after(500, self._scan_boards)

    def _build_ui(self):
        theme = get_theme()

        # ---------- Header ----------
        header = ttk.Frame(self.root, padding=10)
        header.pack(fill=tk.X)

        ttk.Label(header, text="ArduCheck",
                  font=("Segoe UI", 22, "bold")).pack(side=tk.LEFT)

        # Selector de puerto
        port_frame = ttk.Frame(header)
        port_frame.pack(side=tk.LEFT, padx=30)

        ttk.Label(port_frame, text="Puerto:",
                  font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.selected_port,
                                       width=12, state="readonly", font=("Segoe UI", 11))
        self.port_combo.pack(side=tk.LEFT, padx=5)
        self.port_combo.bind("<<ComboboxSelected>>", self._on_port_selected)

        ttk.Button(header, text="Actualizar",
                   command=self._scan_boards).pack(side=tk.LEFT, padx=5)

        # Toggle tema
        ttk.Label(header, text="Tema:").pack(side=tk.RIGHT, padx=(0, 5))
        self.theme_toggle = ttk.Combobox(header, values=["light", "dark"],
                                          textvariable=self.theme_name,
                                          width=8, state="readonly")
        self.theme_toggle.pack(side=tk.RIGHT)
        self.theme_toggle.bind("<<ComboboxSelected>>", self._on_theme_changed)

        # ---------- Notebook (pestañas) ----------
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Pestaña de Placas
        self.tab_placas = self._build_tab_placas()
        self.notebook.add(self.tab_placas, text="  Placas  ")

        # Pestaña de Diagnóstico
        self.tab_diagnostico = TabDiagnostico(self.notebook, self)
        self.notebook.add(self.tab_diagnostico, text="  Diagnostico  ")

        # Pestaña de Reparación
        self.tab_reparar = TabReparar(self.notebook, self)
        self.notebook.add(self.tab_reparar, text="  Reparar  ")

        # ---------- Status bar ----------
        self.status_var = tk.StringVar(value="Listo")
        ttk.Label(self.root, textvariable=self.status_var,
                  relief=tk.SUNKEN, anchor=tk.W,
                  font=("Segoe UI", 9)).pack(side=tk.BOTTOM, fill=tk.X)

    def _build_tab_placas(self):
        """Construye la pestaña de listado de placas."""
        frame = ttk.Frame(self.notebook, padding=10)

        # Header
        ttk.Label(frame, text="Placas Conectadas",
                  font=("Segoe UI", 16, "bold")).pack(anchor=tk.W, pady=5)

        # Lista de placas
        cols = ("icon", "puerto", "nombre", "vidpid", "tipo")
        self.placas_tree = ttk.Treeview(frame, columns=cols, show="headings", height=15)
        self.placas_tree.heading("icon", text="")
        self.placas_tree.heading("puerto", text="Puerto")
        self.placas_tree.heading("nombre", text="Nombre")
        self.placas_tree.heading("vidpid", text="VID:PID")
        self.placas_tree.heading("tipo", text="Tipo")
        self.placas_tree.column("icon", width=40, anchor=tk.CENTER)
        self.placas_tree.column("puerto", width=100)
        self.placas_tree.column("nombre", width=300)
        self.placas_tree.column("vidpid", width=120)
        self.placas_tree.column("tipo", width=200)
        self.placas_tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.placas_tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Diagnosticar Seleccionada",
                   command=self._diagnose_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Reparar Seleccionada",
                   command=self._repair_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Refrescar",
                   command=self._scan_boards).pack(side=tk.RIGHT, padx=5)

        return frame

    def _on_tree_select(self, event=None):
        """Cuando se selecciona una placa."""
        sel = self.placas_tree.selection()
        if sel:
            item = self.placas_tree.item(sel[0])
            values = item.get("values", [])
            if values:
                port = values[1]  # columna puerto
                self.selected_port.set(port)

    def _on_port_selected(self, event=None):
        """Cuando se cambia el puerto seleccionado."""
        port = self.selected_port.get()
        self.status_var.set(f"Puerto seleccionado: {port}")

    def _on_theme_changed(self, event=None):
        """Cambia el tema de la aplicacion."""
        theme_name = self.theme_name.get()
        set_theme(theme_name)
        self._apply_theme()
        self.status_var.set(f"Tema cambiado a: {theme_name}")

    def _apply_theme(self):
        """Aplica el tema actual a la ventana."""
        theme = get_theme()
        # Fondo general
        self.root.configure(bg=theme["bg"])

    def _scan_boards(self):
        """Escanea las placas conectadas."""
        self.status_var.set("Escaneando puertos...")
        self.boards_cache = ArduinoDetector.scan()

        # Limpiar tree
        for item in self.placas_tree.get_children():
            self.placas_tree.delete(item)

        # Llenar
        for b in self.boards_cache:
            vid_pid = f"{b.vid:04X}:{b.pid:04X}" if b.vid and b.pid else "????"
            icon = "A" if b.is_arduino_like else "?"
            tipo = self._guess_type(b)

            self.placas_tree.insert("", tk.END, values=(
                icon, b.port, b.guessed_name, vid_pid, tipo
            ))

        self.status_var.set(f"{len(self.boards_cache)} placa(s) detectada(s)")
        self._refresh_port_combo()

    def _guess_type(self, board) -> str:
        """Adivina el tipo de placa."""
        if "ch340" in board.guessed_name.lower() or "ch341" in board.guessed_name.lower():
            return "Clone CH340"
        elif "ch9102" in board.guessed_name.lower():
            return "Clone CH9102"
        elif "cp210" in board.guessed_name.lower():
            return "Silicon Labs CP210x"
        elif "ftdi" in board.guessed_name.lower():
            return "FTDI"
        elif "pl2303" in board.guessed_name.lower():
            return "Prolific PL2303"
        elif board.is_arduino_like:
            return "Arduino Original"
        return "Otro"

    def _refresh_port_combo(self):
        """Actualiza el combobox de puertos."""
        ports = [b.port for b in self.boards_cache]
        self.port_combo["values"] = ports
        if ports and not self.selected_port.get():
            self.selected_port.set(ports[0])

    def _diagnose_selected(self):
        """Diagnosticar la placa seleccionada."""
        port = self.selected_port.get()
        if not port:
            self.status_var.set("Selecciona una placa primero")
            return
        self.notebook.select(1)  # Ir a pestaña diagnóstico
        self.tab_diagnostico._start_diagnostic()

    def _repair_selected(self):
        """Reparar la placa seleccionada."""
        port = self.selected_port.get()
        if not port:
            self.status_var.set("Selecciona una placa primero")
            return
        self.notebook.select(2)  # Ir a pestaña reparar

    def _start_watcher(self):
        """Inicia el watcher de hotplug."""
        self.watcher = get_default_watcher()
        self.watcher.add_connected_handler(self._on_connected)
        self.watcher.add_disconnected_handler(self._on_disconnected)
        self.watcher.start()
        self.status_var.set("Watcher activo - Conecta un Arduino")

    def _on_connected(self, board):
        """Callback cuando se conecta una placa."""
        self.status_var.set(f"Conectado: {board.port} ({board.guessed_name})")
        self._scan_boards()

    def _on_disconnected(self, port):
        """Callback cuando se desconecta una placa."""
        self.status_var.set(f"Desconectado: {port}")
        self._scan_boards()

    def get_selected_port(self) -> str:
        """Retorna el puerto seleccionado."""
        return self.selected_port.get()

    def set_status(self, msg: str):
        """Actualiza el status bar."""
        self.status_var.set(msg)

    def run(self):
        """Ejecuta el mainloop."""
        self.root.mainloop()


def launch_gui():
    """Lanza la GUI."""
    root = tk.Tk()
    app = ArduCheckGUI(root)
    app.run()


if __name__ == "__main__":
    launch_gui()

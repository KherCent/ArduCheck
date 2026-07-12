"""
gui/tabs/tab_diagnostico.py — Pestaña de diagnóstico con veredicto visual
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk
import threading
import queue

from gui.theme import get_theme


class TabDiagnostico(ttk.Frame):
    """Pestaña de diagnóstico con veredicto, score y lista de tests."""

    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        self.event_queue: queue.Queue = queue.Queue()
        self.tests: list = []
        self._running = False

        self._build_ui()

    def _build_ui(self):
        theme = get_theme()

        # Header con veredicto grande
        header = ttk.Frame(self, padding=10)
        header.pack(fill=tk.X)

        self.verdict_label = ttk.Label(
            header, text="SIN DIAGNOSTICAR",
            font=("Segoe UI", 32, "bold"),
            foreground=theme["fg"]
        )
        self.verdict_label.pack(side=tk.LEFT, padx=10)

        # Score gauge
        score_frame = ttk.Frame(header)
        score_frame.pack(side=tk.LEFT, padx=20)

        self.score_canvas = tk.Canvas(score_frame, width=100, height=100, bg=theme["bg"], highlightthickness=0)
        self.score_canvas.pack()
        self.score_text = self.score_canvas.create_text(50, 50, text="--/100", font=("Segoe UI", 18, "bold"), fill=theme["fg"])
        self._draw_gauge(0)

        # Info de la placa
        info_frame = ttk.Frame(header)
        info_frame.pack(side=tk.RIGHT, padx=10)

        self.info_labels = {}
        for label_text in ["Puerto:", "Placa:", "Chip:", "Voltaje:"]:
            row = ttk.Frame(info_frame)
            row.pack(anchor=tk.W, pady=2)
            ttk.Label(row, text=label_text, width=10, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
            value_label = ttk.Label(row, text="-", font=("Segoe UI", 10))
            value_label.pack(side=tk.LEFT)
            self.info_labels[label_text] = value_label

        # Barra de progreso
        progress_frame = ttk.Frame(self, padding=(10, 0, 10, 0))
        progress_frame.pack(fill=tk.X, pady=5)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                             maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        self.progress_label = ttk.Label(progress_frame, text="", font=("Segoe UI", 9))
        self.progress_label.pack(anchor=tk.W)

        # Lista de tests
        tests_frame = ttk.LabelFrame(self, text="Resultados de Tests", padding=10)
        tests_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        cols = ("test", "resultado", "valor")
        self.tests_tree = ttk.Treeview(tests_frame, columns=cols, show="headings", height=15)
        self.tests_tree.heading("test", text="Test")
        self.tests_tree.heading("resultado", text="Resultado")
        self.tests_tree.heading("valor", text="Valor")
        self.tests_tree.column("test", width=200)
        self.tests_tree.column("resultado", width=100, anchor=tk.CENTER)
        self.tests_tree.column("valor", width=150, anchor=tk.CENTER)
        self.tests_tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar para tests
        scrollbar = ttk.Scrollbar(tests_frame, orient=tk.VERTICAL, command=self.tests_tree.yview)
        self.tests_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Botones
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="Iniciar Diagnostico", command=self._start_diagnostic).pack(side=tk.LEFT, padx=5)

        self._poll_queue()

    def _draw_gauge(self, score: int):
        """Dibuja el gauge circular con el score."""
        theme = get_theme()
        self.score_canvas.delete("arc")

        # Color según score
        if score >= 85:
            color = theme["success"]
        elif score >= 60:
            color = theme["warning"]
        else:
            color = theme["danger"]

        # Dibujar arco (0-100%)
        x, y, r = 50, 50, 40
        extent = int(score * 3.6)  # 360 grados = 100%
        self.score_canvas.create_arc(x - r, y - r, x + r, y + r,
                                      start=90, extent=-extent,
                                      outline=color, width=8, tags="arc")
        self.score_canvas.itemconfigure(self.score_text, text=f"{score}/100", fill=color)

    def _poll_queue(self):
        """Procesa eventos de la cola."""
        try:
            while True:
                msg = self.event_queue.get_nowait()
                if msg == "start":
                    self._running = True
                    self.verdict_label.configure(text="DIAGNOSTICANDO...")
                elif msg == "done":
                    self._running = False
                    self.progress_var.set(100)
                    self.progress_label.configure(text="Completado")
                elif isinstance(msg, dict):
                    self._update_result(msg)
        except queue.Empty:
            pass
        self.after(200, self._poll_queue)

    def _update_result(self, result: dict):
        """Actualiza la UI con el resultado del diagnóstico."""
        theme = get_theme()

        verdict = result.get("verdict", "?")
        score = result.get("score", 0)

        verdict_text = {
            "GOOD": "BUENO",
            "WARN": "ADVERTENCIA",
            "FAIL": "MALO"
        }.get(verdict, "?")

        verdict_color = {
            "GOOD": theme["success"],
            "WARN": theme["warning"],
            "FAIL": theme["danger"]
        }.get(verdict, theme["fg"])

        self.verdict_label.configure(text=verdict_text, foreground=verdict_color)
        self._draw_gauge(score)

        # Info
        self.info_labels["Puerto:"].configure(text=result.get("port", "-"))
        self.info_labels["Placa:"].configure(text=result.get("board", "-"))
        self.info_labels["Chip:"].configure(text=result.get("chip", "-"))
        self.info_labels["Voltaje:"].configure(text=f"{result.get('vcc', 0):.2f}V")

        # Limpiar y llenar tests
        for item in self.tests_tree.get_children():
            self.tests_tree.delete(item)

        for test in result.get("tests", []):
            status = test.get("status", "unknown")
            status_text = {"PASS": "PASA", "WARN": "WARN", "FAIL": "FALLA", "unknown": "?"}.get(status, "?")
            status_color = {"PASS": theme["success"], "WARN": theme["warning"], "FAIL": theme["danger"], "unknown": theme["fg"]}.get(status, theme["fg"])

            item_id = self.tests_tree.insert("", tk.END, values=(
                test.get("name", "?"),
                status_text,
                test.get("value", "")
            ))
            self.tests_tree.set(item_id, "resultado", status_text)

            # Colorear fila
            color = {"PASS": "#e8f5e9", "WARN": "#fff8e1", "FAIL": "#ffebee"}.get(status, theme["bg"])
            self.tests_tree.tag_configure(status, background=color)

    def _start_diagnostic(self):
        """Inicia el diagnóstico en un hilo separado."""
        if self._running:
            return

        port = self.app.get_selected_port()
        if not port:
            return

        self._running = True
        self.verdict_label.configure(text="DIAGNOSTICANDO...")
        self.progress_var.set(0)
        self.progress_label.configure(text="Iniciando...")

        # Limpiar tests
        for item in self.tests_tree.get_children():
            self.tests_tree.delete(item)

        def worker():
            self.event_queue.put("start")
            try:
                from core import ArduinoDiagnostic
                diag = ArduinoDiagnostic(port=port, timeout=60)
                result = diag.run_full_diagnostic()

                result_dict = {
                    "verdict": result.verdict,
                    "score": result.score,
                    "port": result.port,
                    "board": result.board,
                    "chip": result.chip,
                    "vcc": getattr(result, 'vcc', 0),
                    "tests": [
                        {"name": t, "status": "PASS", "value": ""}
                        for t in result.details or []
                    ] + [
                        {"name": t, "status": "WARN", "value": ""}
                        for t in result.warnings or []
                    ] + [
                        {"name": t, "status": "FAIL", "value": ""}
                        for t in result.errors or []
                    ]
                }
                self.event_queue.put(result_dict)
            except Exception as e:
                self.event_queue.put({"verdict": "FAIL", "score": 0, "error": str(e)})
            finally:
                self.event_queue.put("done")

        threading.Thread(target=worker, daemon=True).start()

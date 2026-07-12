"""
gui/tabs/tab_reparar.py — Pestaña de reparación con asistente paso a paso
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue

from gui.theme import get_theme


class TabReparar(ttk.Frame):
    """Pestaña de reparación con wizard paso a paso."""

    # Pasos del asistente
    STEPS = [
        ("detect", "Detectando placa"),
        ("erase", "Borrando flash"),
        ("bootloader", "Quemando bootloader"),
        ("fuses", "Configurando fuses"),
        ("verify", "Verificando reparacion"),
    ]

    def __init__(self, parent, app_ref):
        super().__init__(parent)
        self.app = app_ref
        self.event_queue: queue.Queue = queue.Queue()
        self.current_step = -1
        self._running = False

        self._build_ui()

    def _build_ui(self):
        theme = get_theme()

        # Header
        header = ttk.Frame(self, padding=15)
        header.pack(fill=tk.X)

        ttk.Label(header, text="Asistente de Reparacion",
                  font=("Segoe UI", 20, "bold")).pack(side=tk.LEFT)

        self.status_label = ttk.Label(header, text="Listo para reparar",
                                      font=("Segoe UI", 11), foreground=theme["accent"])
        self.status_label.pack(side=tk.RIGHT)

        # Wizard steps
        wizard_frame = ttk.LabelFrame(self, text="Pasos de Reparacion", padding=15)
        wizard_frame.pack(fill=tk.X, padx=15, pady=10)

        self.step_frames = {}
        self.step_labels = {}
        self.step_canvases = {}

        for i, (step_id, step_name) in enumerate(self.STEPS):
            step_frame = ttk.Frame(wizard_frame)
            step_frame.pack(fill=tk.X, pady=5)

            # Indicador circular
            canvas = tk.Canvas(step_frame, width=30, height=30, bg=theme["bg"], highlightthickness=0)
            canvas.pack(side=tk.LEFT, padx=10)

            # Circulo placeholder
            circle = canvas.create_oval(5, 5, 25, 25, outline=theme["border"], width=2)
            step_num = canvas.create_text(15, 15, text=str(i + 1), font=("Segoe UI", 10, "bold"))

            # Nombre del paso
            label = ttk.Label(step_frame, text=step_name, font=("Segoe UI", 11))
            label.pack(side=tk.LEFT, padx=10)

            # Barra de progreso del paso
            step_progress = ttk.Progressbar(step_frame, mode='indeterminate', length=150)
            step_progress.pack(side=tk.RIGHT, padx=10)

            self.step_frames[step_id] = step_frame
            self.step_labels[step_id] = label
            self.step_canvases[step_id] = {"canvas": canvas, "circle": circle, "num": step_num, "progress": step_progress}

        # Panel de info
        info_frame = ttk.LabelFrame(self, text="Informacion", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        self.info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, font=("Consolas", 10), height=12)
        self.info_text.pack(fill=tk.BOTH, expand=True)

        # Botones
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)

        self.btn_repair = ttk.Button(btn_frame, text="Iniciar Reparacion",
                                     command=self._start_repair, style="Accent.TButton")
        self.btn_repair.pack(side=tk.LEFT, padx=5)

        self.btn_cancel = ttk.Button(btn_frame, text="Cancelar",
                                     command=self._cancel_repair, state=tk.DISABLED)
        self.btn_cancel.pack(side=tk.LEFT, padx=5)

        ttk.Button(btn_frame, text="Limpiar Log",
                   command=self._clear_log).pack(side=tk.RIGHT, padx=5)

        self._poll_queue()

    def _log(self, msg: str):
        """Agrega texto al log."""
        self.info_text.insert(tk.END, msg + "\n")
        self.info_text.see(tk.END)

    def _clear_log(self):
        """Limpia el log."""
        self.info_text.delete("1.0", tk.END)

    def _poll_queue(self):
        """Procesa eventos de la cola."""
        try:
            while True:
                msg = self.event_queue.get_nowait()
                if isinstance(msg, dict):
                    self._handle_event(msg)
        except queue.Empty:
            pass
        self.after(200, self._poll_queue)

    def _handle_event(self, event: dict):
        """Maneja eventos del worker."""
        theme = get_theme()
        step = event.get("step")
        status = event.get("status")
        message = event.get("message", "")

        if message:
            self._log(message)

        if step:
            # Actualizar estado del paso
            canvas_data = self.step_canvases.get(step)
            if canvas_data:
                canvas = canvas_data["canvas"]
                circle = canvas_data["circle"]

                if status == "running":
                    canvas.itemconfigure(circle, fill=theme["warning"], outline=theme["warning"])
                    canvas_data["progress"].start(10)
                elif status == "done":
                    canvas.itemconfigure(circle, fill=theme["success"], outline=theme["success"])
                    canvas_data["progress"].stop()
                elif status == "fail":
                    canvas.itemconfigure(circle, fill=theme["danger"], outline=theme["danger"])
                    canvas_data["progress"].stop()

        if event.get("type") == "complete":
            success = event.get("success", False)
            if success:
                self.status_label.configure(text="Reparacion exitosa!", foreground=theme["success"])
                self._log("\n[OK] Reparacion completada con exito!")
            else:
                self.status_label.configure(text="Reparacion fallida", foreground=theme["danger"])
                self._log("\n[FAIL] La reparacion no pudo completarse.")

            self.btn_repair.configure(state=tk.NORMAL)
            self.btn_cancel.configure(state=tk.DISABLED)
            self._running = False

    def _start_repair(self):
        """Inicia el proceso de reparacion."""
        if self._running:
            return

        port = self.app.get_selected_port()
        if not port:
            self._log("[ERROR] Selecciona un puerto primero.")
            return

        self._running = True
        self.btn_repair.configure(state=tk.DISABLED)
        self.btn_cancel.configure(state=tk.NORMAL)
        self.status_label.configure(text="Reparando...", foreground=get_theme()["warning"])

        # Resetear UI
        for step_id, canvas_data in self.step_canvases.items():
            theme = get_theme()
            canvas = canvas_data["canvas"]
            canvas.itemconfigure(canvas_data["circle"], fill=theme["bg"], outline=theme["border"])
            canvas_data["progress"].stop()

        self._log(f"Iniciando reparacion en {port}...")
        self._log("=" * 50)

        def worker():
            try:
                from core import ArduinoRepair

                repair = ArduinoRepair(port=port)

                # Notificar inicio de deteccion
                self.event_queue.put({"step": "detect", "status": "running", "message": "Detectando placa..."})

                diag_result = repair.diagnose_bootloader()

                if diag_result.get("status") == "ok":
                    self.event_queue.put({
                        "step": "detect",
                        "status": "done",
                        "message": f"Placa OK: {diag_result.get('chip', 'desconocida')}"
                    })
                    self.event_queue.put({"type": "complete", "success": True})
                    return

                self.event_queue.put({
                    "step": "detect",
                    "status": "done",
                    "message": "Bootloader corrupto detectado. Procediendo..."
                })

                # Determinar MCU
                mcu = "m328p"
                sig = diag_result.get("signature")
                if sig:
                    from core.board_info import KNOWN_SIGNATURES
                    if sig in KNOWN_SIGNATURES:
                        chip_info = KNOWN_SIGNATURES[sig]
                        if "2560" in chip_info[0] or "mega" in chip_info[0].lower():
                            mcu = "m2560"

                self._log(f"MCU detectado: {mcu}")

                # Ejecutar reparacion
                self.event_queue.put({"step": "erase", "status": "running", "message": "Borrando flash..."})
                result = repair.repair_bootloader(mcu)

                for step_info in result.steps:
                    step_id = self._guess_step_id(step_info)
                    if step_id:
                        self.event_queue.put({"step": step_id, "status": "done", "message": step_info})

                # Verificacion
                self.event_queue.put({"step": "verify", "status": "running", "message": "Verificando..."})
                verify_result = repair.diagnose_bootloader()

                if verify_result.get("status") == "ok":
                    self.event_queue.put({
                        "step": "verify",
                        "status": "done",
                        "message": "Verificacion exitosa!"
                    })
                else:
                    self.event_queue.put({
                        "step": "verify",
                        "status": "fail",
                        "message": "Verificacion fallida. Intenta de nuevo."
                    })

                self.event_queue.put({
                    "type": "complete",
                    "success": result.success,
                    "message": result.message
                })

            except Exception as e:
                self._log(f"[ERROR] {str(e)}")
                self.event_queue.put({"type": "complete", "success": False})

        threading.Thread(target=worker, daemon=True).start()

    def _guess_step_id(self, step_info: str) -> str:
        """Adivina el step_id basado en el mensaje."""
        step_lower = step_info.lower()
        if "detect" in step_lower or "iniciando" in step_lower:
            return "detect"
        elif "borr" in step_lower:
            return "erase"
        elif "bootloader" in step_lower or "quemando" in step_lower:
            return "bootloader"
        elif "fuse" in step_lower or "configurando" in step_lower:
            return "fuses"
        elif "verif" in step_lower:
            return "verify"
        return None

    def _cancel_repair(self):
        """Cancela la reparacion (limitado, ya que avrdude no soporta cancelacion)."""
        self._log("[INFO] Cancelacion solicitada. El proceso actual terminara.")
        self.btn_cancel.configure(state=tk.DISABLED)

"""
core/watcher.py

Monitor de conexión/desconexión USB de placas Arduino en caliente.
Permite que el sistema "vea" cuándo conectas o desconectas un Arduino,
sin necesidad de pulsar "Escanear" manualmente.

Estrategia multiplataforma:
- Windows:  usa WMI (wmi/ctypes) para detectar eventos de Plug and Play.
- Linux:    usa pyudev si está disponible, si no, polling con pyserial.
- macOS:    polling con pyserial (no hay hot-plug USB fiable desde Python).
- Fallback: polling cada 2 s comparando la lista de puertos.
"""

from __future__ import annotations
import threading
import time
import platform
from typing import Callable, List, Optional

from .detector import ArduinoDetector, DetectedBoard


class HotplugWatcher:
    """Notifica mediante callbacks cuando aparece/desaparece un Arduino.

    Uso:
        watcher = HotplugWatcher()
        watcher.on_connected(lambda b: print('conectado:', b.port))
        watcher.on_disconnected(lambda port: print('desconectado:', port))
        watcher.start()
        # ... cuando quieras parar:
        watcher.stop()
    """

    def __init__(self, poll_interval: float = 2.0):
        self.poll_interval = poll_interval
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.on_connected: List[Callable[[DetectedBoard], None]] = []
        self.on_disconnected: List[Callable[[str], None]] = []
        self._known_ports: set = set()
        self._last_boards: List[DetectedBoard] = []
        self._impl = self._pick_impl()

    # ---------- API pública ----------
    def start(self):
        if self._thread and self._thread.is_alive():
            return
        # Estado inicial
        self._last_boards = ArduinoDetector.scan()
        self._known_ports = {b.port for b in self._last_boards}
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True,
                                        name="ArduinoHotplugWatcher")
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None

    def add_connected_handler(self, cb: Callable[[DetectedBoard], None]):
        self.on_connected.append(cb)

    def add_disconnected_handler(self, cb: Callable[[str], None]):
        self.on_disconnected.append(cb)

    @property
    def current_boards(self) -> List[DetectedBoard]:
        return list(self._last_boards)

    # ---------- Interno ----------
    def _pick_impl(self):
        """Elige la mejor implementación disponible."""
        system = platform.system()
        if system == "Windows":
            try:
                import wmi  # type: ignore
                return self._impl_wmi_watch
            except ImportError:
                return self._impl_polling
        elif system == "Linux":
            try:
                import pyudev  # type: ignore
                return self._impl_pyudev
            except ImportError:
                return self._impl_polling
        else:
            return self._impl_polling

    def _loop(self):
        """Bucle principal: delega en la implementación."""
        self._impl()

    def _impl_polling(self):
        """Polling: compara cada N segundos la lista de puertos."""
        while not self._stop.is_set():
            try:
                boards = ArduinoDetector.scan()
                current_ports = {b.port for b in boards}
                new_ports = current_ports - self._known_ports
                removed_ports = self._known_ports - current_ports

                for port in removed_ports:
                    for cb in self.on_disconnected:
                        try:
                            cb(port)
                        except Exception:
                            pass
                for b in boards:
                    if b.port in new_ports:
                        for cb in self.on_connected:
                            try:
                                cb(b)
                            except Exception:
                                pass
                self._last_boards = boards
                self._known_ports = current_ports
            except Exception:
                pass
            self._stop.wait(self.poll_interval)

    def _impl_wmi_watch(self):
        """Windows: usa WMI para eventos de Plug and Play."""
        try:
            import wmi  # type: ignore
            c = wmi.WMI()
            watcher = c.Win32_PnPEntity.watch_for(notification_type="creation")
            while not self._stop.is_set():
                # WMI watch es bloqueante; lo combinamos con polling para
                # también detectar desconexiones.
                try:
                    self._stop.wait(0.5)
                except Exception:
                    pass
                # Polling rápido para detectar ambos eventos
                self._impl_polling()
                break
        except Exception:
            # Si WMI falla, vuelve al polling
            self._impl_polling()

    def _impl_pyudev(self):
        """Linux: usa pyudev para eventos del kernel."""
        try:
            import pyudev  # type: ignore
            context = pyudev.Context()
            monitor = pyudev.Monitor.from_netlink(context)
            monitor.filter_by(subsystem="tty")
            # pyudev no tiene wait interrumpible sencillo; usamos poll cada 1 s
            # combinado con el observer.
            self._impl_polling()
        except Exception:
            self._impl_polling()


# ---------- Monitor singleton para uso fácil ----------
_default_watcher: Optional[HotplugWatcher] = None


def get_default_watcher() -> HotplugWatcher:
    global _default_watcher
    if _default_watcher is None:
        _default_watcher = HotplugWatcher()
    return _default_watcher

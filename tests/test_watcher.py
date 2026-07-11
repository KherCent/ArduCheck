"""
Test rápido del watcher (no requiere Arduino).
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.watcher import HotplugWatcher


def test_watcher_lifecycle():
    """Crea un watcher, lo arranca, espera un poco y lo para."""
    connected = []
    disconnected = []

    w = HotplugWatcher(poll_interval=0.5)
    w.add_connected_handler(lambda b: connected.append(b.port))
    w.add_disconnected_handler(lambda p: disconnected.append(p))

    w.start()
    print("[OK] watcher.start() no crash")
    time.sleep(2)
    boards = w.current_boards
    print(f"[OK] current_boards count={len(boards)}")
    for b in boards:
        print(f"     - {b.port} {b.guessed_name}")
    w.stop()
    print("[OK] watcher.stop() sin colgar")
    print(f"     eventos conectados={len(connected)} desconectados={len(disconnected)}")


if __name__ == "__main__":
    test_watcher_lifecycle()
    print("\n[PASS] Watcher OK.")

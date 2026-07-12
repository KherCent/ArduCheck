"""
tests/test_repair.py — Tests para el módulo de reparación
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.repair import (
    ArduinoRepair,
    RepairResult,
    DEFAULT_FUSES_328P,
    DEFAULT_FUSES_2560,
)


class TestRepairModule(unittest.TestCase):
    """Tests del módulo de reparación."""

    def test_repair_result_dataclass(self):
        """Verifica que RepairResult sea un dataclass válido."""
        result = RepairResult(
            success=False,
            message="Test message",
            steps=["step1", "step2"],
            score_before=0,
            score_after=50,
        )
        self.assertFalse(result.success)
        self.assertEqual(result.message, "Test message")
        self.assertEqual(len(result.steps), 2)
        self.assertEqual(result.score_before, 0)
        self.assertEqual(result.score_after, 50)

    def test_default_fuses_328p(self):
        """Verifica los fuses por defecto para ATmega328P."""
        self.assertIn("lfuse", DEFAULT_FUSES_328P)
        self.assertIn("hfuse", DEFAULT_FUSES_328P)
        self.assertIn("efuse", DEFAULT_FUSES_328P)
        self.assertEqual(DEFAULT_FUSES_328P["lfuse"], 0xFF)
        self.assertEqual(DEFAULT_FUSES_328P["hfuse"], 0xD9)
        self.assertEqual(DEFAULT_FUSES_328P["efuse"], 0xFD)

    def test_default_fuses_2560(self):
        """Verifica los fuses por defecto para ATmega2560."""
        self.assertIn("lfuse", DEFAULT_FUSES_2560)
        self.assertIn("hfuse", DEFAULT_FUSES_2560)
        self.assertIn("efuse", DEFAULT_FUSES_2560)
        self.assertEqual(DEFAULT_FUSES_2560["lfuse"], 0xFF)
        self.assertEqual(DEFAULT_FUSES_2560["hfuse"], 0xD8)
        self.assertEqual(DEFAULT_FUSES_2560["efuse"], 0xFD)

    def test_arduino_repair_init(self):
        """Verifica que ArduinoRepair se inicializa correctamente."""
        repair = ArduinoRepair("COM3", 115200)
        self.assertEqual(repair.port, "COM3")
        self.assertEqual(repair.baud, 115200)
        self.assertIsInstance(repair.steps, list)
        self.assertEqual(len(repair.steps), 0)

    def test_optiboot_path_returns_none_or_str(self):
        """Verifica que _get_optiboot_path devuelve un path válido o None."""
        repair = ArduinoRepair("COM3")
        result = repair._get_optiboot_path()
        # Puede ser None si no hay avrdude instalado, o una ruta válida
        self.assertTrue(result is None or isinstance(result, str))

    def test_mega_bootloader_path_returns_none_or_str(self):
        """Verifica que _get_mega_bootloader_path devuelve un path válido o None."""
        repair = ArduinoRepair("COM3")
        result = repair._get_mega_bootloader_path()
        # Puede ser None si no hay avrdude instalado, o una ruta válida
        self.assertTrue(result is None or isinstance(result, str))

    def test_run_avrdude_without_avrdude(self):
        """Verifica el manejo de error cuando avrdude no está disponible."""
        repair = ArduinoRepair("COM3")
        # Simular que no hay avrdude
        repair.avrdude = None
        code, out, err = repair._run_avrdude(["-v"])
        self.assertEqual(code, -1)
        self.assertEqual(out, "")
        self.assertIn("no encontrado", err)


if __name__ == "__main__":
    unittest.main()

"""
tests/test_smoke.py

Tests rápidos de humo (smoke) que no requieren Arduino conectado.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.parser import DiagnosticParser
from core.detector import ArduinoDetector
from core.runner import ArduinoDiagnostic


def test_parser_basic():
    p = DiagnosticParser()
    p.feed("# comentario")
    p.feed("$ID,Uno,ATmega328P")
    p.feed("$VCC,5012")
    p.feed("$LED,1")
    p.feed("$DIGPIN,2,1")
    p.feed("$DIGPIN,3,0")
    p.feed("$DIGLOW,2,0")
    p.feed("$ADC,0,512")
    p.feed("$EEPROM,0,1")
    p.feed("$EEPOK,1")
    p.feed("$RAM,1500")
    p.feed("$FLASH,32768")
    p.feed("$SPI,1")
    p.feed("$CLK,1000,1002")
    p.feed("$DONE,0")
    r = p.report
    assert r.board == "Uno"
    assert r.chip == "ATmega328P"
    assert r.vcc_mv == 5012
    assert r.led_ok is True
    assert r.digital_results[2] is True
    assert r.digital_results[3] is False
    assert 3 in r.digital_failures
    assert r.adc_results[0] == 512
    assert r.eeprom_ok is True
    assert r.ram_free == 1500
    assert r.flash_size == 32768
    assert r.spi_ok is True
    assert r.clock_drift_ms == 2
    assert r.done_code == 0
    assert r.done is True
    print("[OK] test_parser_basic")


def test_parser_done():
    p = DiagnosticParser()
    p.feed("$DONE,0")
    assert p.report.done is True
    assert p.report.done_code == 0
    print("[OK] test_parser_done")


def test_runner_good_path():
    diag = ArduinoDiagnostic(port="COM_FAKE", baud=115200, timeout=0.5)
    # Simulamos líneas sin tener placa real
    diag.parser.feed("$ID,Uno,ATmega328P")
    diag.parser.feed("$VCC,5050")
    diag.parser.feed("$LED,1")
    for i in range(2, 14):
        diag.parser.feed(f"$DIGPIN,{i},1")
        diag.parser.feed(f"$DIGLOW,{i},0")
    diag.parser.feed("$EEPOK,1")
    diag.parser.feed("$RAM,1500")
    diag.parser.feed("$SPI,1")
    diag.parser.feed("$CLK,1000,1000")
    diag.parser.feed("$DONE,0")
    # Forzamos veredicto
    result = diag._build_verdict()
    assert result.verdict in ("GOOD", "WARN", "FAIL")
    assert result.score >= 0
    assert result.board == "Uno"
    print(f"[OK] test_runner_good_path  verdict={result.verdict} score={result.score}")


def test_runner_fail_path():
    diag = ArduinoDiagnostic(port="COM_FAKE", baud=115200, timeout=0.5)
    diag.parser.feed("$VCC,3500")  # voltaje critico
    diag.parser.feed("$EEPOK,0")   # EEPROM mala
    diag.parser.feed("$DONE,1")
    result = diag._build_verdict()
    assert result.verdict == "FAIL"
    assert result.score < 100
    print(f"[OK] test_runner_fail_path  verdict={result.verdict} score={result.score}")


def test_detector_no_crash():
    boards = ArduinoDetector.scan()
    assert isinstance(boards, list)
    print(f"[OK] test_detector_no_crash  found={len(boards)} ports")


if __name__ == "__main__":
    print("=== ArduCheck - Tests de humo ===\n")
    test_parser_basic()
    test_parser_done()
    test_runner_good_path()
    test_runner_fail_path()
    test_detector_no_crash()
    print("\n[PASS] Todos los tests pasaron.")

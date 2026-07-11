"""
core/parser.py

Parsea la salida del sketch de diagnóstico.
Cada línea tiene formato:  $TAG,v1,v2
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Generator


@dataclass
class TestRecord:
    tag: str
    values: list = field(default_factory=list)

    def get(self, idx: int, default=None):
        return self.values[idx] if 0 <= idx < len(self.values) else default


@dataclass
class DiagnosticReport:
    board: str = ""
    chip: str = ""
    vcc_mv: int = 0
    led_ok: bool = False
    digital_failures: List[int] = field(default_factory=list)
    digital_results: Dict[int, bool] = field(default_factory=dict)
    adc_results: Dict[int, int] = field(default_factory=dict)
    pwm_results: Dict[int, int] = field(default_factory=dict)
    eeprom_ok: bool = False
    ram_free: int = 0
    flash_size: int = 0
    i2c_devices: List[int] = field(default_factory=list)
    spi_ok: bool = False
    clock_drift_ms: int = 0
    done_code: int = -1
    raw_lines: List[str] = field(default_factory=list)

    @property
    def done(self) -> bool:
        return self.done_code >= 0


class DiagnosticParser:
    """Parser en streaming de las líneas que emite el sketch."""

    def __init__(self):
        self.report = DiagnosticReport()

    def feed(self, line: str) -> Optional[TestRecord]:
        line = line.strip()
        if not line:
            return None
        self.report.raw_lines.append(line)
        if not line.startswith("$"):
            return None
        parts = line[1:].split(",")
        tag = parts[0]
        try:
            values = [int(p) for p in parts[1:]]
        except ValueError:
            values = [p for p in parts[1:]]
        rec = TestRecord(tag=tag, values=values)
        self._apply(rec)
        return rec

    def feed_many(self, lines: List[str]):
        for l in lines:
            self.feed(l)

    def _apply(self, rec: TestRecord):
        t = rec.tag
        v = rec.values
        if t == "ID" and len(v) >= 2:
            self.report.board = str(v[0])
            self.report.chip = str(v[1])
        elif t == "VCC" and v:
            self.report.vcc_mv = int(v[0])
        elif t == "LED" and v:
            self.report.led_ok = bool(int(v[0]))
        elif t == "DIGPIN" and len(v) >= 2:
            pin, hi = int(v[0]), int(v[1])
            self.report.digital_results[pin] = (hi == 1)
            if hi != 1:
                self.report.digital_failures.append(pin)
        elif t == "DIGFAIL" and v:
            n = int(v[0])
            # se complementa con la lista
        elif t == "ADC" and len(v) >= 2:
            self.report.adc_results[int(v[0])] = int(v[1])
        elif t == "PWM" and len(v) >= 3:
            self.report.pwm_results[int(v[0])] = int(v[2])
        elif t == "EEPOK" and v:
            self.report.eeprom_ok = bool(int(v[0]))
        elif t == "RAM" and v:
            self.report.ram_free = int(v[0])
        elif t == "FLASH" and v:
            self.report.flash_size = int(v[0])
        elif t == "I2C" and len(v) >= 2:
            if int(v[1]) == 1:
                self.report.i2c_devices.append(int(v[0]))
        elif t == "SPI" and v:
            self.report.spi_ok = bool(int(v[0]))
        elif t == "CLK" and len(v) >= 2:
            self.report.clock_drift_ms = int(v[1]) - 1000
        elif t == "DONE" and v:
            self.report.done_code = int(v[0])

    def lines(self) -> Generator[str, None, None]:
        yield from self.report.raw_lines

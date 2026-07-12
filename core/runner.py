"""
core/runner.py

Coordinador del diagnóstico completo.
Abre el puerto, ejecuta el sketch de auto-test, parsea resultados
y emite un veredicto.

Multiplataforma: usa platform_utils para encontrar avrdude
y maneja excepciones del puerto serial de forma robusta.
"""

from __future__ import annotations
import time
import serial
from dataclasses import dataclass, field
from typing import List, Optional

from .parser import DiagnosticParser, DiagnosticReport
from .platform_utils import get_avrdude_path, is_unix, require_dialout_membership
from .board_info import _avrdude_conf, KNOWN_SIGNATURES


# Umbrales
VCC_MIN_OK = 4500      # mV
VCC_MIN_WARN = 4000    # mV
RAM_MIN_UNO = 200      # bytes libres mínimos esperados
RAM_MIN_MEGA = 500
CLOCK_TOLERANCE = 50   # ms de desviación admisible en 1 segundo


@dataclass
class DiagnosticResult:
    port: str
    board: str
    chip: str
    verdict: str             # "GOOD" | "WARN" | "FAIL"
    score: int               # 0..100
    summary: str
    details: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    report: Optional[DiagnosticReport] = None

    def to_dict(self):
        return {
            "port": self.port,
            "board": self.board,
            "chip": self.chip,
            "verdict": self.verdict,
            "score": self.score,
            "summary": self.summary,
            "details": self.details,
            "warnings": self.warnings,
            "errors": self.errors,
        }


class ArduinoDiagnostic:
    """Ejecuta el diagnóstico completo sobre un puerto."""

    def __init__(self, port: str, baud: int = 115200, timeout: float = 60.0):
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.parser = DiagnosticParser()

    def run_full_diagnostic(self) -> DiagnosticResult:
        """Abre el puerto, lee la salida del sketch y devuelve el veredicto."""
        self._bootloader_check_done = False
        self._bootloader_error = ""
        self._disconnect_error = ""
        
        # 0) Verificar bootloader ANTES de tests por Serial
        # Usa get_avrdude_path() multiplataforma de platform_utils
        avrdude = get_avrdude_path()
        if avrdude:
            conf = _avrdude_conf()
            import subprocess
            for mcu in ["m328p", "m2560"]:
                cmd = [avrdude]
                if conf:
                    cmd.extend(["-C", conf])
                cmd.extend(["-v", "-c", "arduino", "-p", mcu, "-P", self.port, "-b", str(self.baud), "-D"])
                try:
                    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
                    output = r.stdout + r.stderr
                    if "signature" in output.lower() and "0x1e" in output:
                        # Extraer firma
                        for line in output.split('\n'):
                            line = line.strip()
                            if len(line) == 6 and all(c in "0123456789abcdefABCDEF" for c in line):
                                try:
                                    sig = tuple(int(line[i:i+2], 16) for i in (0, 2, 4))
                                    if sig in KNOWN_SIGNATURES:
                                        chip, arch, fl, ram, eep = KNOWN_SIGNATURES[sig]
                                        self.parser.report.chip = chip
                                        break
                                except Exception:
                                    pass
                        self._bootloader_check_done = True
                        break
                    elif "not in sync" in output.lower() or "resp=0x00" in output:
                        self._bootloader_error = f"Bootloader corrupto/ausente (MCU {mcu})"
                        self._bootloader_check_done = True
                        break
                except subprocess.TimeoutExpired:
                    self._bootloader_error = "Timeout en verificacion bootloader"
                    break
                except Exception:
                    break
        
        # 1) Abrir puerto y leer datos del sketch
        try:
            with serial.Serial(self.port, self.baud, timeout=2) as ser:
                # Reset por DTR (algunos clones CH340 lo ignoran)
                try:
                    ser.setDTR(False)
                    time.sleep(0.1)
                    ser.setDTR(True)
                    time.sleep(0.1)
                    ser.reset_input_buffer()
                except Exception:
                    pass

                start = time.time()
                while time.time() - start < self.timeout:
                    # Capturar desconexiones abruptas durante la lectura
                    try:
                        line = ser.readline().decode("utf-8", errors="ignore")
                    except (OSError, serial.SerialException, AttributeError) as e:
                        # La placa se desconectó durante el test
                        self._disconnect_error = (
                            f"La placa se desconectó durante el diagnóstico: {e}"
                        )
                        break
                    if not line:
                        continue
                    self.parser.feed(line)
                    if self.parser.report.done:
                        break
        except serial.SerialException as e:
            err_str = str(e).lower()
            # Mejorar mensaje para errores de permisos en Unix
            if "permission" in err_str or "acceso denegado" in err_str:
                if is_unix():
                    dialout_ok, dialout_hint = require_dialout_membership()
                    if not dialout_ok:
                        return DiagnosticResult(
                            port=self.port, board="?", chip="?",
                            verdict="FAIL", score=0,
                            summary=f"Sin permisos para abrir {self.port}.\n{dialout_hint}",
                            errors=[f"Permission denied en {self.port}", dialout_hint],
                        )
            return DiagnosticResult(
                port=self.port, board="?", chip="?",
                verdict="FAIL", score=0,
                summary=f"No se pudo abrir {self.port}: {e}",
                errors=[str(e)],
            )
        except OSError as e:
            return DiagnosticResult(
                port=self.port, board="?", chip="?",
                verdict="FAIL", score=0,
                summary=f"Error del sistema al abrir {self.port}: {e}",
                errors=[str(e)],
            )

        # 2) Si hubo desconexión durante el test
        if self._disconnect_error:
            return DiagnosticResult(
                port=self.port,
                board=self.parser.report.board or "?",
                chip=self.parser.report.chip or "?",
                verdict="FAIL",
                score=0,
                summary=self._disconnect_error,
                errors=[self._disconnect_error],
                report=self.parser.report,
            )

        return self._build_verdict()

    def feed_existing_lines(self, lines: List[str]) -> DiagnosticResult:
        """Útil cuando se lee desde otro proceso (p.ej. arduino-cli monitor)."""
        for l in lines:
            self.parser.feed(l)
        return self._build_verdict()

    # ---------- veredicto ----------
    def _build_verdict(self) -> DiagnosticResult:
        r = self.parser.report
        result = DiagnosticResult(
            port=self.port,
            board=r.board or "?",
            chip=r.chip or "?",
            verdict="GOOD",
            score=100,
            summary="",
            report=r,
        )

        # 0) Veredicto de bootloader (si se detecto error)
        if getattr(self, '_bootloader_check_done', False) and getattr(self, '_bootloader_error', ''):
            result.errors.append(self._bootloader_error)
            result.verdict = "FAIL"
            result.score = 0
            result.summary = f"[FAIL] FAIL - ? (?) score=0/100"
            return result

        # 1) Voltaje
        if r.vcc_mv:
            result.details.append(f"Voltaje de alimentación: {r.vcc_mv/100:.2f} V")
            if r.vcc_mv < VCC_MIN_WARN:
                result.errors.append(f"Voltaje crítico: {r.vcc_mv/100:.2f} V")
                result.verdict = "FAIL"
                result.score -= 40
            elif r.vcc_mv < VCC_MIN_OK:
                result.warnings.append(
                    f"Voltaje bajo: {r.vcc_mv/100:.2f} V (< {VCC_MIN_OK/100:.1f} V)"
                )
                if result.verdict == "GOOD":
                    result.verdict = "WARN"
                result.score -= 15

        # 2) LED
        if r.led_ok:
            result.details.append("LED integrado (pin 13): OK")
        else:
            result.warnings.append("LED pin 13 no responde (puede estar quemado o la placa no tiene)")
            if result.verdict == "GOOD":
                result.verdict = "WARN"
            result.score -= 10

        # 3) Pines digitales
        if r.digital_results:
            total = len(r.digital_results)
            ok = sum(1 for v in r.digital_results.values() if v)
            result.details.append(f"Pines digitales: {ok}/{total} OK")
            if ok != total:
                pins_bad = [p for p, ok in r.digital_results.items() if not ok]
                msg = f"Pines digitales quemados: {pins_bad}"
                result.warnings.append(msg)
                # Solo 1 pin malo = WARN; varios = FAIL
                if len(pins_bad) > 2:
                    result.verdict = "FAIL"
                elif result.verdict == "GOOD":
                    result.verdict = "WARN"
                result.score -= 10 * len(pins_bad)

        # 4) ADC
        if r.adc_results:
            errores_adc = [p for p, v in r.adc_results.items() if v == 0 or v == 1023]
            if errores_adc:
                result.warnings.append(f"ADC con lecturas fijas en {errores_adc}")
                if result.verdict == "GOOD":
                    result.verdict = "WARN"
                result.score -= 5 * len(errores_adc)
            else:
                result.details.append(f"ADC: {len(r.adc_results)} canales leídos OK")

        # 5) EEPROM
        if r.eeprom_ok:
            result.details.append("EEPROM: OK")
        elif r.done:
            result.errors.append("EEPROM: fallo en la verificación")
            result.verdict = "FAIL"
            result.score -= 30

        # 6) RAM
        if r.ram_free:
            result.details.append(f"RAM libre: {r.ram_free} bytes")
            min_ram = RAM_MIN_MEGA if "Mega" in r.board or "mega" in r.board.lower() else RAM_MIN_UNO
            if r.ram_free < min_ram:
                result.warnings.append(f"RAM libre baja ({r.ram_free} B)")
                if result.verdict == "GOOD":
                    result.verdict = "WARN"
                result.score -= 10

        # 7) I2C
        result.details.append(f"I2C dispositivos encontrados: {len(r.i2c_devices)} {r.i2c_devices or ''}")

        # 8) SPI
        if r.spi_ok:
            result.details.append("SPI: SCK responde OK")
        else:
            result.warnings.append("SPI: línea SCK no responde")

        # 9) Reloj
        if r.clock_drift_ms:
            drift = abs(r.clock_drift_ms)
            if drift > CLOCK_TOLERANCE:
                result.warnings.append(f"Reloj con deriva de {drift} ms/s")
                if result.verdict == "GOOD":
                    result.verdict = "WARN"
                result.score -= 5

        # Score final
        result.score = max(0, result.score)
        emoji = {"GOOD": "[OK]", "WARN": "[WARN]", "FAIL": "[FAIL]"}.get(result.verdict, "?")
        result.summary = f"{emoji} {result.verdict} - {r.board or '?'} ({r.chip or '?'}) score={result.score}/100"

        return result

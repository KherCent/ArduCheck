"""
core/repair.py — Módulo de reparación de placas Arduino

Coordina las reparaciones automáticas según el diagnóstico.
"""

from __future__ import annotations
import subprocess
import shutil
import os
from dataclasses import dataclass
from typing import Optional, List, Tuple

from .board_info import _find_avrdude, _avrdude_conf, KNOWN_SIGNATURES


# Fuses por defecto para ATmega328P (Arduino Uno)
DEFAULT_FUSES_328P = {
    "lfuse": 0xFF,
    "hfuse": 0xD9,
    "efuse": 0xFD,
    "lock": 0xCF,
}

# Fuses por defecto para ATmega2560 (Arduino Mega)
DEFAULT_FUSES_2560 = {
    "lfuse": 0xFF,
    "hfuse": 0xD8,
    "efuse": 0xFD,
    "lock": 0xCF,
}


@dataclass
class RepairResult:
    success: bool
    message: str
    steps: List[str]
    score_before: int
    score_after: int


class ArduinoRepair:
    """Coordina reparaciones automáticas de placas Arduino."""

    def __init__(self, port: str, baud: int = 115200):
        self.port = port
        self.baud = baud
        self.avrdude = _find_avrdude()
        self.conf = _avrdude_conf() if self.avrdude else None
        self.steps: List[str] = []

    def _run_avrdude(self, extra_args: List[str], timeout: int = 60) -> Tuple[int, str, str]:
        """Ejecuta avrdude con argumentos dados."""
        if not self.avrdude:
            return -1, "", "avrdude no encontrado"
        cmd = [self.avrdude]
        if self.conf:
            cmd.extend(["-C", self.conf])
        cmd.extend(extra_args)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return r.returncode, r.stdout, r.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "timeout"
        except Exception as e:
            return -1, "", str(e)

    def diagnose_bootloader(self) -> dict:
        """Diagnostica el estado del bootloader."""
        result = {"status": "unknown", "signature": None, "fuses": {}, "errors": []}
        
        # Probar con m328p primero
        for mcu in ["m328p", "m2560"]:
            code, out, err = self._run_avrdude([
                "-v", "-c", "arduino", "-p", mcu,
                "-P", self.port, "-b", str(self.baud), "-D"
            ], timeout=20)
            output = out + err
            
            if "signature" in output.lower() and "0x1e" in output:
                # Extraer firma
                for line in output.split('\n'):
                    line = line.strip()
                    if len(line) == 6 and all(c in "0123456789abcdefABCDEF" for c in line):
                        sig = tuple(int(line[i:i+2], 16) for i in (0, 2, 4))
                        result["signature"] = sig
                        if sig in KNOWN_SIGNATURES:
                            chip, arch, fl, ram, eep = KNOWN_SIGNATURES[sig]
                            result["chip"] = chip
                        break
                
                # Extraer fuses si disponibles
                fuses = {}
                for line in output.split('\n'):
                    if 'lfuse' in line.lower() or 'hfuse' in line.lower():
                        for part in line.split():
                            if ':' in part:
                                k, v = part.split(':', 1)
                                try:
                                    fuses[k.strip().lower()] = int(v.strip(), 16)
                                except:
                                    pass
                if fuses:
                    result["fuses"] = fuses
                
                result["status"] = "ok"
                return result
                
            elif "not in sync" in output.lower() or "resp=0x00" in output:
                result["errors"].append(f"Bootloader no responde (MCU: {mcu})")
        
        if result["errors"]:
            result["status"] = "corrupted"
        
        return result

    def repair_bootloader(self, mcu: str = "m328p") -> RepairResult:
        """Repara el bootloader usando avrdude."""
        self.steps = []
        result = RepairResult(
            success=False,
            message="",
            steps=[],
            score_before=0,
            score_after=0
        )
        
        if not self.avrdude:
            result.message = "avrdude no disponible"
            return result
        
        self.steps.append(f"Iniciando reparación de bootloader para {mcu}")
        
        # Paso 1: Detectar el chip primero
        diag = self.diagnose_bootloader()
        if diag["status"] == "ok":
            result.message = "Bootloader ya funciona correctamente"
            result.success = True
            result.steps = self.steps
            result.score_after = 100
            return result
        
        # Paso 2: Chip responde?
        if diag["status"] == "unknown" and not diag["errors"]:
            result.message = "No se detectó chip. Verifica la conexión."
            result.steps = self.steps
            return result
        
        # Paso 3: Chip responde pero bootloader corrupto → quemar
        self.steps.append("Detectado: bootloader corrupto. Procediendo a quemar nuevo bootloader...")
        
        # Determinar el archivo de bootloader según el MCU
        bootloader_files = {
            "m328p": self._get_optiboot_path(),
            "m2560": self._get_mega_bootloader_path(),
        }
        
        boot_file = bootloader_files.get(mcu)
        if not boot_file or not os.path.exists(boot_file):
            result.message = f"Bootloader para {mcu} no encontrado"
            result.steps = self.steps
            return result
        
        self.steps.append(f"Bootloader: {os.path.basename(boot_file)}")
        
        # Paso 4: Quemar con -e (erase) primero
        self.steps.append("Borrando flash...")
        code, out, err = self._run_avrdude([
            "-c", "arduino", "-p", mcu,
            "-P", self.port, "-b", str(self.baud), "-e"
        ], timeout=30)
        
        if code != 0:
            result.message = f"Error al borrar: {err[:200]}"
            result.steps = self.steps
            return result
        
        self.steps.append("Flash borrada OK")
        
        # Paso 5: Quemar bootloader
        self.steps.append("Quemando bootloader...")
        code, out, err = self._run_avrdude([
            "-c", "arduino", "-p", mcu,
            "-P", self.port, "-b", str(self.baud),
            "-U", f"flash:w:{boot_file}:i"
        ], timeout=60)
        
        if code != 0:
            result.message = f"Error al quemar bootloader: {err[:200]}"
            result.steps = self.steps
            return result
        
        self.steps.append("Bootloader quemado OK")
        
        # Paso 6: Quemar fuses
        self.steps.append("Configurando fuses...")
        default_fuses = DEFAULT_FUSES_328P if mcu == "m328p" else DEFAULT_FUSES_2560
        fuse_args = []
        for name, value in default_fuses.items():
            fuse_args.extend(["-U", f"{name}:w:{value:#04x}:m"])
        
        code, out, err = self._run_avrdude([
            "-c", "arduino", "-p", mcu,
            "-P", self.port, "-b", str(self.baud)
        ] + fuse_args, timeout=30)
        
        if code == 0:
            self.steps.append("Fuses configurados OK")
        
        # Paso 7: Verificar
        self.steps.append("Verificando reparación...")
        diag2 = self.diagnose_bootloader()
        
        if diag2["status"] == "ok":
            result.success = True
            result.message = f"Bootloader reparado exitosamente para {mcu}"
            result.score_after = 100
        else:
            result.message = "Reparación completó pero no se pudo verificar"
            result.score_after = 50
        
        result.steps = self.steps
        return result

    def _get_optiboot_path(self) -> Optional[str]:
        """Busca el archivo Optiboot.hex."""
        # Buscar en Arduino CLI
        search_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Arduino CLI", "packages", "arduino", "hardware", "avr", "1.8.8", "bootloaders", "optiboot", "optiboot_atmega328.hex"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Arduino15", "packages", "arduino", "hardware", "avr", "1.8.8", "bootloaders", "optiboot", "optiboot_atmega328.hex"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Arduino", "hardware", "arduino", "avr", "bootloaders", "optiboot", "optiboot_atmega328.hex"),
            # Incluir en el proyecto
            os.path.join(os.path.dirname(__file__), "..", "firmware", "bootloaders", "optiboot_atmega328.hex"),
        ]
        for p in search_paths:
            if os.path.exists(p):
                return p
        return None

    def _get_mega_bootloader_path(self) -> Optional[str]:
        """Busca el bootloader para Mega 2560."""
        search_paths = [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Arduino CLI", "packages", "arduino", "hardware", "avr", "1.8.8", "bootloaders", "stk500v2", "stk500boot_v2_mega2560.hex"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Arduino15", "packages", "arduino", "hardware", "avr", "1.8.8", "bootloaders", "stk500v2", "stk500boot_v2_mega2560.hex"),
            os.path.join(os.path.dirname(__file__), "..", "firmware", "bootloaders", "stk500boot_v2_mega2560.hex"),
        ]
        for p in search_paths:
            if os.path.exists(p):
                return p
        return None

    def auto_repair(self) -> RepairResult:
        """Intenta reparar automáticamente detectando el chip."""
        self.steps = []
        result = RepairResult(
            success=False,
            message="",
            steps=[],
            score_before=0,
            score_after=0
        )
        
        # Primero diagnosticar
        diag = self.diagnose_bootloader()
        
        if diag["status"] == "ok":
            result.success = True
            result.message = "Placa funcionando correctamente"
            result.score_after = 100
            result.steps = ["Diagnóstico: Bootloader OK"]
            return result
        
        # Determinar MCU
        mcu = "m328p"
        if diag.get("signature"):
            sig = diag["signature"]
            if sig in KNOWN_SIGNATURES:
                chip, arch, fl, ram, eep = KNOWN_SIGNATURES[sig]
                if "2560" in chip or "mega" in chip.lower():
                    mcu = "m2560"
        
        self.steps.append(f"MCU detectado: {mcu}")
        
        # Reparar
        repair_result = self.repair_bootloader(mcu)
        return repair_result


def repair_port(port: str, baud: int = 115200) -> RepairResult:
    """Función de conveniencia para reparar un puerto."""
    repair = ArduinoRepair(port, baud)
    return repair.auto_repair()

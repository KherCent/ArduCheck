"""Verificacion de bootloader usando avrdude."""
import subprocess
import shutil
import os

def check_bootloader(port, board_fqbn="arduino:avr:uno", timeout=15):
    """Verifica si el bootloader responde correctamente."""
    avrdude = shutil.which("avrdude") or os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "Arduino15", "packages", "arduino", "tools", "avrdude", "8.0.0-arduino1", "bin", "avrdude.exe"
    )
    
    if not os.path.exists(avrdude):
        return {"ok": None, "error": "avrdude no encontrado", "score": 0}
    
    conf = os.path.join(os.path.dirname(avrdude), "..", "etc", "avrdude.conf")
    if not os.path.exists(conf):
        conf = os.path.join(os.path.dirname(avrdude), "..", "..", "etc", "avrdude.conf")
    
    mcu = "atmega328p" if "328" in board_fqbn else "atmega2560"
    
    cmd = [avrdude, "-C" + conf, "-v", "-p" + mcu, "-carduino", "-P" + port, "-b115200", "-D"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output = result.stdout + result.stderr
        
        if "signature" in output.lower() and "0x1e" in output:
            sig_line = [l for l in output.split('\n') if '0x1e' in l]
            if sig_line:
                return {"ok": True, "signature": sig_line[0].strip(), "score": 10}
        elif "not in sync" in output.lower() or "resp=0x00" in output:
            return {"ok": False, "error": "Bootloader corrupto o ausente", "score": -10}
        else:
            return {"ok": None, "error": "Respuesta inesperada", "score": 0}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "Timeout", "score": -10}
    except Exception as e:
        return {"ok": None, "error": str(e), "score": 0}

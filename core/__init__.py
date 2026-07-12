"""
core/__init__.py — Arduino Diagnostic Core
"""

from .detector import ArduinoDetector, DetectedBoard
from .board_info import BoardInfo
from .runner import ArduinoDiagnostic, DiagnosticResult
from .repair import ArduinoRepair, RepairResult, repair_port
from .watcher import get_default_watcher
from .flasher import upload_sketch, is_flasher_available
from .platform_utils import (
    find_tool,
    get_arduino_cli_path,
    get_avrdude_path,
    get_esptool_path,
    get_picotool_path,
    get_bossac_path,
    require_dialout_membership,
    check_port_permissions,
    get_serial_port_prefix,
    get_system,
    is_windows,
    is_unix,
)

__all__ = [
    "ArduinoDetector",
    "DetectedBoard",
    "BoardInfo",
    "ArduinoDiagnostic",
    "DiagnosticResult",
    "ArduinoRepair",
    "RepairResult",
    "repair_port",
    "get_default_watcher",
    "upload_sketch",
    "is_flasher_available",
    # platform_utils
    "find_tool",
    "get_arduino_cli_path",
    "get_avrdude_path",
    "get_esptool_path",
    "get_picotool_path",
    "get_bossac_path",
    "require_dialout_membership",
    "check_port_permissions",
    "get_serial_port_prefix",
    "get_system",
    "is_windows",
    "is_unix",
]

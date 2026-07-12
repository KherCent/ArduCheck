"""
gui/theme/__init__.py — Sistema de temas para ArduCheck
"""

# Paleta clara
LIGHT_THEME = {
    "bg": "#f0f0f0",
    "fg": "#1e1e1e",
    "accent": "#0078d4",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "card_bg": "#ffffff",
    "border": "#cccccc",
    "hover": "#e0e0e0",
}

# Paleta oscura
DARK_THEME = {
    "bg": "#1e1e1e",
    "fg": "#e0e0e0",
    "accent": "#4da6ff",
    "success": "#3cff3c",
    "warning": "#ffd700",
    "danger": "#ff4444",
    "card_bg": "#2d2d2d",
    "border": "#444444",
    "hover": "#3a3a3a",
}

_current_theme = LIGHT_THEME

def get_theme():
    """Retorna el tema actual."""
    return _current_theme

def set_theme(name: str):
    """Establece el tema: 'light' o 'dark'."""
    global _current_theme
    if name == "dark":
        _current_theme = DARK_THEME
    else:
        _current_theme = LIGHT_THEME
    return _current_theme

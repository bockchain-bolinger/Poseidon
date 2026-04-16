import os

# ========== Farbdefinitionen ==========
# Hellmodus (Standard)
LIGHT_FG = {
    'BLACK': '\033[30m',
    'RED': '\033[31m',
    'GREEN': '\033[32m',
    'YELLOW': '\033[33m',
    'BLUE': '\033[34m',
    'MAGENTA': '\033[35m',
    'CYAN': '\033[36m',
    'WHITE': '\033[37m',
    'RESET': '\033[39m',
}
LIGHT_BG = {
    'BLACK': '\033[40m',
    'RED': '\033[41m',
    'GREEN': '\033[42m',
    'YELLOW': '\033[43m',
    'BLUE': '\033[44m',
    'MAGENTA': '\033[45m',
    'CYAN': '\033[46m',
    'WHITE': '\033[47m',
    'RESET': '\033[49m',
}

# Dunkelmodus
DARK_FG = {
    'BLACK': '\033[90m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'MAGENTA': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
    'RESET': '\033[39m',
}
DARK_BG = {
    'BLACK': '\033[100m',
    'RED': '\033[101m',
    'GREEN': '\033[102m',
    'YELLOW': '\033[103m',
    'BLUE': '\033[104m',
    'MAGENTA': '\033[105m',
    'CYAN': '\033[106m',
    'WHITE': '\033[107m',
    'RESET': '\033[49m',
}

STYLE = {
    'BRIGHT': '\033[1m',
    'DIM': '\033[2m',
    'NORMAL': '\033[22m',
    'RESET': '\033[0m',
}

# Aktive Zuordnung (wird bei Theme-Wechsel geändert)
_active_fg = LIGHT_FG
_active_bg = LIGHT_BG

# ========== Klassen für den Import ==========
class fg:
    pass
class bg:
    pass
class style:
    pass

def _update_classes():
    """Aktualisiert die Klassenattribute mit den aktuellen Farben."""
    for name, code in _active_fg.items():
        setattr(fg, name, code)
    for name, code in _active_bg.items():
        setattr(bg, name, code)
    for name, code in STYLE.items():
        setattr(style, name, code)

def set_theme(theme_name):
    """Wechselt das Farbschema (light/dark)."""
    global _active_fg, _active_bg
    if theme_name == 'dark':
        _active_fg = DARK_FG
        _active_bg = DARK_BG
    else:
        _active_fg = LIGHT_FG
        _active_bg = LIGHT_BG
    _update_classes()

def init():
    """Initialisiert Farben für Windows und setzt Standardtheme."""
    if os.name == 'nt':
        os.system('')
    _update_classes()

# Initialisierung beim Import
init()

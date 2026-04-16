import json
from pathlib import Path

LANGUAGE_DIR = Path(__file__).parent.parent / "locales"
LANGUAGE_DIR.mkdir(exist_ok=True)

_current_language = "de"
_translations = {}

def load_language(lang_code):
    global _current_language, _translations
    lang_file = LANGUAGE_DIR / f"{lang_code}.json"
    if not lang_file.exists():
        # Fallback auf Englisch
        lang_file = LANGUAGE_DIR / "en.json"
        if not lang_file.exists():
            _translations = {}
            return
    with open(lang_file, 'r', encoding='utf-8') as f:
        _translations = json.load(f)
    _current_language = lang_code

def get_text(key, **kwargs):
    """Gibt den übersetzten Text für einen Schlüssel zurück, mit optionalen Formatierungen."""
    text = _translations.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text

def set_language(lang_code):
    load_language(lang_code)

def get_available_languages():
    """Gibt Liste der verfügbaren Sprachdateien zurück (ohne .json)."""
    return [f.stem for f in LANGUAGE_DIR.glob("*.json")]

# Beim Import Standardsprache laden
load_language("de")

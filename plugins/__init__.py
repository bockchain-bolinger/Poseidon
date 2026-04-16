# plugins/__init__.py
import importlib
import pkgutil
from pathlib import Path

def load_plugins():
    plugins = []
    plugin_dir = Path(__file__).parent
    for finder, name, ispkg in pkgutil.iter_modules([str(plugin_dir)]):
        module = importlib.import_module(f"plugins.{name}")
        if hasattr(module, "register"):
            plugins.append(module.register())
    return plugins
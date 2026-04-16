import importlib
import pkgutil
import inspect
from pathlib import Path
from typing import List, Dict, Any, Tuple
from utils.ui_helpers import print_header, menu_prompt, wait_for_enter
from core.plugin_base import PluginBase
from core.logger import logger

class PluginManager:
    """Verwaltet alle Plugins und deren Menüpunkte."""

    def __init__(self, plugin_dir="plugins"):
        self.plugin_dir = Path(__file__).parent.parent / plugin_dir
        self.plugins = []  # Liste von Plugin-Objekten oder Modulen
        self.menu_entries = []  # Liste von (Titel, Callback, Beschreibung)

    def discover_plugins(self):
        """Durchsucht den Plugin-Ordner nach gültigen Plugins."""
        if not self.plugin_dir.exists():
            self.plugin_dir.mkdir(exist_ok=True)
            init_file = self.plugin_dir / "__init__.py"
            if not init_file.exists():
                init_file.touch()
            return

        logger.info(f"Suche nach Plugins in {self.plugin_dir}...")
        for finder, name, ispkg in pkgutil.iter_modules([str(self.plugin_dir)]):
            try:
                module = importlib.import_module(f"plugins.{name}")

                # Suche nach Klassen, die von PluginBase erben
                plugin_classes = [
                    cls for _, cls in inspect.getmembers(module, inspect.isclass)
                    if issubclass(cls, PluginBase) and cls is not PluginBase
                ]

                if plugin_classes:
                    for cls in plugin_classes:
                        instance = cls()
                        self.plugins.append(instance)
                        self.menu_entries.append((instance.name, instance.run, instance.description))
                        logger.info(f"[Plugin] Geladen (Klasse): {instance.name} v{instance.version}")

                # Fallback für altes System (setup-Funktion)
                elif hasattr(module, "setup"):
                    plugin_info = module.setup()
                    if isinstance(plugin_info, tuple) and len(plugin_info) >= 2:
                        titel, callback = plugin_info[0], plugin_info[1]
                        desc = plugin_info[2] if len(plugin_info) > 2 else ""
                        self.plugins.append(module)
                        self.menu_entries.append((titel, callback, desc))
                        logger.info(f"[Plugin] Geladen (Legacy): {titel}")

            except Exception as e:
                logger.error(f"[Plugin] Fehler beim Laden von {name}: {e}")

    def show_plugin_menu(self, device_manager, adb, config):
        """Zeigt ein Untermenü mit allen Plugins an."""
        if not self.menu_entries:
            print("Keine Plugins installiert.")
            wait_for_enter()
            return

        while True:
            print_header("Plugin-Menü", "Zusätzliche Funktionen")
            for i, (titel, _, desc) in enumerate(self.menu_entries, 1):
                entry = f"{i}. {titel}"
                if desc:
                    entry += f" - {desc}"
                print(entry)
            print("0. Zurück")

            choice = menu_prompt("Plugin wählen", range(0, len(self.menu_entries)+1))
            if choice == 0:
                break
            else:
                callback = self.menu_entries[choice-1][1]
                titel = self.menu_entries[choice-1][0]
                logger.info(f"Plugin wird ausgeführt: {titel}")
                try:
                    callback(device_manager, adb, config)
                except Exception as e:
                    logger.error(f"Kritischer Fehler im Plugin {titel}: {e}")
                    print(f"Fehler im Plugin: {e}")
                    wait_for_enter()
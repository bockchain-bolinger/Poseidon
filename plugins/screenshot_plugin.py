import os
from core.plugin_base import PluginBase
from utils.file_utils import ensure_dir, get_timestamp
from utils.ui_helpers import wait_for_enter

class ScreenshotPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "📸 Screenshot (erweitert)"

    @property
    def description(self) -> str:
        return "Erstellt einen Screenshot mit benutzerdefiniertem Namen."

    @property
    def version(self) -> str:
        return "2.0"

    @property
    def author(self) -> str:
        return "Arturik69"

    def run(self, device_manager, adb, config):
        serial = device_manager.get_current_device()
        if not serial:
            print("Kein Gerät verbunden.")
            wait_for_enter()
            return

        name = input("Dateiname (ohne Endung, leer = automatisch): ").strip()
        if not name:
            name = f"screenshot_{get_timestamp()}"
        else:
            name = name.rsplit('.', 1)[0]

        ensure_dir(config["global"]["screenshot_path"])
        dest = os.path.join(config["global"]["screenshot_path"], f"{name}.png")

        print("Erstelle Screenshot...")
        adb.run_shell("screencap -p /sdcard/screen.png", serial)
        print(f"Übertrage Datei nach {dest}...")
        adb.run(f"pull /sdcard/screen.png \"{dest}\"", serial)
        adb.run_shell("rm /sdcard/screen.png", serial)
        print(f"Screenshot erfolgreich gespeichert!")
        wait_for_enter()

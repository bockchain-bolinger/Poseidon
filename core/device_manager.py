import subprocess
from typing import List, Optional
from core.logger import logger

class DeviceManager:
    def __init__(self, config=None):
        """
        Initialisiert den Gerätemanager.
        :param config: Konfigurationsdikt (optional, für gerätespezifische Einstellungen)
        """
        self.config = config if config is not None else {}
        self.current_serial = None
        self.devices = []
        self.device_config = {}
        logger.info("DeviceManager initialisiert.")

    def refresh_devices(self) -> List[str]:
        """Aktualisiert die Liste der verbundenen Geräte."""
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.splitlines()
            devices = []
            for line in lines[1:]:
                if line.strip() and "device" in line and "offline" not in line:
                    serial = line.split()[0]
                    devices.append(serial)
            self.devices = devices
            logger.debug(f"Geräteliste aktualisiert: {devices}")
            if self.current_serial and self.current_serial not in devices:
                logger.warning(f"Zuvor ausgewähltes Gerät {self.current_serial} nicht mehr verbunden.")
                self.current_serial = None
            return devices
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Geräte: {e}")
            return []

    def select_device(self) -> Optional[str]:
        """Zeigt eine Auswahl an Geräten und setzt das aktuelle Gerät."""
        devices = self.refresh_devices()
        if not devices:
            print("Keine Geräte gefunden.")
            return None
        if len(devices) == 1:
            self.current_serial = devices[0]
            print(f"Einziges Gerät ausgewählt: {self.current_serial}")
            logger.info(f"Gerät automatisch ausgewählt: {self.current_serial}")
        else:
            print("Mehrere Geräte verfügbar:")
            for i, serial in enumerate(devices):
                print(f"{i+1}. {serial}")
            try:
                choice = int(input("Bitte wählen: ")) - 1
                if 0 <= choice < len(devices):
                    self.current_serial = devices[choice]
                    logger.info(f"Gerät manuell ausgewählt: {self.current_serial}")
                else:
                    print("Ungültige Auswahl.")
                    logger.warning(f"Ungültige Geräteauswahl getroffen (Index {choice+1}).")
                    return None
            except:
                print("Ungültige Eingabe.")
                logger.warning("Ungültige Eingabe bei Geräteauswahl.")
                return None

        # Gerätespezifische Konfiguration laden (falls vorhanden)
        if self.config and "devices" in self.config and self.current_serial:
            self.device_config = self.config["devices"].get(self.current_serial, {})
        return self.current_serial

    def get_current_device(self) -> Optional[str]:
        """Gibt die Seriennummer des aktuell ausgewählten Geräts zurück."""
        if not self.current_serial:
            self.select_device()
        return self.current_serial

    def get_current_serial(self) -> Optional[str]:
        """Alias für get_current_device (für Kompatibilität)."""
        return self.get_current_device()

    def disconnect_all(self):
        """Trennt alle ADB-Verbindungen."""
        subprocess.run(["adb", "disconnect"], capture_output=True)
        self.current_serial = None
        self.devices = []

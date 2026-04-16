from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple

class PluginBase(ABC):
    """Abstrakte Basisklasse für alle Poseidon-Plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Der Anzeigename des Plugins im Menü."""
        pass

    @property
    def description(self) -> str:
        """Kurze Beschreibung der Funktionalität."""
        return ""

    @property
    def version(self) -> str:
        """Version des Plugins."""
        return "1.0"

    @property
    def author(self) -> str:
        """Autor des Plugins."""
        return "Unbekannt"

    @abstractmethod
    def run(self, device_manager: Any, adb: Any, config: Dict[str, Any]) -> None:
        """Hauptlogik des Plugins."""
        pass

    def setup(self) -> Tuple[str, Any]:
        """
        Rückwärtskompatibilität für das alte Plugin-System.
        Gibt (Name, Run-Methode) zurück.
        """
        return (self.name, self.run)

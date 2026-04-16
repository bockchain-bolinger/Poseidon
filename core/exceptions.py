class PoseidonError(Exception):
    """Basisklasse für alle projektspezifischen Fehler."""


class DependencyError(PoseidonError):
    """Fehlende oder defekte System-/Python-Abhängigkeit."""


class DeviceNotFoundError(PoseidonError):
    """Kein geeignetes Android-Gerät gefunden oder ausgewählt."""


class CommandExecutionError(PoseidonError):
    """Ein Kommando wurde ausgeführt, lieferte aber einen Fehler zurück."""

    def __init__(self, message: str, command: str = "", returncode: int = -1):
        super().__init__(message)
        self.command = command
        self.returncode = returncode


class ConfigurationError(PoseidonError):
    """Fehlerhafte oder unlesbare Konfiguration."""

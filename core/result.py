from dataclasses import dataclass
from typing import Optional, Any, Dict


@dataclass
class CommandResult:
    """Standardisierte Rückgabe für ADB- und System-Kommandos."""

    ok: bool
    stdout: str
    stderr: str
    returncode: int
    command: str
    serial: Optional[str] = None
    duration_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "returncode": self.returncode,
            "command": self.command,
            "serial": self.serial,
            "duration_ms": self.duration_ms,
        }

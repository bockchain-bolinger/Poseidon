from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.adb_handler import ADBHandler
from core.device_manager import DeviceManager
from core.logger import logger


@dataclass
class DeviceMetrics:
    timestamp: str
    serial: str
    battery_level: Optional[int] = None
    battery_temp_c: Optional[float] = None
    memory_used_mb: Optional[float] = None
    memory_free_mb: Optional[float] = None
    cpu_load: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MonitoringService:
    """Erste Monitoring-Abstraktion für spätere Live- und Export-Funktionen."""

    def __init__(self, device_manager: DeviceManager, adb: ADBHandler):
        self.device_manager = device_manager
        self.adb = adb

    def collect_once(self, serial: Optional[str] = None) -> DeviceMetrics:
        serial = serial or self.device_manager.get_current_device() or "unknown"

        battery_level = self._read_battery_level(serial)
        battery_temp_c = self._read_battery_temp_c(serial)
        memory_used_mb, memory_free_mb = self._read_memory(serial)

        metrics = DeviceMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            serial=serial,
            battery_level=battery_level,
            battery_temp_c=battery_temp_c,
            memory_used_mb=memory_used_mb,
            memory_free_mb=memory_free_mb,
            cpu_load=None,
        )
        logger.debug(f"Monitoring-Metriken erfasst: {metrics.to_dict()}")
        return metrics

    def _read_battery_level(self, serial: str) -> Optional[int]:
        out, _, rc = self.adb.run_shell("dumpsys battery", serial=serial, use_cache=False)
        if rc != 0:
            return None
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("level:"):
                try:
                    return int(line.split(":", 1)[1].strip())
                except ValueError:
                    return None
        return None

    def _read_battery_temp_c(self, serial: str) -> Optional[float]:
        out, _, rc = self.adb.run_shell("dumpsys battery", serial=serial, use_cache=False)
        if rc != 0:
            return None
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("temperature:"):
                try:
                    raw = int(line.split(":", 1)[1].strip())
                    return raw / 10.0
                except ValueError:
                    return None
        return None

    def _read_memory(self, serial: str) -> tuple[Optional[float], Optional[float]]:
        out, _, rc = self.adb.run_shell("cat /proc/meminfo", serial=serial, use_cache=False)
        if rc != 0:
            return None, None

        mem_total = None
        mem_available = None

        for line in out.splitlines():
            if line.startswith("MemTotal:"):
                parts = line.split()
                if len(parts) >= 2:
                    mem_total = float(parts[1]) / 1024.0
            elif line.startswith("MemAvailable:"):
                parts = line.split()
                if len(parts) >= 2:
                    mem_available = float(parts[1]) / 1024.0

        if mem_total is None or mem_available is None:
            return None, None

        used = round(mem_total - mem_available, 2)
        free = round(mem_available, 2)
        return used, free

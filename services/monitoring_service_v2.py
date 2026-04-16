from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
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


class MonitoringServiceV2:
    """Monitoring-Service mit Snapshot-Erfassung und Exportfunktionen."""

    def __init__(self, device_manager: DeviceManager, adb: ADBHandler, export_dir: str = "./logs"):
        self.device_manager = device_manager
        self.adb = adb
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def collect_once(self, serial: Optional[str] = None) -> DeviceMetrics:
        serial = serial or self.device_manager.get_current_device() or "unknown"
        battery_dump = self._read_battery_dump(serial)
        memory_dump = self._read_meminfo(serial)

        metrics = DeviceMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            serial=serial,
            battery_level=self._parse_battery_level(battery_dump),
            battery_temp_c=self._parse_battery_temp_c(battery_dump),
            memory_used_mb=self._parse_memory(memory_dump)[0],
            memory_free_mb=self._parse_memory(memory_dump)[1],
            cpu_load=self._read_cpu_load(serial),
        )
        logger.debug(f"MonitoringServiceV2 metrics: {metrics.to_dict()}")
        return metrics

    def export_jsonl(self, metrics: DeviceMetrics, filename: str = "poseidon_metrics.jsonl") -> Path:
        target = self.export_dir / filename
        with open(target, "a", encoding="utf-8") as f:
            f.write(json.dumps(metrics.to_dict(), ensure_ascii=False) + "\n")
        logger.info(f"JSONL export geschrieben: {target}")
        return target

    def export_csv(self, metrics: DeviceMetrics, filename: str = "poseidon_metrics.csv") -> Path:
        target = self.export_dir / filename
        row = metrics.to_dict()
        write_header = not target.exists()
        with open(target, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(row.keys()))
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        logger.info(f"CSV export geschrieben: {target}")
        return target

    def _read_battery_dump(self, serial: str) -> str:
        out, _, rc = self.adb.run_shell("dumpsys battery", serial=serial, use_cache=False)
        return out if rc == 0 else ""

    def _read_meminfo(self, serial: str) -> str:
        out, _, rc = self.adb.run_shell("cat /proc/meminfo", serial=serial, use_cache=False)
        return out if rc == 0 else ""

    def _read_cpu_load(self, serial: str) -> Optional[float]:
        out, _, rc = self.adb.run_shell("cat /proc/loadavg", serial=serial, use_cache=False)
        if rc != 0 or not out:
            return None
        try:
            return float(out.split()[0])
        except Exception:
            return None

    def _parse_battery_level(self, dump: str) -> Optional[int]:
        for line in dump.splitlines():
            line = line.strip()
            if line.startswith("level:"):
                try:
                    return int(line.split(":", 1)[1].strip())
                except ValueError:
                    return None
        return None

    def _parse_battery_temp_c(self, dump: str) -> Optional[float]:
        for line in dump.splitlines():
            line = line.strip()
            if line.startswith("temperature:"):
                try:
                    raw = int(line.split(":", 1)[1].strip())
                    return raw / 10.0
                except ValueError:
                    return None
        return None

    def _parse_memory(self, dump: str) -> tuple[Optional[float], Optional[float]]:
        mem_total = None
        mem_available = None
        for line in dump.splitlines():
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

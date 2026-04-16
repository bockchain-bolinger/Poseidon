import shlex
import subprocess
import time
from typing import Optional, Tuple

from core.logger import logger
from core.result import CommandResult


class ADBHandlerV2:
    """Gehärteter ADB-Handler mit Result-Objekt, Retry-Logik und Cache."""

    def __init__(self, device_manager, cache_ttl: int = 30, default_timeout: int = 30, retries: int = 1):
        self.device_manager = device_manager
        self.cache_ttl = cache_ttl
        self.default_timeout = default_timeout
        self.retries = retries
        self._property_cache = {}
        self._generic_cache = {}
        self._last_serial = None

    def _get_serial(self, serial: Optional[str] = None) -> Optional[str]:
        current_serial = serial if serial else self.device_manager.get_current_device()
        if current_serial != self._last_serial:
            self.clear_cache()
            self._last_serial = current_serial
        return current_serial

    def _build_cmd(self, cmd: str, serial: Optional[str] = None) -> str:
        s = self._get_serial(serial)
        return f"adb -s {s} {cmd}" if s else f"adb {cmd}"

    def run_result(self, cmd: str, serial: Optional[str] = None, timeout: Optional[int] = None, use_cache: bool = False) -> CommandResult:
        full_cmd = self._build_cmd(cmd, serial)
        timeout = timeout or self.default_timeout

        if use_cache and full_cmd in self._generic_cache:
            ts, cached = self._generic_cache[full_cmd]
            if time.time() - ts < self.cache_ttl:
                logger.debug(f"ADB cache hit: {full_cmd}")
                return cached

        last_result = None
        for attempt in range(self.retries + 1):
            started = time.time()
            try:
                cmd_list = shlex.split(full_cmd)
                process = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate(timeout=timeout)
                result = CommandResult(
                    ok=process.returncode == 0,
                    stdout=(stdout or "").strip(),
                    stderr=(stderr or "").strip(),
                    returncode=process.returncode,
                    command=full_cmd,
                    serial=self._get_serial(serial),
                    duration_ms=int((time.time() - started) * 1000),
                )
                last_result = result
                if use_cache:
                    self._generic_cache[full_cmd] = (time.time(), result)
                if result.ok or attempt >= self.retries:
                    if not result.ok:
                        logger.warning(f"ADB command failed ({result.returncode}): {result.stderr}")
                    return result
                logger.warning(f"ADB retry {attempt + 1}/{self.retries} for: {full_cmd}")
                time.sleep(0.25)
            except subprocess.TimeoutExpired:
                try:
                    process.kill()
                except Exception:
                    pass
                last_result = CommandResult(
                    ok=False,
                    stdout="",
                    stderr=f"Timeout nach {timeout}s",
                    returncode=-1,
                    command=full_cmd,
                    serial=self._get_serial(serial),
                    duration_ms=int((time.time() - started) * 1000),
                )
            except Exception as e:
                last_result = CommandResult(
                    ok=False,
                    stdout="",
                    stderr=str(e),
                    returncode=-1,
                    command=full_cmd,
                    serial=self._get_serial(serial),
                    duration_ms=int((time.time() - started) * 1000),
                )
            if attempt < self.retries:
                time.sleep(0.25)

        return last_result or CommandResult(False, "", "Unbekannter Fehler", -1, full_cmd, self._get_serial(serial), None)

    def run(self, cmd: str, serial: Optional[str] = None, timeout: Optional[int] = None, use_cache: bool = False) -> Tuple[str, str, int]:
        result = self.run_result(cmd, serial=serial, timeout=timeout, use_cache=use_cache)
        return result.stdout, result.stderr, result.returncode

    def run_shell(self, shell_cmd: str, serial: Optional[str] = None, timeout: Optional[int] = None, use_cache: bool = False) -> Tuple[str, str, int]:
        return self.run(f"shell {shell_cmd}", serial=serial, timeout=timeout, use_cache=use_cache)

    def get_device_property(self, prop: str, serial: Optional[str] = None) -> str:
        s = self._get_serial(serial)
        cache_key = f"{s}:{prop}"
        if cache_key in self._property_cache:
            return self._property_cache[cache_key]
        out, _, _ = self.run_shell(f"getprop {prop}", serial=s, use_cache=True)
        self._property_cache[cache_key] = out
        return out

    def clear_cache(self) -> None:
        self._generic_cache = {}
        self._property_cache = {}
        logger.info("ADBHandlerV2 cache cleared.")

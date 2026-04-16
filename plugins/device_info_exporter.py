"""
Plugin: Geräteinformationen in Datei exportieren
Speichert Modell, Android-Version, Akku, IMEI, etc. als JSON.
"""
import json
from utils.file_utils import save_file, get_timestamp
from utils.ui_helpers import wait_for_enter, confirm

def setup():
    return ("📄 Geräte-Info exportieren (JSON)", run)

def run(device_manager, adb, config):
    serial = device_manager.get_current_device()
    if not serial:
        print("Kein Gerät verbunden.")
        wait_for_enter()
        return

    info = {}
    info["serial"] = serial
    info["model"] = adb.get_device_property("ro.product.model", serial)
    info["brand"] = adb.get_device_property("ro.product.brand", serial)
    info["android"] = adb.get_device_property("ro.build.version.release", serial)
    info["sdk"] = adb.get_device_property("ro.build.version.sdk", serial)
    info["security_patch"] = adb.get_device_property("ro.build.version.security_patch", serial)

    battery_out, _, _ = adb.run_shell("dumpsys battery", serial)
    for line in battery_out.splitlines():
        if "level" in line:
            info["battery_level"] = line.split(":")[-1].strip()
            break

    # IMEI (falls verfügbar)
    imei_out, _, _ = adb.run_shell("service call iphonesubinfo 1 | cut -c 52-66 | tr -d '.[:space:]'", serial)
    if imei_out and len(imei_out) >= 15:
        info["imei"] = imei_out.strip()

    filename = f"device_info_{get_timestamp()}.json"
    save_file(json.dumps(info, indent=2), filename, "exports")
    print(f"Geräteinformationen gespeichert unter: exports/{filename}")
    wait_for_enter()

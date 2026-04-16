from utils.ui_helpers import show_menu_generic, wait_for_enter
from utils.ansi_colors import fg, style
from utils.decorators import require_device
from utils.i18n import get_text

def show_menu(device_manager, adb):
    options = [
        ("📋", "info_basic", show_basic_info),
        ("💾", "info_storage", show_storage_info),
        ("🖥️", "info_display", show_display_info),
        ("🔧", "info_props", search_properties),
        ("📡", "info_network", show_network_info),
        ("🌡️", "info_sensors", show_sensors),
        ("📱", "info_imei", show_imei),
        ("🌡️", "info_cpu", show_cpu_temp),
        ("📶", "info_signal", show_signal_strength)
    ]
    show_menu_generic("info_title", "info_subtitle", options, device_manager, adb)

@require_device
def show_basic_info(device_manager, adb):
    serial = device_manager.get_current_device()
    print(f"{fg.CYAN}Fetching device information...{style.RESET}")
    model = adb.get_device_property("ro.product.model", serial)
    brand = adb.get_device_property("ro.product.brand", serial)
    android = adb.get_device_property("ro.build.version.release", serial)
    sdk = adb.get_device_property("ro.build.version.sdk", serial)
    security = adb.get_device_property("ro.build.version.security_patch", serial)
    battery_out, _, _ = adb.run_shell("dumpsys battery", serial)
    battery_level = "Unknown"
    for line in battery_out.splitlines():
        if "level" in line:
            battery_level = line.split(":")[-1].strip()
    
    # Hier nutzen wir noch teilweise deutsche Labels, da wir keine Keys dafür haben.
    # Wir könnten mehr Keys hinzufügen oder es so lassen, wenn es nur Labels sind.
    print(f"\n{fg.GREEN}Model:{style.RESET} {model}")
    print(f"{fg.GREEN}Brand:{style.RESET} {brand}")
    print(f"{fg.GREEN}Android:{style.RESET} {android} (API {sdk})")
    print(f"{fg.GREEN}Security Patch:{style.RESET} {security}")
    print(f"{fg.GREEN}Battery:{style.RESET} {battery_level}%")
    wait_for_enter()

@require_device
def show_storage_info(device_manager, adb):
    serial = device_manager.get_current_device()
    out, _, _ = adb.run_shell("df -h /sdcard", serial)
    print("\nInternal Storage (/sdcard):")
    print(out)
    out, _, _ = adb.run_shell("df -h /data", serial)
    print("\nData Partition (/data):")
    print(out)
    wait_for_enter()

@require_device
def show_display_info(device_manager, adb):
    serial = device_manager.get_current_device()
    out, _, _ = adb.run_shell("wm size", serial)
    print(f"Resolution: {out}")
    out, _, _ = adb.run_shell("wm density", serial)
    print(f"DPI: {out}")
    wait_for_enter()

@require_device
def search_properties(device_manager, adb):
    serial = device_manager.get_current_device()
    search = input("Search term for system properties (empty = all): ")
    out, _, _ = adb.run_shell("getprop", serial)
    lines = out.splitlines()
    if search:
        lines = [l for l in lines if search.lower() in l.lower()]
    for line in lines[:50]:
        print(line)
    if len(lines) > 50:
        print(f"... and {len(lines)-50} more.")
    wait_for_enter()

@require_device
def show_network_info(device_manager, adb):
    serial = device_manager.get_current_device()
    out, _, _ = adb.run_shell("ip addr show wlan0", serial)
    print("Wi-Fi IP:")
    print(out)
    out, _, _ = adb.run_shell("ip addr show rmnet0", serial)
    print("\nMobile Data IP:")
    print(out)
    wait_for_enter()

@require_device
def show_sensors(device_manager, adb):
    serial = device_manager.get_current_device()
    out, _, _ = adb.run_shell("dumpsys sensorservice", serial)
    print("Sensors:")
    for line in out.splitlines():
        if "Sensor" in line and "{" in line:
            print(line.strip())
    wait_for_enter()

@require_device
def show_imei(device_manager, adb):
    serial = device_manager.get_current_device()
    out, _, _ = adb.run_shell("service call iphonesubinfo 1 | cut -c 52-66 | tr -d '.[:space:]'", serial)
    if not out or len(out) < 15:
        out, _, _ = adb.run_shell("dumpsys telephony.device_identity | grep 'Device IMEI'", serial)
    print(f"📱 IMEI: {out.strip()}")
    wait_for_enter()

@require_device
def show_cpu_temp(device_manager, adb):
    serial = device_manager.get_current_device()
    out, _, _ = adb.run_shell("dumpsys battery | grep temperature", serial)
    temp = out.split(":")[-1].strip()
    if temp:
        try:
            temp_celsius = int(temp) / 10
            print(f"🌡️ Battery Temperature: {temp_celsius}°C")
        except:
            print(f"🌡️ Battery Temperature: {temp} (Raw)")
    else:
        print("No temperature data available.")
    out, _, _ = adb.run_shell("top -n 1 -b | grep -E '^(User|System)'", serial)
    print("\n⚙️ CPU Usage:")
    print(out)
    wait_for_enter()

@require_device
def show_signal_strength(device_manager, adb):
    serial = device_manager.get_current_device()
    out, _, _ = adb.run_shell("dumpsys telephony.registry | grep -E 'mSignalStrength|mDataConnectionState'", serial)
    print("📶 Signal Strength:")
    print(out)
    wait_for_enter()

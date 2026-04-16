from utils.ui_helpers import print_header, menu_prompt, wait_for_enter
from utils.ansi_colors import fg, style
from utils.decorators import require_device

@require_device
def show_menu(device_manager, adb):
    serial = device_manager.get_current_device()
    
    while True:
        print_header("ANALYZER & MITM", "Dynamic Analysis Mode")
        print("1. 🕵️ App-Spion (Dateizugriff-Monitor)")
        print("2. 🌐 Globalen Proxy konfigurieren")
        print("3. 🛑 Proxy deaktivieren")
        print("0. Zurück")
        
        choice = menu_prompt("Option", range(0, 4))
        if choice == 0: break
        elif choice == 1: monitor_app_files(adb, serial)
        elif choice == 2: set_proxy(adb, serial)
        elif choice == 3: disable_proxy(adb, serial)

def monitor_app_files(adb, serial):
    pkg = input("Package-Name für Überwachung: ")
    print(f"{fg.CYAN}Überwache Datei-Events für {pkg}... (Strg+C zum Stoppen){style.RESET}")
    # Nutzt logcat, um File-Zugriffe zu "sniffen" (kann je nach App-Verhalten variieren)
    try:
        adb.run_shell(f"logcat | grep '{pkg}'", serial)
    except KeyboardInterrupt:
        pass

def set_proxy(adb, serial):
    ip = input("PC-IP Adresse: ")
    port = input("Proxy-Port (z.B. 8080): ")
    adb.run_shell(f"settings put global http_proxy {ip}:{port}", serial)
    print(f"{fg.GREEN}Proxy gesetzt auf {ip}:{port}{style.RESET}")
    wait_for_enter()

def disable_proxy(adb, serial):
    adb.run_shell("settings put global http_proxy :0", serial)
    print(f"{fg.YELLOW}Proxy deaktiviert.{style.RESET}")
    wait_for_enter()

import time
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm
from utils.file_utils import save_file, get_timestamp

def show_menu(device_manager, adb):
    while True:
        clear_screen()
        print_header("Entwickler-Helfer", "Optionen für Entwickler")
        print("1. 📐 Layout-Grenzen anzeigen")
        print("2. 🎨 GPU-Überzeichnung anzeigen")
        print("3. 🕒 Strikten Modus aktivieren")
        print("4. 🖥️ OpenGL-Treiberinfo")
        print("5. 📊 Task Manager (laufende Prozesse)")
        print("6. 🔧 Dumpsys-Dienste auflisten")
        print("7. 📱 Entwickleroptionen öffnen (Intent)")
        print("8. 🔧 Dumpsys-Dienst auswählen")
        print("9. 🔋 Batteriestatistiken zurücksetzen")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 10))

        if choice == 0:
            break
        elif choice == 1:
            toggle_layout_bounds(device_manager, adb)
        elif choice == 2:
            toggle_gpu_overdraw(device_manager, adb)
        elif choice == 3:
            toggle_strict_mode(device_manager, adb)
        elif choice == 4:
            gpu_info(device_manager, adb)
        elif choice == 5:
            task_manager(device_manager, adb)
        elif choice == 6:
            list_dumpsys(device_manager, adb)
        elif choice == 7:
            open_developer_options(device_manager, adb)
        elif choice == 8:
            select_dumpsys(device_manager, adb)
        elif choice == 9:
            reset_battery_stats(device_manager, adb)

def toggle_layout_bounds(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    out, _, _ = adb.run_shell("settings get global debug_layout", serial)
    current = out.strip()
    new = "0" if current == "1" else "1"
    adb.run_shell(f"settings put global debug_layout {new}", serial)
    print(f"Layout-Grenzen: {'AN' if new=='1' else 'AUS'}")
    wait_for_enter()

def toggle_gpu_overdraw(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    out, _, _ = adb.run_shell("settings get global show_gpu_overdraw", serial)
    current = out.strip()
    new = "0" if current == "1" else "1"
    adb.run_shell(f"settings put global show_gpu_overdraw {new}", serial)
    print(f"GPU-Überzeichnung: {'AN' if new=='1' else 'AUS'}")
    wait_for_enter()

def toggle_strict_mode(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    out, _, _ = adb.run_shell("settings get global strict_mode", serial)
    current = out.strip()
    new = "0" if current == "1" else "1"
    adb.run_shell(f"settings put global strict_mode {new}", serial)
    print(f"Strikter Modus: {'AN' if new=='1' else 'AUS'}")
    wait_for_enter()

def gpu_info(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    out, _, _ = adb.run_shell("dumpsys gfxinfo", serial)
    print(out[:1000])
    wait_for_enter()

def task_manager(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    out, _, _ = adb.run_shell("top -n 1", serial)
    print(out)
    wait_for_enter()

def list_dumpsys(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    out, _, _ = adb.run_shell("dumpsys -l", serial)
    print("Verfügbare Dienste:")
    print(out)
    wait_for_enter()

def open_developer_options(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    adb.run_shell("am start -n com.android.settings/.DevelopmentSettings", serial)
    print("Entwickleroptionen geöffnet.")
    wait_for_enter()

def select_dumpsys(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    out, _, _ = adb.run_shell("dumpsys -l", serial)
    services = [line.strip() for line in out.splitlines() if line.strip()]
    print("Verfügbare Dienste (Auszug):")
    for i, s in enumerate(services[:20]):
        print(f"{i+1}. {s}")
    print("0. Eigene Eingabe")
    choice = menu_prompt("Dienst wählen", range(0, len(services[:20])+1))
    if choice == 0:
        service = input("Dienstname: ")
    else:
        service = services[choice-1]
    out, _, _ = adb.run_shell(f"dumpsys {service}", serial)
    print(f"\n--- dumpsys {service} ---")
    print(out[:2000])
    if len(out) > 2000:
        print("... (Ausgabe gekürzt)")
    if confirm("Vollständige Ausgabe in Datei speichern?"):
        filename = f"dumpsys_{service}_{get_timestamp()}.txt"
        save_file(out, filename, "logs")
        print(f"Gespeichert unter: logs/{filename}")
    wait_for_enter()

def reset_battery_stats(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    if confirm("Batteriestatistiken wirklich zurücksetzen?"):
        adb.run_shell("dumpsys batterystats --reset", serial)
        print("Batteriestatistiken zurückgesetzt.")
    wait_for_enter()
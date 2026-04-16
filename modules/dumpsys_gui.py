import json
import re
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm
from utils.file_utils import save_file, get_timestamp

def show_menu(device_manager, adb):
    while True:
        clear_screen()
        print_header("Dumpsys GUI", "Systemdienst-Informationen strukturiert anzeigen")
        print("1. 🔍 Verfügbare Dienste auflisten")
        print("2. 📊 Dienst auswählen und anzeigen")
        print("3. 🔎 In Dienstausgabe suchen")
        print("4. 💾 Dienstausgabe exportieren (JSON/CSV)")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 5))
        if choice == 0:
            break
        elif choice == 1:
            list_services(device_manager, adb)
        elif choice == 2:
            show_service(device_manager, adb)
        elif choice == 3:
            search_in_service(device_manager, adb)
        elif choice == 4:
            export_service(device_manager, adb)

def list_services(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    out, _, _ = adb.run_shell("dumpsys -l", serial)
    services = [s.strip() for s in out.splitlines() if s.strip()]
    print("\nVerfügbare Dienste (insgesamt {}):".format(len(services)))
    for i, s in enumerate(services, 1):
        print(f"{i:3}. {s}")
    wait_for_enter()

def show_service(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    service = input("Dienstname (z.B. battery, wifi, meminfo): ").strip()
    if not service:
        return
    print(f"Rufe dumpsys {service} ab...")
    out, _, _ = adb.run_shell(f"dumpsys {service}", serial)
    # Strukturierte Aufbereitung für bekannte Dienste
    parsed = parse_dumpsys(service, out)
    if parsed:
        print_formatted(parsed)
    else:
        # Rohe Ausgabe mit Paginierung
        lines = out.splitlines()
        for i, line in enumerate(lines):
            print(line)
            if (i+1) % 30 == 0:
                if not confirm("Weiter?"):
                    break
    wait_for_enter()

def parse_dumpsys(service, raw_output):
    """Versucht, bekannte Dienste zu parsen und in ein dict zu überführen."""
    result = {"service": service, "sections": {}}
    if service == "battery":
        current_section = "battery"
        for line in raw_output.splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                result["sections"][key.strip()] = val.strip()
        return result
    elif service == "wifi":
        # Einfache Extraktion von SSID, Signalstärke, etc.
        match = re.search(r"SSID: (.+)", raw_output)
        if match:
            result["sections"]["SSID"] = match.group(1)
        match = re.search(r"RSSI: (.+)", raw_output)
        if match:
            result["sections"]["RSSI"] = match.group(1)
        return result
    elif service == "meminfo":
        result["sections"]["raw"] = raw_output  # Zu komplex für einfaches Parsing
        return result
    else:
        return None

def print_formatted(parsed):
    print(f"\n--- Dienst: {parsed['service']} ---")
    for key, val in parsed["sections"].items():
        print(f"{key}: {val}")

def search_in_service(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    service = input("Dienstname: ").strip()
    if not service:
        return
    keyword = input("Suchbegriff: ").strip()
    if not keyword:
        return
    out, _, _ = adb.run_shell(f"dumpsys {service} | grep -i '{keyword}'", serial)
    if out:
        print(f"\n--- Gefundene Zeilen in {service} für '{keyword}' ---")
        print(out)
    else:
        print("Keine Treffer.")
    wait_for_enter()

def export_service(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    service = input("Dienstname: ").strip()
    if not service:
        return
    out, _, _ = adb.run_shell(f"dumpsys {service}", serial)
    fmt = input("Exportformat (json, csv, txt) [txt]: ").strip().lower() or "txt"
    timestamp = get_timestamp()
    filename = f"dumpsys_{service}_{timestamp}.{fmt}"
    if fmt == "json":
        data = {"service": service, "timestamp": timestamp, "output": out}
        save_file(json.dumps(data, indent=2), filename, "exports")
    elif fmt == "csv":
        # Sehr einfache CSV: jede Zeile als Feld
        lines = out.splitlines()
        csv_content = "\n".join([f'"{line.replace(chr(34), chr(34)+chr(34))}"' for line in lines])
        save_file(csv_content, filename, "exports")
    else:
        save_file(out, filename, "exports")
    print(f"Exportiert nach: exports/{filename}")
    wait_for_enter()

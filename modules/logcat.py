import subprocess
import os
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm
from utils.file_utils import get_timestamp, save_file

def show_menu(device_manager, adb):
    while True:
        clear_screen()
        print_header("Logcat Viewer", "System-Logs anzeigen")
        print("1. 📋 Logcat live anzeigen")
        print("2. 💾 Logcat in Datei speichern")
        print("3. 🔍 Nach Schlagwort filtern")
        print("4. 📊 Logcat nach Priorität filtern")
        print("5. 🧹 Logcat löschen")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 6))

        if choice == 0:
            break
        elif choice == 1:
            logcat_live(device_manager, adb)
        elif choice == 2:
            logcat_save(device_manager, adb)
        elif choice == 3:
            logcat_filter(device_manager, adb)
        elif choice == 4:
            logcat_priority(device_manager, adb)
        elif choice == 5:
            logcat_clear(device_manager, adb)

def logcat_live(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    print("Drücke Ctrl+C zum Beenden.")
    try:
        # Direkter subprocess-Aufruf für Live-Ausgabe
        cmd = f"adb -s {serial} logcat"
        subprocess.run(cmd, shell=True)
    except KeyboardInterrupt:
        pass
    wait_for_enter()

def logcat_save(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    filename = f"logcat_{get_timestamp()}.txt"
    out, _, _ = adb.run("logcat -d", serial)
    save_file(out, filename, "logs")
    print(f"Logcat gespeichert unter: logs/{filename}")
    wait_for_enter()

def logcat_filter(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    tag = input("Nach welchem Schlagwort filtern? ")
    if not tag:
        return
    out, _, _ = adb.run(f"logcat -d | grep -i {tag}", serial)
    print(out)
    wait_for_enter()

def logcat_priority(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    print("Priorität: V(erbose), D(ebug), I(nfo), W(arn), E(rror), F(atal)")
    prio = input("Buchstabe: ").upper()
    if prio not in "VDIWEF":
        print("Ungültig.")
        return
    out, _, _ = adb.run(f"logcat -d *:{prio}", serial)
    print(out)
    wait_for_enter()

def logcat_clear(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    adb.run("logcat -c", serial)
    print("Logcat gelöscht.")
    wait_for_enter()
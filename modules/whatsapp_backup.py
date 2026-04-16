import os
import re
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm
from utils.file_utils import ensure_dir, get_timestamp, save_file

def show_menu(device_manager, adb):
    while True:
        clear_screen()
        print_header("WhatsApp Backup", "Chat-Datenbank sichern (nur mit Root)")
        print("1. 📱 WhatsApp-Datenbank kopieren (msgstore.db)")
        print("2. 📄 Datenbank als Text exportieren (erfordert sqlite3)")
        print("3. 🔍 Nachrichten durchsuchen")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 4))
        if choice == 0:
            break
        elif choice == 1:
            backup_whatsapp_db(device_manager, adb)
        elif choice == 2:
            export_db_to_text(device_manager, adb)
        elif choice == 3:
            search_messages(device_manager, adb)

def backup_whatsapp_db(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    print("Dies erfordert Root-Rechte auf dem Gerät.")
    if not confirm("Fahren Sie fort?"):
        return

    # Pfade für WhatsApp-Datenbanken (kann je nach Version variieren)
    db_paths = [
        "/data/data/com.whatsapp/databases/msgstore.db",
        "/data/data/com.whatsapp/databases/msgstore.db.crypt14",
        "/data/data/com.whatsapp/databases/msgstore.db.crypt13"
    ]

    found = False
    for db_path in db_paths:
        # Prüfen, ob Datei existiert
        test, _, _ = adb.run_shell(f"test -f {db_path} && echo exists", serial)
        if "exists" in test:
            found = True
            print(f"Gefunden: {db_path}")
            dest = f"whatsapp_backup_{get_timestamp()}.db"
            # Mit Root-Berechtigung kopieren
            adb.run_shell(f"su -c 'cat {db_path}' > /sdcard/whatsapp_temp.db", serial)
            adb.run("pull /sdcard/whatsapp_temp.db " + dest, serial)
            adb.run_shell("rm /sdcard/whatsapp_temp.db", serial)
            print(f"Backup gespeichert: {dest}")
            break

    if not found:
        print("Keine WhatsApp-Datenbank gefunden. Stellen Sie sicher, dass das Gerät gerootet ist und WhatsApp installiert wurde.")
    wait_for_enter()

def export_db_to_text(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    print("Diese Funktion exportiert die msgstore.db als Text (erfordert sqlite3 auf dem Gerät oder PC).")
    print("Es wird versucht, sqlite3 auf dem Gerät zu verwenden (Root).")
    if not confirm("Fortfahren?"):
        return

    # Prüfen, ob sqlite3 vorhanden ist
    has_sqlite, _, _ = adb.run_shell("which sqlite3", serial)
    if not has_sqlite:
        print("sqlite3 nicht auf dem Gerät gefunden. Kann nicht exportieren.")
        wait_for_enter()
        return

    # Temporäre Kopie der Datenbank erstellen
    adb.run_shell("su -c 'cat /data/data/com.whatsapp/databases/msgstore.db' > /sdcard/msgstore_temp.db", serial)
    # SQL-Abfrage, um Nachrichten in Text zu extrahieren
    query = "SELECT _id, key_from_me, message_data, timestamp FROM messages ORDER BY timestamp;"
    # Ausgabe als CSV
    cmd = f"sqlite3 -csv /sdcard/msgstore_temp.db \"{query}\""
    out, _, _ = adb.run_shell(cmd, serial)
    adb.run_shell("rm /sdcard/msgstore_temp.db", serial)

    if out:
        filename = f"whatsapp_messages_{get_timestamp()}.csv"
        save_file(out, filename, "exports")
        print(f"Nachrichten exportiert nach: exports/{filename}")
    else:
        print("Keine Daten oder Fehler beim Export.")
    wait_for_enter()

def search_messages(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    keyword = input("Suchbegriff in Nachrichten: ").strip()
    if not keyword:
        return
    # Ähnlicher Prozess wie oben, aber mit grep
    adb.run_shell("su -c 'cat /data/data/com.whatsapp/databases/msgstore.db' > /sdcard/msgstore_temp.db", serial)
    # Wir versuchen, mit sqlite3 zu suchen (falls vorhanden)
    has_sqlite, _, _ = adb.run_shell("which sqlite3", serial)
    if has_sqlite:
        query = f"SELECT _id, message_data FROM messages WHERE message_data LIKE '%{keyword}%' LIMIT 50;"
        cmd = f"sqlite3 /sdcard/msgstore_temp.db \"{query}\""
        out, _, _ = adb.run_shell(cmd, serial)
        if out:
            print(f"\n--- Gefundene Nachrichten für '{keyword}' ---")
            print(out)
        else:
            print("Keine Treffer.")
    else:
        print("sqlite3 nicht gefunden, kann nicht suchen.")
    adb.run_shell("rm /sdcard/msgstore_temp.db", serial)
    wait_for_enter()

import os
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm
from utils.ansi_colors import fg, style
from utils.decorators import require_device

@require_device
def show_manager(device_manager, adb, config):
    """Interaktiver Dateimanager für Android (/sdcard)."""
    current_path = "/sdcard"
    serial = device_manager.get_current_device()

    while True:
        clear_screen()
        print_header("ANDROID FILE MANAGER", f"Path: {current_path}")
        
        # 1. Inhalt des aktuellen Verzeichnisses abrufen
        out, err, rc = adb.run_shell(f"ls -F {current_path}", serial, use_cache=True)
        if rc != 0:
            print(f"{fg.RED}Fehler beim Lesen des Verzeichnisses: {err}{style.RESET}")
            current_path = "/sdcard" # Fallback
            wait_for_enter()
            continue

        items = out.splitlines()
        # Sortieren: Ordner zuerst
        items.sort(key=lambda x: not x.endswith('/'))

        print(f" 0. [ .. ] (Parent Directory)")
        for i, item in enumerate(items, 1):
            icon = "📁" if item.endswith('/') else "📄"
            print(f" {i:2}. {icon} {item}")
        
        print(f"\n a. 📥 [DOWNLOAD] (Datei vom Handy laden)")
        print(f" u. 📤 [UPLOAD] (Datei zum Handy senden)")
        print(f" d. 🗑️  [DELETE] (Datei löschen)")
        print(f" 00. ❌ [EXIT]")

        choice = input(f"\n{fg.YELLOW}Option / Nummer wählen{style.RESET}: ").strip()

        if choice == "00":
            break
        elif choice == "0":
            if current_path != "/":
                current_path = os.path.dirname(current_path.rstrip('/'))
                if not current_path: current_path = "/"
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(items):
                selected = items[idx]
                if selected.endswith('/'):
                    current_path = os.path.join(current_path, selected.rstrip('/'))
                else:
                    print(f"Info: {selected} ist eine Datei. Nutze 'a' zum Herunterladen.")
                    wait_for_enter()
        elif choice == 'a':
            idx = int(input("Nummer der Datei zum Download: ")) - 1
            if 0 <= idx < len(items):
                file_name = items[idx].rstrip('/')
                src = os.path.join(current_path, file_name)
                dest = os.path.join(config['backup_path'], file_name)
                print(f"Lade {src} herunter...")
                adb.run(f"pull \"{src}\" \"{dest}\"", serial)
                print(f"Gespeichert in: {dest}")
                wait_for_enter()
        elif choice == 'u':
            local_path = input("Lokaler Pfad zur Datei: ").strip()
            if os.path.exists(local_path):
                file_name = os.path.basename(local_path)
                dest = os.path.join(current_path, file_name)
                print(f"Sende {local_path} nach {dest}...")
                adb.run(f"push \"{local_path}\" \"{dest}\"", serial)
                print("Upload abgeschlossen.")
                adb.clear_cache() # Liste aktualisieren
            else:
                print("Datei nicht gefunden.")
            wait_for_enter()
        elif choice == 'd':
            idx = int(input("Nummer zum Löschen: ")) - 1
            if 0 <= idx < len(items):
                target = os.path.join(current_path, items[idx].rstrip('/'))
                if confirm(f"Wirklich löschen: {target}?"):
                    adb.run_shell(f"rm -rf \"{target}\"", serial)
                    print("Gelöscht.")
                    adb.clear_cache()
            wait_for_enter()

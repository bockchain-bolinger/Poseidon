import json
import time
from pathlib import Path
from typing import Dict, Any, List
from utils.ui_helpers import confirm, wait_for_enter, SimpleProgressBar
from utils.file_utils import get_timestamp, save_file
from utils.ansi_colors import fg, style

class BatchProcessor:
    """Führt JSON-Skripte mit ADB-Befehlen aus."""

    def __init__(self, adb, device_manager):
        self.adb = adb
        self.device_manager = device_manager
        self.variables = {}  # Für einfache Variablenersetzung

    def run_script(self, script_path: str) -> bool:
        """Führt ein Skript aus. Gibt True bei Erfolg zurück."""
        p = Path(script_path)
        if not p.exists():
            print(f"{fg.RED}Skript nicht gefunden: {script_path}{style.RESET}")
            return False

        with open(p, 'r', encoding='utf-8') as f:
            try:
                script = json.load(f)
            except json.JSONDecodeError as e:
                print(f"{fg.RED}Fehler beim Parsen des Skripts: {e}{style.RESET}")
                return False

        if "commands" not in script:
            print(f"{fg.RED}Keine 'commands'-Liste im Skript gefunden.{style.RESET}")
            return False

        print(f"{fg.CYAN}Starte Batch-Skript: {script.get('name', 'Unbenannt')}{style.RESET}")
        if script.get("description"):
            print(f"{fg.DIM}Beschreibung: {script['description']}{style.RESET}")

        commands = script["commands"]
        total = len(commands)
        pbar = SimpleProgressBar(total, "Skript-Status")

        for idx, cmd in enumerate(commands, 1):
            desc = cmd.get('description', cmd.get('command', 'Befehl'))
            # pbar.update wird erst am Ende des Schritts gerufen
            if not self._execute_command(cmd):
                pbar.close()
                print(f"\n{fg.RED}Skript abgebrochen bei Schritt {idx}/{total}: {desc}{style.RESET}")
                return False
            pbar.update(1)

        pbar.close()
        print(f"\n{fg.GREEN}✅ Skript erfolgreich abgeschlossen.{style.RESET}")
        return True

    def _execute_command(self, cmd_dict: Dict[str, Any]) -> bool:
        command = cmd_dict.get("command", "")
        action = cmd_dict.get("action", "")
        
        if not command and not action:
            print(f"{fg.RED}Ungültiger Befehl: Weder 'command' noch 'action' vorhanden.{style.RESET}")
            return False

        # Variablen ersetzen: {variable} durch self.variables[variable]
        for key, value in self.variables.items():
            command = command.replace(f"{{{key}}}", str(value))

        # Spezielle Aktionen
        if action == "wait":
            try:
                sec = int(command)
                # print(f"Warte {sec} Sekunden...")
                time.sleep(sec)
                return True
            except:
                print(f"{fg.RED}Ungültige Wartezeit: {command}{style.RESET}")
                return False
        elif action == "confirm":
            if not confirm(command):
                print(f"{fg.YELLOW}Abgebrochen durch Benutzer.{style.RESET}")
                return False
            return True
        elif action == "set_variable":
            if "=" in command:
                var, val = command.split("=", 1)
                self.variables[var.strip()] = val.strip()
                return True
            else:
                print(f"{fg.RED}Ungültiges set_variable Format: {command}{style.RESET}")
                return False
        elif action == "user_input":
            val = input(f"{fg.YELLOW}Eingabe für {command}{style.RESET}: ")
            self.variables[command] = val
            return True
        else:
            # Normaler ADB-Befehl
            serial = self.device_manager.get_current_device()
            if not serial:
                print(f"{fg.RED}Kein Gerät verbunden.{style.RESET}")
                return False
            
            # logger wird hier nicht direkt importiert um zirkuläre Abhängigkeiten zu vermeiden,
            # aber der ADBHandler nutzt ihn bereits intern.
            stdout, stderr, rc = self.adb.run(command, serial)
            
            if rc != 0:
                print(f"{fg.RED}Fehler bei '{command}': {stderr}{style.RESET}")
                return cmd_dict.get("ignore_errors", False)
            else:
                if cmd_dict.get("save_output"):
                    filename = f"batch_output_{get_timestamp()}.txt"
                    save_file(stdout, filename, "logs")
                return True

def show_batch_menu(device_manager, adb, config):
    """Menü für Batch-Verarbeitung (wird in main.py eingebunden)."""
    from utils.ui_helpers import clear_screen, print_header, menu_prompt
    processor = BatchProcessor(adb, device_manager)

    while True:
        clear_screen()
        print_header("Batch-Verarbeitung", "ADB-Skripte ausführen")
        print("1. 📜 Skript ausführen (JSON-Datei)")
        print("2. 📝 Beispiel-Skript erstellen")
        print("3. 📂 Skripte im Ordner anzeigen")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 4))
        if choice == 0:
            break
        elif choice == 1:
            path = input("Pfad zur JSON-Skriptdatei: ").strip()
            if path:
                processor.run_script(path)
                wait_for_enter()
        elif choice == 2:
            create_example_script()
            wait_for_enter()
        elif choice == 3:
            list_scripts()
            wait_for_enter()

def create_example_script():
    """Erstellt ein Beispiel-Skript im aktuellen Verzeichnis."""
    example = {
        "name": "Beispiel-Skript",
        "description": "Zeigt Geräteinfo, wartet, macht Screenshot",
        "commands": [
            {"command": "shell getprop ro.product.model", "description": "Modell abfragen", "save_output": True},
            {"command": "shell dumpsys battery | grep level", "description": "Akkustand"},
            {"action": "wait", "command": "2", "description": "2 Sekunden warten"},
            {"action": "confirm", "command": "Screenshot erstellen?", "description": "Benutzerbestätigung"},
            {"command": "shell screencap -p /sdcard/screen.png", "ignore_errors": False},
            {"command": "pull /sdcard/screen.png ./screenshot_batch.png"},
            {"command": "shell rm /sdcard/screen.png"},
            {"action": "user_input", "command": "benutzername", "description": "Gib einen Namen ein"},
            {"command": "shell echo 'Hallo {benutzername}' > /sdcard/hallo.txt"}
        ]
    }
    filename = "example_script.json"
    with open(filename, 'w') as f:
        json.dump(example, f, indent=2)
    print(f"Beispiel-Skript erstellt: {filename}")

def list_scripts():
    from pathlib import Path
    scripts = list(Path(".").glob("*.json"))
    if not scripts:
        print("Keine JSON-Dateien im aktuellen Ordner gefunden.")
    else:
        print("Gefundene Skripte:")
        for s in scripts:
            print(f" - {s}")

import time
import json
import os
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm
from utils.file_utils import get_timestamp, ensure_dir

MACRO_DIR = "macros"

class MacroRecorder:
    def __init__(self, adb, serial):
        self.adb = adb
        self.serial = serial
        self.events = []
        self.recording = False

    def record_event(self, event_type, **kwargs):
        self.events.append({
            "type": event_type,
            "time": time.time(),
            **kwargs
        })

    def start_recording(self):
        self.events = []
        self.recording = True
        print("Aufnahme gestartet. Führe jetzt Aktionen auf dem Gerät aus.")
        print("Drücke hier Enter, um die Aufnahme zu beenden.")
        input()
        self.recording = False
        print(f"Aufnahme beendet. {len(self.events)} Ereignisse aufgezeichnet.")

    def save_macro(self, name):
        filename = os.path.join(MACRO_DIR, f"{name}.json")
        with open(filename, 'w') as f:
            json.dump(self.events, f, indent=2)
        return filename

    def load_macro(self, name):
        filename = os.path.join(MACRO_DIR, f"{name}.json")
        with open(filename, 'r') as f:
            self.events = json.load(f)

    def play_macro(self, playback_speed=1.0):
        if not self.events:
            print("Keine Ereignisse zum Abspielen.")
            return
        start_time = time.time()
        first_event_time = self.events[0]["time"]
        for event in self.events:
            rel_time = (event["time"] - first_event_time) / playback_speed
            elapsed = time.time() - start_time
            if rel_time > elapsed:
                time.sleep(rel_time - elapsed)
            if event["type"] == "tap":
                x, y = event["x"], event["y"]
                self.adb.run_shell(f"input tap {x} {y}", self.serial)
                print(f"Tap ({x}, {y})")
            elif event["type"] == "swipe":
                self.adb.run_shell(f"input swipe {event['x1']} {event['y1']} {event['x2']} {event['y2']} {event.get('duration', 300)}", self.serial)
            elif event["type"] == "key":
                self.adb.run_shell(f"input keyevent {event['keycode']}", self.serial)
            elif event["type"] == "text":
                self.adb.run_shell(f"input text '{event['text']}'", self.serial)
        print("Makro abgespielt.")

def show_menu(device_manager, adb):
    ensure_dir(MACRO_DIR)
    recorder = None
    while True:
        clear_screen()
        print_header("Makro-Rekorder", "Touch-Eingaben aufzeichnen & abspielen")
        print("1. 🎬 Neue Aufnahme starten")
        print("2. 💾 Aufnahme speichern")
        print("3. 📂 Makro laden")
        print("4. ▶️ Makro abspielen")
        print("5. 📋 Gespeicherte Makros auflisten")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 6))

        if choice == 0:
            break
        elif choice == 1:
            serial = device_manager.get_current_device()
            if not serial:
                continue
            recorder = MacroRecorder(adb, serial)
            recorder.start_recording()
        elif choice == 2:
            if not recorder or not recorder.events:
                print("Keine Aufnahme vorhanden.")
                wait_for_enter()
                continue
            name = input("Name für Makro: ")
            if name:
                path = recorder.save_macro(name)
                print(f"Makro gespeichert: {path}")
            wait_for_enter()
        elif choice == 3:
            files = [f for f in os.listdir(MACRO_DIR) if f.endswith('.json')]
            if not files:
                print("Keine gespeicherten Makros.")
                wait_for_enter()
                continue
            print("Verfügbare Makros:")
            for i, f in enumerate(files):
                print(f"{i+1}. {f}")
            try:
                idx = int(input("Nummer: ")) - 1
                if 0 <= idx < len(files):
                    recorder = MacroRecorder(adb, device_manager.get_current_device())
                    recorder.load_macro(files[idx][:-5])
                    print(f"Makro {files[idx]} geladen.")
            except:
                pass
            wait_for_enter()
        elif choice == 4:
            if not recorder or not recorder.events:
                print("Kein Makro geladen.")
                wait_for_enter()
                continue
            speed = input("Abspielgeschwindigkeit (1 = normal, 2 = doppelt, 0.5 = halb) [1]: ") or "1"
            try:
                speed = float(speed)
                recorder.play_macro(speed)
            except:
                print("Ungültige Geschwindigkeit.")
            wait_for_enter()
        elif choice == 5:
            files = os.listdir(MACRO_DIR)
            if files:
                print("Gespeicherte Makros:")
                for f in files:
                    size = os.path.getsize(os.path.join(MACRO_DIR, f)) // 1024
                    print(f" - {f} ({size} KB)")
            else:
                print("Keine Makros gefunden.")
            wait_for_enter()

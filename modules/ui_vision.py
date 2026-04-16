from core.adb_handler import ADBHandler
from core.device_manager import DeviceManager
from services.vision_service import VisionService
from utils.ui_helpers import print_header, menu_prompt, wait_for_enter, confirm


def show_menu(device_manager: DeviceManager, adb: ADBHandler, config: dict) -> None:
    screenshot_dir = config.get("global", {}).get("screenshot_path", "./screenshots")
    service = VisionService(device_manager, adb, screenshot_dir=screenshot_dir)

    while True:
        print_header("Vision / OCR", "Texterkennung und UI-Zielsuche")
        print("1. Screenshot aufnehmen und Text suchen")
        print("2. Screenshot aufnehmen, Text markieren und speichern")
        print("3. Text suchen und antippen")
        print("0. Zurück")

        choice = menu_prompt("Option wählen", range(0, 4))
        if choice == 0:
            break

        query = input("Suchtext: ").strip()
        if not query:
            print("Kein Suchtext eingegeben.")
            wait_for_enter()
            continue

        image_path = service.take_screenshot(filename="ui_vision_capture.png")
        matches = service.find_text(query, image_path)

        print(f"Treffer: {len(matches)}")
        for idx, match in enumerate(matches, 1):
            print(f"{idx}. {match.text} @ ({match.left}, {match.top}) {match.width}x{match.height} conf={match.confidence}")

        if choice == 2 and matches:
            annotated = service.annotate_matches(image_path, matches, output_name="ui_vision_annotated.png")
            print(f"Annotierter Screenshot: {annotated}")

        elif choice == 3:
            if not matches:
                print("Kein Treffer zum Antippen gefunden.")
            else:
                best = sorted(matches, key=lambda m: m.confidence, reverse=True)[0]
                x = best.left + best.width // 2
                y = best.top + best.height // 2
                print(f"Bester Treffer: {best.text} @ ({x}, {y})")
                if confirm("Jetzt tippen?"):
                    out, err, rc = adb.run_shell(f"input tap {x} {y}")
                    if rc == 0:
                        print("Tap erfolgreich gesendet.")
                    else:
                        print(f"Tap fehlgeschlagen: {err}")

        wait_for_enter()

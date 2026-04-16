from services.vision_service_v2 import VisionServiceV2
from utils.ui_helpers import print_header, menu_prompt, wait_for_enter, confirm


def show_menu(device_manager, adb, config):
    screenshot_dir = config.get("global", {}).get("screenshot_path", "./screenshots")
    service = VisionServiceV2(device_manager, adb, screenshot_dir=screenshot_dir)

    while True:
        print_header("Vision / OCR v2", "Robuste Textsuche, Annotation und Tap")
        print("1. Screenshot aufnehmen und Text suchen")
        print("2. Text suchen und Treffer annotieren")
        print("3. Besten Treffer suchen und antippen")
        print("0. Zurück")

        choice = menu_prompt("Option wählen", range(0, 4))
        if choice == 0:
            break

        query = input("Suchtext: ").strip()
        if not query:
            print("Kein Suchtext eingegeben.")
            wait_for_enter()
            continue

        image_path = service.take_screenshot(filename="ui_vision_v2_capture.png")

        if choice in (1, 2):
            matches = service.find_text(query, image_path)
            print(f"Treffer: {len(matches)}")
            for idx, match in enumerate(matches, 1):
                print(f"{idx}. {match.text} @ ({match.left}, {match.top}) {match.width}x{match.height} conf={match.confidence} score={match.score}")
            if choice == 2 and matches:
                annotated = service.annotate_matches(image_path, matches, output_name="ui_vision_v2_annotated.png")
                print(f"Annotierter Screenshot: {annotated}")

        elif choice == 3:
            match = service.best_match(query, image_path)
            if not match:
                print("Kein geeigneter Treffer gefunden.")
            else:
                x = match.left + match.width // 2
                y = match.top + match.height // 2
                print(f"Bester Treffer: {match.text} @ ({x}, {y}) conf={match.confidence} score={match.score}")
                if confirm("Jetzt tippen?"):
                    out, err, rc = adb.run_shell(f"input tap {x} {y}")
                    if rc == 0:
                        print("Tap erfolgreich gesendet.")
                    else:
                        print(f"Tap fehlgeschlagen: {err}")

        wait_for_enter()

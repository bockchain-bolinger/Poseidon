from services.monitoring_service_v2 import MonitoringServiceV2
from utils.ui_helpers import print_header, menu_prompt, wait_for_enter


def show_menu(device_manager, adb, config):
    export_dir = config.get("global", {}).get("log_path", "./logs")
    service = MonitoringServiceV2(device_manager, adb, export_dir=export_dir)

    while True:
        print_header("Monitoring v2", "Gerätemetriken mit Export")
        print("1. Einmalige Snapshot-Erfassung")
        print("2. Snapshot + CSV-Export")
        print("3. Snapshot + JSONL-Export")
        print("4. Snapshot + beide Exporte")
        print("0. Zurück")

        choice = menu_prompt("Option wählen", range(0, 5))
        if choice == 0:
            break

        metrics = service.collect_once()
        data = metrics.to_dict()

        print("-" * 50)
        for key, value in data.items():
            print(f"{key}: {value}")

        if choice == 2:
            path = service.export_csv(metrics)
            print(f"CSV exportiert nach: {path}")
        elif choice == 3:
            path = service.export_jsonl(metrics)
            print(f"JSONL exportiert nach: {path}")
        elif choice == 4:
            csv_path = service.export_csv(metrics)
            jsonl_path = service.export_jsonl(metrics)
            print(f"CSV exportiert nach: {csv_path}")
            print(f"JSONL exportiert nach: {jsonl_path}")

        wait_for_enter()

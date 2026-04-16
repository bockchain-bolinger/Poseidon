from core.adb_handler import ADBHandler
from core.device_manager import DeviceManager
from services.monitoring_service import MonitoringService
from utils.ui_helpers import print_header, menu_prompt, wait_for_enter


def show_menu(device_manager: DeviceManager, adb: ADBHandler, config: dict) -> None:
    service = MonitoringService(device_manager, adb)

    while True:
        print_header("Monitoring", "Gerätemetriken und Live-Status")
        print("1. Einmalige Snapshot-Erfassung")
        print("2. Snapshot mit Rohdaten anzeigen")
        print("0. Zurück")

        choice = menu_prompt("Option wählen", range(0, 3))
        if choice == 0:
            break

        metrics = service.collect_once()
        data = metrics.to_dict()

        print("-" * 50)
        print(f"Zeitpunkt: {data.get('timestamp')}")
        print(f"Gerät: {data.get('serial')}")
        print(f"Akku: {data.get('battery_level')}%")
        print(f"Akku-Temperatur: {data.get('battery_temp_c')} °C")
        print(f"RAM genutzt: {data.get('memory_used_mb')} MB")
        print(f"RAM frei: {data.get('memory_free_mb')} MB")
        print(f"CPU-Last: {data.get('cpu_load')}")

        if choice == 2:
            print("\nRohdaten:")
            for key, value in data.items():
                print(f"- {key}: {value}")

        wait_for_enter()

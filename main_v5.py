#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.device_manager import DeviceManager
from core.adb_handler import ADBHandler
from core.plugin_manager import PluginManager
from core.batch_processor import show_batch_menu
from core.updater import check_for_updates, show_update_menu
from core.logger import logger

from utils.ansi_colors import fg, style, init as color_init, set_theme
from utils.ui_helpers import clear_screen, print_header, menu_prompt, confirm, wait_for_enter
from utils.i18n import get_text, set_language, get_available_languages
from utils.dependency_checker import check_all_dependencies

from modules import (
    info,
    apps,
    media,
    control,
    network,
    system,
    logcat,
    backup,
    developer,
    security,
    macro,
    dumpsys_gui,
    whatsapp_backup,
    dashboard,
    files,
    analyzer,
    monitoring_v2,
    ui_vision_v2,
)

CONFIG_PATH = BASE_DIR / "config.json"
LOGO_PATH = BASE_DIR / "assets" / "logo.txt"


def default_config() -> Dict[str, Any]:
    return {
        "version": "5.0-dev",
        "language": "de",
        "theme": "light",
        "auto_update_check": True,
        "license_check_enabled": False,
        "global": {
            "backup_path": "./backups",
            "screenshot_path": "./screenshots",
            "record_duration": 30,
            "scrcpy_path": "scrcpy",
            "log_path": "./logs",
        },
        "devices": {},
    }


def load_config() -> Dict[str, Any]:
    config = default_config()
    if not CONFIG_PATH.exists():
        return config
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden von {CONFIG_PATH}: {e}")
        return config
    merged = default_config()
    merged.update({k: v for k, v in raw.items() if k != "global"})
    merged["global"].update(raw.get("global", {}))
    merged["devices"] = raw.get("devices", {})
    return merged


def save_config(config: Dict[str, Any]) -> None:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def check_license_safe(config: Dict[str, Any]) -> bool:
    if not config.get("license_check_enabled", False):
        return True
    logger.warning("Lizenzprüfung ist aktiviert, aber noch nicht implementiert. Start wird erlaubt.")
    return True


def ensure_runtime_dirs(config: Dict[str, Any]) -> None:
    Path(config["global"].get("backup_path", "./backups")).mkdir(parents=True, exist_ok=True)
    Path(config["global"].get("screenshot_path", "./screenshots")).mkdir(parents=True, exist_ok=True)
    Path(config["global"].get("log_path", "./logs")).mkdir(parents=True, exist_ok=True)
    (BASE_DIR / "plugins").mkdir(parents=True, exist_ok=True)


def run_dependency_checks() -> None:
    results, warnings = check_all_dependencies()
    if not results.get("adb"):
        logger.critical("'adb' wurde nicht im Systempfad gefunden. Abbruch.")
        print_header("POSEIDON", "v5.0-dev - ADB Power Tool")
        print(f"{fg.RED}KRITISCHER FEHLER: 'adb' wurde nicht gefunden!{style.RESET}")
        sys.exit(1)
    if warnings:
        print_header("POSEIDON", "Abhängigkeits-Warnung")
        for warning in warnings:
            print(f"{fg.YELLOW}[!] {warning}{style.RESET}")
        print("-" * 50)
        if sys.stdin.isatty() and not confirm("Möchten Sie trotzdem fortfahren?"):
            sys.exit(0)


def show_logo() -> None:
    if LOGO_PATH.exists():
        try:
            with open(LOGO_PATH, "r", encoding="utf-8") as f:
                print(fg.CYAN + f.read() + style.RESET)
                return
        except Exception:
            pass
    print_header("POSEIDON", "v5.0-dev - ADB Power Tool")


def auto_check_updates(config: Dict[str, Any]) -> None:
    if not config.get("auto_update_check", True):
        return
    try:
        has_update, latest = check_for_updates(config.get("version", "5.0-dev"))
        if has_update:
            print(f"{fg.YELLOW}{get_text('update_available').format(version=latest)}{style.RESET}")
    except Exception as e:
        logger.error(f"Fehler beim Update-Check: {e}")


def build_context() -> Tuple[Dict[str, Any], DeviceManager, ADBHandler, PluginManager]:
    config = load_config()
    ensure_runtime_dirs(config)
    set_language(config.get("language", "de"))
    set_theme(config.get("theme", "light"))
    check_license_safe(config)
    device_manager = DeviceManager(config)
    adb = ADBHandler(device_manager)
    plugin_manager = PluginManager()
    plugin_manager.discover_plugins()
    return config, device_manager, adb, plugin_manager


def settings_menu(config: Dict[str, Any], device_manager: DeviceManager) -> None:
    while True:
        clear_screen()
        print_header(get_text("settings_title"), get_text("settings_subtitle"))
        print(f"1. {get_text('setting_backup_path')}: {config['global']['backup_path']}")
        print(f"2. {get_text('setting_screenshot_path')}: {config['global']['screenshot_path']}")
        print(f"3. {get_text('setting_record_duration')}: {config['global']['record_duration']} s")
        print(f"4. {get_text('setting_scrcpy_path')}: {config['global']['scrcpy_path']}")
        print(f"5. {get_text('setting_theme')}: {config.get('theme', 'light')}")
        print(f"6. {get_text('setting_language')}: {config.get('language', 'de')}")
        print(f"7. {get_text('setting_auto_update')}: {'an' if config.get('auto_update_check', True) else 'aus'}")
        print(f"8. Log-Pfad: {config['global'].get('log_path', './logs')}")
        print("0. " + get_text("back"))
        choice = menu_prompt(get_text("choose_option"), range(0, 9))
        if choice == 0:
            break
        elif choice == 1:
            new_path = input(get_text("new_backup_path") + ": ").strip()
            if new_path:
                config["global"]["backup_path"] = new_path
        elif choice == 2:
            new_path = input(get_text("new_screenshot_path") + ": ").strip()
            if new_path:
                config["global"]["screenshot_path"] = new_path
        elif choice == 3:
            try:
                config["global"]["record_duration"] = int(input(get_text("new_record_duration") + ": ").strip())
            except ValueError:
                print(get_text("invalid_input"))
        elif choice == 4:
            new_scrcpy = input(get_text("new_scrcpy_path") + ": ").strip()
            if new_scrcpy:
                config["global"]["scrcpy_path"] = new_scrcpy
        elif choice == 5:
            new_theme = input(get_text("theme_prompt") + " (light/dark): ").strip().lower()
            if new_theme in ("light", "dark"):
                config["theme"] = new_theme
                set_theme(new_theme)
        elif choice == 6:
            langs = get_available_languages()
            if langs:
                print(get_text("available_languages") + ": " + ", ".join(langs))
                new_lang = input(get_text("language_prompt") + ": ").strip()
                if new_lang in langs:
                    config["language"] = new_lang
                    set_language(new_lang)
        elif choice == 7:
            config["auto_update_check"] = not config.get("auto_update_check", True)
        elif choice == 8:
            new_log_path = input("Neuer Log-Pfad: ").strip()
            if new_log_path:
                config["global"]["log_path"] = new_log_path
        save_config(config)
        wait_for_enter()


def render_main_menu(device_manager: DeviceManager) -> None:
    print()
    print(f"{fg.YELLOW}{get_text('main_menu')}{style.RESET}")
    print("=" * 50)
    device = device_manager.get_current_device()
    if device:
        print(f"{fg.GREEN}{get_text('device_connected').format(serial=device)}{style.RESET}")
    else:
        print(f"{fg.RED}{get_text('no_device')}{style.RESET}")
    print("\n" + get_text("categories"))
    print(" 1. 📱 " + get_text("menu_device_info"))
    print(" 2. 📦 " + get_text("menu_app_management"))
    print(" 3. 🎥 " + get_text("menu_media"))
    print(" 4. 🎮 " + get_text("menu_control"))
    print(" 5. 🌐 " + get_text("menu_network"))
    print(" 6. ⚙️ " + get_text("menu_system"))
    print(" 7. 🛠️ " + get_text("menu_developer"))
    print(" 8. 🔒 " + get_text("menu_security"))
    print(" 9. 📋 " + get_text("menu_logcat"))
    print("10. 💾 " + get_text("menu_backup"))
    print("11. ⚙️ " + get_text("menu_settings"))
    print("12. 🎬 " + get_text("menu_macro"))
    print("13. 🧩 " + get_text("menu_plugins"))
    print("14. 📦 " + get_text("menu_batch"))
    print("15. 🖥️ " + get_text("menu_dumpsys"))
    print("16. 💬 WhatsApp Backup")
    print("17. 🔄 Update")
    print("18. 📊 " + get_text("menu_dashboard"))
    print("19. 📁 " + get_text("menu_files"))
    print("20. 🕵️ " + get_text("menu_analyzer"))
    print("21. 📈 Monitoring v2")
    print("22. 👁️ Vision / OCR v2")
    print(" 0. ❌ " + get_text("exit"))


def handle_menu_choice(choice: int, config: Dict[str, Any], device_manager: DeviceManager, adb: ADBHandler, plugin_manager: PluginManager) -> bool:
    if choice == 0:
        if confirm(get_text("confirm_exit")):
            print(f"{fg.GREEN}{get_text('goodbye')}{style.RESET}")
            return False
    elif choice == 1:
        info.show_menu(device_manager, adb)
    elif choice == 2:
        apps.show_menu(device_manager, adb)
    elif choice == 3:
        media.show_menu(device_manager, adb, config["global"])
    elif choice == 4:
        control.show_menu(device_manager, adb)
    elif choice == 5:
        network.show_menu(device_manager, adb, config)
    elif choice == 6:
        system.show_menu(device_manager, adb)
    elif choice == 7:
        developer.show_menu(device_manager, adb)
    elif choice == 8:
        security.show_menu(device_manager, adb)
    elif choice == 9:
        logcat.show_menu(device_manager, adb)
    elif choice == 10:
        backup.show_menu(device_manager, adb, config["global"])
    elif choice == 11:
        settings_menu(config, device_manager)
    elif choice == 12:
        macro.show_menu(device_manager, adb)
    elif choice == 13:
        plugin_manager.show_plugin_menu(device_manager, adb, config)
    elif choice == 14:
        show_batch_menu(device_manager, adb, config)
    elif choice == 15:
        dumpsys_gui.show_menu(device_manager, adb)
    elif choice == 16:
        whatsapp_backup.show_menu(device_manager, adb)
    elif choice == 17:
        show_update_menu(device_manager, adb, config)
    elif choice == 18:
        dashboard.show_dashboard(device_manager, adb)
    elif choice == 19:
        files.show_manager(device_manager, adb, config["global"])
    elif choice == 20:
        analyzer.show_menu(device_manager, adb)
    elif choice == 21:
        monitoring_v2.show_menu(device_manager, adb, config)
    elif choice == 22:
        ui_vision_v2.show_menu(device_manager, adb, config)
    return True


def main() -> None:
    color_init()
    logger.info("Poseidon v5.0-dev wird gestartet...")
    run_dependency_checks()
    config, device_manager, adb, plugin_manager = build_context()
    auto_check_updates(config)
    show_logo()
    running = True
    while running:
        render_main_menu(device_manager)
        choice = menu_prompt(get_text("choose_category"), range(0, 23))
        running = handle_menu_choice(choice, config, device_manager, adb, plugin_manager)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{fg.YELLOW}{get_text('aborted')}{style.RESET}")
        sys.exit(0)
    except Exception as e:
        logger.exception("Kritischer Fehler im Hauptprogramm")
        print(f"\n{fg.RED}Ein unerwarteter Fehler ist aufgetreten: {e}{style.RESET}")
        sys.exit(1)

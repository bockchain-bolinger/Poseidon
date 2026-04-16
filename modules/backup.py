import os
import time
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm, SimpleProgressBar
from utils.file_utils import ensure_dir, get_timestamp
from utils.ansi_colors import fg, style
from utils.i18n import get_text

def show_menu(device_manager, adb, config):
    while True:
        clear_screen()
        print_header(get_text("backup_title"), get_text("backup_subtitle"))
        print("1. 💾 " + get_text("backup_full"))
        print("2. 📦 " + get_text("backup_app"))
        print("3. 🔄 " + get_text("backup_restore"))
        print("4. 📋 " + get_text("backup_list"))
        print("0. " + get_text("back"))

        choice = menu_prompt(get_text("choose_option"), range(0, 5))

        if choice == 0:
            break
        elif choice == 1:
            full_backup(device_manager, adb, config)
        elif choice == 2:
            app_backup(device_manager, adb, config)
        elif choice == 3:
            restore_backup(device_manager, adb, config)
        elif choice == 4:
            list_backups(config)

def full_backup(device_manager, adb, config):
    serial = device_manager.get_current_device()
    if not serial:
        return
    ensure_dir(config['backup_path'])
    filename = f"full_backup_{get_timestamp()}.ab"
    path = os.path.join(config['backup_path'], filename)
    print(f"{fg.YELLOW}{get_text('backup_start_full')}{style.RESET}")
    
    pbar = SimpleProgressBar(1, get_text("backup_full"))
    adb.run(f"backup -f \"{path}\" -all -apk -shared", serial)
    pbar.update(1)
    pbar.close()
    
    print(f"{fg.GREEN}{get_text('backup_success', path=path)}{style.RESET}")
    wait_for_enter()

def app_backup(device_manager, adb, config):
    serial = device_manager.get_current_device()
    if not serial:
        return
    package = input(get_text("enter_package"))
    if not package:
        return
    ensure_dir(config['backup_path'])
    filename = f"backup_{package}_{get_timestamp()}.ab"
    path = os.path.join(config['backup_path'], filename)
    print(f"{fg.YELLOW}{get_text('backup_start_app', package=package)}{style.RESET}")
    
    pbar = SimpleProgressBar(1, f"{get_text('backup_app')} ({package})")
    adb.run(f"backup -f \"{path}\" -apk {package}", serial)
    pbar.update(1)
    pbar.close()
    
    print(f"{fg.GREEN}{get_text('backup_success', path=path)}{style.RESET}")
    wait_for_enter()

def restore_backup(device_manager, adb, config):
    serial = device_manager.get_current_device()
    if not serial:
        return
    backups = [f for f in os.listdir(config['backup_path']) if f.endswith('.ab')]
    if not backups:
        print(get_text("no_backups_found"))
        wait_for_enter()
        return
    print(get_text("available_backups"))
    for i, f in enumerate(backups):
        print(f"{i+1}. {f}")
    try:
        choice = int(input(get_text("choose_backup_restore") + " ")) - 1
        if 0 <= choice < len(backups):
            path = os.path.join(config['backup_path'], backups[choice])
            print(f"{fg.YELLOW}{get_text('restore_start', file=backups[choice])}{style.RESET}")
            
            pbar = SimpleProgressBar(1, get_text("backup_restore"))
            adb.run(f"restore \"{path}\"", serial)
            pbar.update(1)
            pbar.close()
            
            print(f"{fg.GREEN}{get_text('restore_success')}{style.RESET}")
    except Exception as e:
        print(f"{fg.RED}{get_text('invalid_input')}: {e}{style.RESET}")
    wait_for_enter()

def list_backups(config):
    path = config['backup_path']
    if not os.path.exists(path):
        print(get_text("backup_dir_missing"))
        wait_for_enter()
        return
    files = os.listdir(path)
    if files:
        print(get_text("available_backups"))
        for f in files:
            full_path = os.path.join(path, f)
            if os.path.isfile(full_path):
                size = os.path.getsize(full_path) // 1024
                print(f" - {f} ({size} KB)")
    else:
        print(get_text("no_backups_found"))
    wait_for_enter()

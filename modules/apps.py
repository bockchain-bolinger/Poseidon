import os
from utils.ui_helpers import show_menu_generic, wait_for_enter, confirm, show_progress
from utils.file_utils import ensure_dir, get_timestamp, save_file
from utils.ansi_colors import fg, style
from utils.decorators import require_device
from utils.i18n import get_text

def show_menu(device_manager, adb):
    options = [
        ("📋", "apps_list", list_apps),
        ("🔍", "apps_info", app_info),
        ("💾", "apps_backup", backup_app),
        ("📦", "apps_install", install_apk),
        ("🗑️", "apps_uninstall", uninstall_app),
        ("📤", "apps_extract", extract_apk),
        ("⚡", "apps_batch_install", batch_install),
        ("🧹", "apps_clear_cache", clear_cache),
        ("🔐", "apps_permissions", app_permissions),
        ("🗑️", "apps_batch_uninstall", batch_uninstall),
        ("📋", "apps_source", show_install_source),
        ("🛒", "apps_playstore", open_playstore)
    ]
    show_menu_generic("apps_title", "apps_subtitle", options, device_manager, adb)

@require_device
def list_apps(device_manager, adb, save_to_file=False):
    serial = device_manager.get_current_device()
    print(get_text("loading_app_list"))
    out, _, _ = adb.run_shell("pm list packages -f -3", serial)
    apps = out.splitlines()
    if save_to_file:
        filename = f"app_list_{get_timestamp()}.txt"
        save_file("\n".join(apps), filename, "backups")
        print(get_text("saved_to", path=f"backups/{filename}"))
    else:
        for app in apps[:100]:
            print(app)
        if len(apps) > 100:
            print(f"... and {len(apps)-100} more.")
    wait_for_enter()

@require_device
def app_info(device_manager, adb):
    serial = device_manager.get_current_device()
    package = input(get_text("enter_package"))
    if not package:
        return
    out, _, _ = adb.run_shell(f"dumpsys package {package}", serial)
    print("\n--- App-Info ---")
    for line in out.splitlines():
        if any(x in line for x in ["versionName", "versionCode", "install", "permission"]):
            print(line.strip())
    wait_for_enter()

@require_device
def backup_app(device_manager, adb):
    serial = device_manager.get_current_device()
    package = input(get_text("enter_package"))
    if not package:
        return
    print(get_text("backup_start_app", package=package))
    out, _, _ = adb.run(f"backup -f backup_{package}.ab {package}", serial)
    print(get_text("wait_for_enter_msg"))
    wait_for_enter()

@require_device
def install_apk(device_manager, adb):
    serial = device_manager.get_current_device()
    path = input("APK Path: ")
    if not os.path.exists(path):
        print(get_text("invalid_input"))
        wait_for_enter()
        return
    print(f"Installing {path}...")
    out, err, rc = adb.run(f"install -r \"{path}\"", serial)
    print(out)
    print(err)
    wait_for_enter()

@require_device
def uninstall_app(device_manager, adb):
    serial = device_manager.get_current_device()
    package = input(get_text("enter_package"))
    if not package or not confirm(f"Uninstall {package}?"):
        return
    out, err, rc = adb.run(f"uninstall {package}", serial)
    print(out)
    print(err)
    wait_for_enter()

@require_device
def extract_apk(device_manager, adb):
    serial = device_manager.get_current_device()
    package = input(get_text("enter_package"))
    if not package:
        return
    out, _, _ = adb.run_shell(f"pm path {package}", serial)
    if not out.startswith("package:"):
        print(get_text("app_not_found"))
        wait_for_enter()
        return
    apk_path = out.split(":")[1].strip()
    print(get_text("apk_path", path=apk_path))
    dest = f"extracted_{package}.apk"
    adb.run(f"pull {apk_path} {dest}", serial)
    print(get_text("extracted_to", path=dest))
    wait_for_enter()

@require_device
def batch_install(device_manager, adb):
    folder = input("Folder with APK files: ")
    if not os.path.isdir(folder):
        print(get_text("invalid_input"))
        return
    apks = [f for f in os.listdir(folder) if f.endswith('.apk')]
    if not apks:
        print("No APKs found.")
        return
    print(f"Found APKs: {len(apks)}")
    if not confirm("Install?"):
        return
    
    for apk in show_progress(apks, get_text("installing_apps")):
        full = os.path.join(folder, apk)
        adb.run(f"install -r \"{full}\"", device_manager.get_current_device())
    wait_for_enter()

@require_device
def clear_cache(device_manager, adb):
    serial = device_manager.get_current_device()
    package = input(get_text("enter_package"))
    if not package:
        return
    out, err, rc = adb.run_shell(f"pm clear {package}", serial)
    print(out)
    wait_for_enter()

@require_device
def app_permissions(device_manager, adb):
    serial = device_manager.get_current_device()
    package = input(get_text("enter_package"))
    if not package:
        return
    out, _, _ = adb.run_shell(f"dumpsys package {package} | grep permission", serial)
    print("Permissions:")
    print(out)
    wait_for_enter()

@require_device
def batch_uninstall(device_manager, adb):
    serial = device_manager.get_current_device()
    print("Batch Uninstall: Enter package names (one per line, empty line to finish):")
    packages = []
    while True:
        pkg = input("Package: ").strip()
        if not pkg:
            break
        packages.append(pkg)
    if not packages:
        return
    print(f"Apps to uninstall: {', '.join(packages)}")
    if not confirm("Really proceed?"):
        return
        
    for pkg in show_progress(packages, get_text("uninstalling_apps")):
        adb.run(f"uninstall {pkg}", serial)
    wait_for_enter()

@require_device
def show_install_source(device_manager, adb):
    serial = device_manager.get_current_device()
    out, _, _ = adb.run_shell("pm list packages -f -i", serial)
    print("Apps with install source:")
    print(out)
    if confirm(get_text("save_to_file")):
        filename = f"app_sources_{get_timestamp()}.txt"
        save_file(out, filename, "backups")
        print(get_text("saved_to", path=f"backups/{filename}"))
    wait_for_enter()

@require_device
def open_playstore(device_manager, adb):
    serial = device_manager.get_current_device()
    package = input(get_text("enter_package"))
    if not package:
        return
    adb.run_shell(f"am start -a android.intent.action.VIEW -d market://details?id={package}", serial)
    print("Play Store should open.")
    wait_for_enter()

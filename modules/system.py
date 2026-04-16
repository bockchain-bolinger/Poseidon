from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm

def show_menu(device_manager, adb):
    while True:
        clear_screen()
        print_header("System & Tweaks", "Systemeinstellungen anpassen")
        print("1. 🔄 System UI neu starten")
        print("2. ⏱️ Bildschirm-Off-Time ändern")
        print("3. 🎨 Animationsskalierung anpassen")
        print("4. 📊 FPS und GPU-Overlay anzeigen")
        print("5. 💤 Doze-Modus testen")
        print("6. ℹ️ Bootloader-Info")
        print("7. 🔓 adb root / remount (nur gerootet)")
        print("8. 📱 Gerät neu starten")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 9))

        if choice == 0:
            break
        elif choice == 1:
            restart_systemui(device_manager, adb)
        elif choice == 2:
            set_screen_timeout(device_manager, adb)
        elif choice == 3:
            set_animations(device_manager, adb)
        elif choice == 4:
            show_overlay(device_manager, adb)
        elif choice == 5:
            test_doze(device_manager, adb)
        elif choice == 6:
            bootloader_info(device_manager, adb)
        elif choice == 7:
            root_remount(device_manager, adb)
        elif choice == 8:
            reboot_device(device_manager, adb)

def restart_systemui(device_manager, adb):
    serial = device_manager.get_current_device()
    if serial:
        adb.run_shell("pkill -f com.android.systemui", serial)
        print("System UI neugestartet.")
    wait_for_enter()

def set_screen_timeout(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    timeout = input("Timeout in ms (z.B. 30000 = 30s, 0 = nie): ")
    if timeout:
        adb.run_shell(f"settings put system screen_off_timeout {timeout}", serial)
        print("Timeout gesetzt.")
    wait_for_enter()

def set_animations(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    scale = input("Skalierungsfaktor (0 = aus, 1 = normal): ")
    if scale:
        adb.run_shell(f"settings put global window_animation_scale {scale}", serial)
        adb.run_shell(f"settings put global transition_animation_scale {scale}", serial)
        adb.run_shell(f"settings put global animator_duration_scale {scale}", serial)
        print("Animationsskalierung gesetzt.")
    wait_for_enter()

def show_overlay(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    # Entwickleroptionen: Profil-HWUI Rendering
    adb.run_shell("setprop debug.hwui.profile true", serial)
    print("Profil-Overlay aktiviert. Auf dem Gerät sollte es jetzt angezeigt werden.")
    wait_for_enter()

def test_doze(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    print("1. Doze-Modus erzwingen")
    print("2. Doze beenden")
    sub = menu_prompt("Wahl", [1,2])
    if sub == 1:
        adb.run_shell("dumpsys deviceidle enable", serial)
        adb.run_shell("dumpsys deviceidle force-idle", serial)
        print("Doze erzwungen.")
    else:
        adb.run_shell("dumpsys deviceidle disable", serial)
        print("Doze deaktiviert.")
    wait_for_enter()

def bootloader_info(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    out, _, _ = adb.run("get-state", serial)
    print(f"Gerätestatus: {out}")
    wait_for_enter()

def root_remount(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    adb.run("root", serial)
    time.sleep(2)
    out, _, _ = adb.run("remount", serial)
    print(out)
    wait_for_enter()

def reboot_device(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    mode = input("Modus (normal, bootloader, recovery) [normal]: ") or "normal"
    if mode == "normal":
        adb.run("reboot", serial)
    elif mode == "bootloader":
        adb.run("reboot bootloader", serial)
    elif mode == "recovery":
        adb.run("reboot recovery", serial)
    else:
        print("Unbekannter Modus.")
    wait_for_enter()
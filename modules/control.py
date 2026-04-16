import time
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm

def show_menu(device_manager, adb):
    while True:
        clear_screen()
        print_header("Steuerung & Automatisierung", "Gerät fernsteuern")
        print("1. 🔑 Gerät sperren")
        print("2. 📱 Gerät entsperren (mit PIN/Muster)")
        print("3. 🏠 Home-Taste")
        print("4. 🔙 Zurück-Taste")
        print("5. 📋 Multitasking-Taste")
        print("6. 🔉 Lautstärke ändern")
        print("7. ⌨️ Text eingeben")
        print("8. 👆 Touch-Ereignis senden (x y)")
        print("9. 📲 Wischen simulieren")
        print("10. 🎮 Makro aufzeichnen/abspielen (siehe Makro-Modul)")
        print("11. 🔍 Gerät orten (klingeln lassen)")
        print("12. 🕹️ Google Assistant starten")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 13))

        if choice == 0:
            break
        elif choice == 1:
            lock_device(device_manager, adb)
        elif choice == 2:
            unlock_device(device_manager, adb)
        elif choice == 3:
            press_key(device_manager, adb, "KEYCODE_HOME")
        elif choice == 4:
            press_key(device_manager, adb, "KEYCODE_BACK")
        elif choice == 5:
            press_key(device_manager, adb, "KEYCODE_APP_SWITCH")
        elif choice == 6:
            adjust_volume(device_manager, adb)
        elif choice == 7:
            input_text(device_manager, adb)
        elif choice == 8:
            tap(device_manager, adb)
        elif choice == 9:
            swipe(device_manager, adb)
        elif choice == 10:
            print("Bitte nutze das separate Makro-Modul (Hauptmenü Punkt 12).")
            wait_for_enter()
        elif choice == 11:
            ring_device(device_manager, adb)
        elif choice == 12:
            start_assistant(device_manager, adb)

def lock_device(device_manager, adb):
    serial = device_manager.get_current_device()
    if serial:
        adb.run_shell("input keyevent KEYCODE_POWER", serial)
        print("Gerät gesperrt.")
    wait_for_enter()

def unlock_device(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    adb.run_shell("input keyevent KEYCODE_POWER", serial)
    time.sleep(1)
    adb.run_shell("input swipe 300 1000 300 300", serial)
    print("Wischbewegung ausgeführt. Falls PIN nötig, manuell eingeben.")
    wait_for_enter()

def press_key(device_manager, adb, keycode):
    serial = device_manager.get_current_device()
    if serial:
        adb.run_shell(f"input keyevent {keycode}", serial)
    wait_for_enter()

def adjust_volume(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    print("1. Lauter")
    print("2. Leiser")
    print("3. Stumm")
    sub = menu_prompt("Wahl", [1,2,3])
    if sub == 1:
        adb.run_shell("input keyevent KEYCODE_VOLUME_UP", serial)
    elif sub == 2:
        adb.run_shell("input keyevent KEYCODE_VOLUME_DOWN", serial)
    elif sub == 3:
        adb.run_shell("input keyevent KEYCODE_VOLUME_MUTE", serial)
    wait_for_enter()

def input_text(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    text = input("Text zum Eingeben: ")
    adb.run_shell(f"input text '{text}'", serial)
    wait_for_enter()

def tap(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    x = input("X-Koordinate: ")
    y = input("Y-Koordinate: ")
    if x and y:
        adb.run_shell(f"input tap {x} {y}", serial)
    wait_for_enter()

def swipe(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    x1 = input("Start X: ")
    y1 = input("Start Y: ")
    x2 = input("Ende X: ")
    y2 = input("Ende Y: ")
    duration = input("Dauer (ms) [300]: ") or "300"
    adb.run_shell(f"input swipe {x1} {y1} {x2} {y2} {duration}", serial)
    wait_for_enter()

def ring_device(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    print("Simuliere Anruf (benötigt entsprechende App/Intent)")
    wait_for_enter()

def start_assistant(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    adb.run_shell("am start -a android.intent.action.VOICE_COMMAND", serial)
    print("Google Assistant gestartet.")
    wait_for_enter()
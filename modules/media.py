import os
import subprocess
import time
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm
from utils.file_utils import get_timestamp, ensure_dir

def show_menu(device_manager, adb, config):
    while True:
        clear_screen()
        print_header("Medien & Bildschirm", "Screenshots, Aufnahmen, Mirroring")
        print("1. 📸 Screenshot erstellen")
        print("2. 🎥 Bildschirmaufnahme (Video)")
        print("3. 🖥️ Bildschirm spiegeln (scrcpy)")
        print("4. 🎞️ GIF aus Aufnahme erstellen (benötigt ffmpeg)")
        print("5. ⏱️ Screenshot mit Verzögerung")
        print("6. 📸 Serien-Screenshots")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 7))

        if choice == 0:
            break
        elif choice == 1:
            take_screenshot(device_manager, adb, config)
        elif choice == 2:
            record_screen(device_manager, adb, config)
        elif choice == 3:
            mirror_screen(device_manager, config)
        elif choice == 4:
            create_gif(device_manager, adb, config)
        elif choice == 5:
            delayed_screenshot(device_manager, adb, config)
        elif choice == 6:
            burst_screenshots(device_manager, adb, config)

def take_screenshot(device_manager, adb, config):
    serial = device_manager.get_current_device()
    if not serial:
        return
    ensure_dir(config['screenshot_path'])
    filename = f"screenshot_{get_timestamp()}.png"
    dest = os.path.join(config['screenshot_path'], filename)
    adb.run_shell("screencap -p /sdcard/screen.png", serial)
    adb.run("pull /sdcard/screen.png " + dest, serial)
    adb.run_shell("rm /sdcard/screen.png", serial)
    print(f"Screenshot gespeichert: {dest}")
    wait_for_enter()

def record_screen(device_manager, adb, config):
    serial = device_manager.get_current_device()
    if not serial:
        return
    print("Erweiterte Bildschirmaufnahme")
    duration = input(f"Dauer in Sekunden [{config['record_duration']}]: ") or str(config['record_duration'])
    bitrate = input("Bitrate (z.B. 4M, 8M) [4M]: ") or "4M"
    resolution = input("Auflösung (z.B. 1280x720, leer = Original): ")
    cmd = f"screenrecord --time-limit {duration} --bit-rate {bitrate}"
    if resolution:
        cmd += f" --size {resolution}"
    cmd += " /sdcard/record.mp4"
    filename = f"recording_{get_timestamp()}.mp4"
    adb.run_shell(cmd, serial)
    adb.run("pull /sdcard/record.mp4 " + filename, serial)
    adb.run_shell("rm /sdcard/record.mp4", serial)
    print(f"Aufnahme gespeichert: {filename}")
    wait_for_enter()

def mirror_screen(device_manager, config):
    serial = device_manager.get_current_device()
    if not serial:
        return
    scrcpy_path = config.get('scrcpy_path', 'scrcpy')
    try:
        subprocess.run([scrcpy_path, "-s", serial])
    except FileNotFoundError:
        print("scrcpy nicht gefunden. Bitte installieren oder Pfad anpassen.")
        wait_for_enter()

def create_gif(device_manager, adb, config):
    serial = device_manager.get_current_device()
    if not serial:
        return
    duration = input("Dauer in Sekunden: ")
    if not duration:
        return
    duration = int(duration)
    temp_mp4 = f"temp_{get_timestamp()}.mp4"
    gif_name = f"recording_{get_timestamp()}.gif"
    adb.run_shell(f"screenrecord --time-limit {duration} /sdcard/record.mp4", serial)
    adb.run("pull /sdcard/record.mp4 " + temp_mp4, serial)
    adb.run_shell("rm /sdcard/record.mp4", serial)
    try:
        subprocess.run(["ffmpeg", "-i", temp_mp4, "-vf", "fps=10", gif_name])
        os.remove(temp_mp4)
        print(f"GIF erstellt: {gif_name}")
    except FileNotFoundError:
        print("ffmpeg nicht gefunden. Kann GIF nicht erstellen.")
    wait_for_enter()

def delayed_screenshot(device_manager, adb, config):
    seconds = input("Verzögerung in Sekunden: ")
    if not seconds:
        return
    seconds = int(seconds)
    print(f"Warte {seconds} Sekunden...")
    time.sleep(seconds)
    take_screenshot(device_manager, adb, config)

def burst_screenshots(device_manager, adb, config):
    count = input("Anzahl Screenshots: ")
    interval = input("Intervall in Sekunden: ")
    if not count or not interval:
        return
    count = int(count)
    interval = float(interval)
    for i in range(count):
        take_screenshot(device_manager, adb, config)
        if i < count-1:
            time.sleep(interval)
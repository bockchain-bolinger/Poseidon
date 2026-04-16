import socket
import subprocess
import time
from utils.ui_helpers import clear_screen, print_header, menu_prompt, wait_for_enter, confirm

def show_menu(device_manager, adb, config):
    while True:
        clear_screen()
        print_header("Netzwerk & WLAN-ADB", "Verbindungen und Tools")
        print("1. 📱 WLAN-ADB verbinden (manuelle IP)")
        print("2. 📲 WLAN-ADB per QR-Code (Android 11+)")
        print("3. 🔍 Automatische Gerätesuche im Netzwerk")
        print("4. 🔌 ADB über USB zurücksetzen")
        print("5. 🌐 Netzwerk-Tools (ping, traceroute)")
        print("6. 🔁 Reverse Port Forwarding")
        print("7. ⚙️ Proxy-Einstellungen setzen")
        print("0. Zurück")

        choice = menu_prompt("Option", range(0, 8))

        if choice == 0:
            break
        elif choice == 1:
            wifi_connect_manual(device_manager, adb, config)
        elif choice == 2:
            wifi_connect_qr(device_manager, adb)
        elif choice == 3:
            auto_discover(device_manager, adb)
        elif choice == 4:
            reset_usb(device_manager, adb)
        elif choice == 5:
            network_tools_menu(device_manager, adb)
        elif choice == 6:
            reverse_port_forward(device_manager, adb)
        elif choice == 7:
            set_proxy(device_manager, adb)

def wifi_connect_manual(device_manager, adb, config):
    serial = device_manager.get_current_device()
    if not serial:
        print("Bitte zuerst ein Gerät über USB verbinden und auswählen.")
        wait_for_enter()
        return
    last_ip = config.get('last_ip', '')
    ip = input(f"IP-Adresse des Telefons (im gleichen WLAN) [{last_ip}]: ") or last_ip
    if not ip:
        return
    config['last_ip'] = ip
    print("Wechsle ADB auf TCP/IP-Modus...")
    adb.run("tcpip 5555", serial)
    time.sleep(2)
    stdout, stderr, rc = adb.run(f"connect {ip}:5555")
    print(stdout)
    if "connected" in stdout:
        print("✅ Erfolgreich verbunden. USB-Kabel kann entfernt werden.")
        device_manager.current_serial = f"{ip}:5555"
    else:
        print("❌ Verbindung fehlgeschlagen.")
    wait_for_enter()

def wifi_connect_qr(device_manager, adb):
    print("Diese Funktion generiert einen QR-Code für die WLAN-Paarung (Android 11+).")
    print("Stelle sicher, dass auf dem Gerät 'Wireless debugging' aktiviert ist.")
    print("Wähle dort 'Gerät per QR-Code paaren' und scanne den folgenden Code.")
    print("\nAlternativ: Gehe zu 'Wireless debugging' → 'Gerät per WLAN koppeln' und notiere IP und Port.")
    pair_ip = input("IP und Port (z.B. 192.168.1.10:12345): ")
    code = input("Sechsstelliger Code: ")
    stdout, stderr, rc = adb.run(f"pair {pair_ip} {code}")
    print(stdout)
    if "Successfully paired" in stdout:
        print("Paarung erfolgreich. Nun kannst du mit 'adb connect <ip>:5555' verbinden.")
    else:
        print("Paarung fehlgeschlagen.")
    wait_for_enter()

def auto_discover(device_manager, adb):
    print("Suche nach Geräten mit offenem Port 5555 im lokalen Netzwerk...")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    if local_ip.startswith("127."):
        print("Keine gültige Netzwerk-IP gefunden. Bitte manuell verbinden.")
        wait_for_enter()
        return
    subnet = ".".join(local_ip.split(".")[:3]) + ".0/24"
    print(f"Scanne Subnetz {subnet} nach Port 5555... (das kann einige Sekunden dauern)")
    try:
        subprocess.run(["nmap", "--version"], capture_output=True, check=True)
        use_nmap = True
    except:
        use_nmap = False
    found_ips = []
    if use_nmap:
        result = subprocess.run(["nmap", "-p", "5555", "--open", "-n", subnet], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "Nmap scan report for" in line:
                ip = line.split()[-1].strip("()")
                found_ips.append(ip)
    else:
        import ipaddress
        net = ipaddress.ip_network(subnet, strict=False)
        for ip in net.hosts():
            ip_str = str(ip)
            response = subprocess.run(["ping", "-c", "1", "-W", "1", ip_str], capture_output=True)
            if response.returncode == 0:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((ip_str, 5555))
                sock.close()
                if result == 0:
                    found_ips.append(ip_str)
    if found_ips:
        print("Gefundene Geräte mit offenem Port 5555:")
        for i, ip in enumerate(found_ips):
            print(f"{i+1}. {ip}")
        try:
            choice = int(input("Welches möchtest du verbinden? (0 = abbrechen): ")) - 1
            if 0 <= choice < len(found_ips):
                ip = found_ips[choice]
                stdout, stderr, rc = adb.run(f"connect {ip}:5555")
                print(stdout)
                if "connected" in stdout:
                    device_manager.current_serial = f"{ip}:5555"
        except:
            pass
    else:
        print("Keine Geräte gefunden.")
    wait_for_enter()

def reset_usb(device_manager, adb):
    adb.run("kill-server")
    adb.run("start-server")
    print("ADB-Server neu gestartet. Bitte USB-Kabel wieder anschließen und Gerät autorisieren.")
    device_manager.current_serial = None
    wait_for_enter()

def network_tools_menu(device_manager, adb):
    target = input("Ziel-IP oder Hostname: ")
    if not target:
        return
    print("1. Ping")
    print("2. Traceroute")
    tool = menu_prompt("Auswahl", [1,2])
    if tool == 1:
        out, _, _ = adb.run_shell(f"ping -c 4 {target}")
        print(out)
    elif tool == 2:
        out, _, _ = adb.run_shell(f"traceroute {target}")
        print(out)
    wait_for_enter()

def reverse_port_forward(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    local_port = input("Lokaler Port (PC): ")
    remote_port = input("Remote Port (Gerät): ")
    if local_port and remote_port:
        adb.run(f"reverse tcp:{local_port} tcp:{remote_port}", serial)
        print(f"Port {local_port} -> {remote_port} weitergeleitet.")
    wait_for_enter()

def set_proxy(device_manager, adb):
    serial = device_manager.get_current_device()
    if not serial:
        return
    proxy_host = input("Proxy-Host (leer = deaktivieren): ")
    proxy_port = input("Proxy-Port: ")
    if not proxy_host:
        adb.run_shell("settings put global http_proxy :0", serial)
        print("Proxy deaktiviert.")
    else:
        adb.run_shell(f"settings put global http_proxy {proxy_host}:{proxy_port}", serial)
        print(f"Proxy gesetzt auf {proxy_host}:{proxy_port}")
    wait_for_enter()
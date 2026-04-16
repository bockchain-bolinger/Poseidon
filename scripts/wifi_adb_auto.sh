#!/bin/bash
# Automatische WLAN-ADB Verbindung
# Benötigt nmap und arp-scan (optional)

echo "Suche nach Android-Geräten mit offenem Port 5555..."

# Netzwerkbereich ermitteln
MY_IP=$(ip route get 1 | awk '{print $NF;exit}')
SUBNET=$(echo $MY_IP | cut -d. -f1-3).0/24

echo "Scanne Subnetz $SUBNET ..."
nmap -p 5555 --open $SUBNET -oG - | grep "/open" | cut -d" " -f2 > /tmp/adb_hosts.txt

if [ ! -s /tmp/adb_hosts.txt ]; then
    echo "Keine Geräte gefunden."
    exit 1
fi

echo "Gefundene IPs:"
cat /tmp/adb_hosts.txt

while read IP; do
    echo "Versuche Verbindung zu $IP:5555 ..."
    adb connect $IP:5555
done < /tmp/adb_hosts.txt

rm /tmp/adb_hosts.txt
echo "Fertig."

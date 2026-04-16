#!/bin/bash
# Quick Backup Skript für Poseidon
# Verwendet ADB, um Geräteinformationen und Screenshot zu sichern.

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./quick_backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

echo "Erstelle Backup in $BACKUP_DIR"

# Geräteinformationen
adb shell getprop > "$BACKUP_DIR/getprop.txt"
adb shell dumpsys battery > "$BACKUP_DIR/battery.txt"
adb shell dumpsys meminfo > "$BACKUP_DIR/meminfo.txt"

# Screenshot
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png "$BACKUP_DIR/screenshot.png"
adb shell rm /sdcard/screen.png

# App-Liste
adb shell pm list packages -f > "$BACKUP_DIR/apps.txt"

echo "Backup abgeschlossen. Dateien in $BACKUP_DIR"

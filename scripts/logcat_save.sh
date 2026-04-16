#!/bin/bash
# Speichert Logcat mit Zeitstempel

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILENAME="logcat_$TIMESTAMP.txt"

adb logcat -d > "$FILENAME"
echo "Logcat gespeichert in $FILENAME"

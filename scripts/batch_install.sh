#!/bin/bash
# Batch-Installation aller APKs im angegebenen Ordner

if [ -z "$1" ]; then
    echo "Usage: $0 /pfad/zum/apk/ordner"
    exit 1
fi

FOLDER="$1"
if [ ! -d "$FOLDER" ]; then
    echo "Ordner nicht gefunden."
    exit 1
fi

echo "Installiere APKs aus $FOLDER ..."
for apk in "$FOLDER"/*.apk; do
    if [ -f "$apk" ]; then
        echo "Installiere $(basename "$apk") ..."
        adb install -r "$apk"
    fi
done
echo "Fertig."

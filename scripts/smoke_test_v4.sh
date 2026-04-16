#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
ACTIVATE_PATH="$VENV_DIR/bin/activate"

log() {
  printf '\n[%s] %s\n' "POSEIDON-SMOKE" "$1"
}

warn() {
  printf '\n[%s] WARNING: %s\n' "POSEIDON-SMOKE" "$1"
}

fail() {
  printf '\n[%s] ERROR: %s\n' "POSEIDON-SMOKE" "$1" >&2
  exit 1
}

log "Projektverzeichnis: $ROOT_DIR"

command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "Python nicht gefunden: $PYTHON_BIN"
command -v adb >/dev/null 2>&1 || fail "adb wurde nicht gefunden"

if [[ ! -d "$VENV_DIR" ]]; then
  log "Virtuelle Umgebung wird erstellt: $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$ACTIVATE_PATH"

log "Pip aktualisieren"
python -m pip install --upgrade pip >/dev/null

log "Abhängigkeiten aus requirements_v4.txt installieren"
pip install -r requirements_v4.txt >/dev/null

log "ADB-Version prüfen"
adb version || fail "adb version fehlgeschlagen"

log "ADB-Geräteliste abrufen"
adb devices || fail "adb devices fehlgeschlagen"

log "CLI Geräte-Test"
python cli_v4.py devices list --json || fail "devices list fehlgeschlagen"

log "CLI Health-Test"
if ! python cli_v4.py health check --json; then
  warn "health check war nicht erfolgreich. Prüfe, ob ein Gerät verbunden ist."
fi

log "CLI Monitoring Snapshot"
if ! python cli_v4.py monitor once --export both --json; then
  warn "monitor once fehlgeschlagen. Prüfe Gerätezustand und ADB-Verbindung."
fi

log "Dateiausgabe prüfen"
mkdir -p logs screenshots backups
ls -la logs || true
ls -la screenshots || true

log "main_v5.py Syntax prüfen"
python -m py_compile main_v5.py || fail "main_v5.py py_compile fehlgeschlagen"

log "cli_v4.py Syntax prüfen"
python -m py_compile cli_v4.py || fail "cli_v4.py py_compile fehlgeschlagen"

log "Poseidon Smoke-Test abgeschlossen"

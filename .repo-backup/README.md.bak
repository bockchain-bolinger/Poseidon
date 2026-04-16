# 🌊 Poseidon

**Poseidon** is an advanced ADB-based Android device toolkit for diagnostics, automation, analysis, and operator-friendly terminal workflows.

It now includes a **v4 parallel path** with:
- a cleaned main entrypoint
- headless CLI workflows
- device monitoring
- OCR / UI vision helpers
- safer upgrade candidates for the core runtime

> ⚠️ Use only on devices you own or are explicitly authorized to test.

---

# Highlights

## Core capabilities
- Android device control via **ADB**
- App, media, system, network, security, logcat, backup, and analysis menus
- Plugin discovery and plugin menu integration
- Rich terminal UX with themed output and interactive menus

## New v4 upgrade path
- **`main_v4.py`**: cleaned and extended main entrypoint
- **`main_clean.py`**: drop-in cleaned replacement for the old main flow
- **`cli_v3.py`**: headless CLI for monitoring and OCR workflows
- **`core/adb_handler_v2.py`**: hardened ADB handler with retries and structured results
- **`services/monitoring_service.py`**: device metrics collection
- **`services/vision_service.py`**: OCR-based screenshot text detection
- **`modules/monitoring.py`**: TUI monitoring menu
- **`modules/ui_vision.py`**: TUI OCR / text search / tap menu

---

# Repository status

Poseidon currently contains both:
- the **legacy/original runtime path**, and
- the **new v4 parallel path** introduced for safer iterative upgrades.

This means you can test and evolve the new architecture **without immediately replacing the original files**.

Recommended current path:
- use **`main_v4.py`** for interactive testing
- use **`cli_v3.py`** for headless workflows
- treat **`main_clean.py`** and **`core/adb_handler_v2.py`** as upgrade candidates for later consolidation

---

# Project structure

```text
Poseidon/
├─ main.py                     # legacy/original entrypoint
├─ main_clean.py               # cleaned drop-in replacement candidate
├─ main_v4.py                  # new v4 interactive entrypoint
├─ cli.py                      # early CLI prototype
├─ cli_v2.py                   # v2 CLI with monitoring/vision basics
├─ cli_v3.py                   # current recommended headless CLI
├─ config.json                 # runtime configuration
├─ core/
│  ├─ adb_handler.py           # legacy/original ADB runtime
│  ├─ adb_handler_v2.py        # hardened ADB runtime candidate
│  ├─ device_manager.py
│  ├─ exceptions.py
│  ├─ logger.py
│  ├─ plugin_manager.py
│  └─ result.py
├─ services/
│  ├─ monitoring_service.py
│  └─ vision_service.py
├─ modules/
│  ├─ monitoring.py
│  ├─ ui_vision.py
│  └─ ... existing feature modules ...
├─ plugins/
├─ logs/
├─ backups/
└─ screenshots/
```

---

# Requirements

## System tools
Recommended on Linux / Debian / Kali / Ubuntu:
- `python3`
- `python3-venv`
- `adb`
- `scrcpy`
- `ffmpeg`
- optionally `tesseract-ocr`

Example:

```bash
sudo apt update
sudo apt install -y python3 python3-venv adb scrcpy ffmpeg tesseract-ocr
```

## Python packages
Install project dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install pillow pytesseract
```

> `pytesseract` and `Pillow` are required for OCR / vision features.

---

# Quick start

## Interactive v4 path
Recommended interactive entrypoint:

```bash
python main_v4.py
```

## Cleaned main alternative
If you want the cleaned legacy-compatible path:

```bash
python main_clean.py
```

## Legacy path
The original entrypoint still exists:

```bash
python main.py
```

---

# Headless CLI

The recommended headless interface is:

```bash
python cli_v3.py
```

## Device commands
```bash
python cli_v3.py devices list
python cli_v3.py health check --json
```

## Monitoring commands
```bash
python cli_v3.py monitor once --json
python cli_v3.py monitor stream --interval 2 --count 5
```

## OCR / Vision commands
```bash
python cli_v3.py vision find-text WLAN --annotate --json
python cli_v3.py vision tap-text WLAN
python cli_v3.py vision tap-text WLAN --force --json
```

### `tap-text` safety behavior
- without `--force`: dry-run preview
- with `--force`: actual `input tap x y` execution via ADB

---

# New v4 menus

`main_v4.py` adds two new menu entries:

## Monitoring
Provides device snapshot metrics such as:
- battery level
- battery temperature
- memory usage
- free memory
- timestamp / active serial

## Vision / OCR
Provides:
- screenshot capture
- OCR text search
- annotation of OCR matches
- optional tap on detected text positions

---

# Monitoring service

`services/monitoring_service.py` currently collects:
- battery level
- battery temperature
- memory usage
- available memory

Planned next steps:
- CPU load
- CSV / JSONL export
- streaming dashboards
- anomaly detection

---

# OCR / Vision service

`services/vision_service.py` currently supports:
- screenshot capture
- OCR text matching
- annotated screenshots

Planned next steps:
- better screenshot handling
- improved multi-word matching
- confidence filtering
- better hit selection logic
- optional template / icon matching later

---

# Runtime notes

## ADB selection
Poseidon selects devices through the device manager. If multiple devices are connected, explicit serial handling is recommended for CLI usage.

## Screenshot directory
Screenshots are stored under:
- `./screenshots`

## Backup directory
Backups are stored under:
- `./backups`

## Logs
Logs are stored under:
- `./logs`

---

# Recommended current workflow

## For interactive use
Use:

```bash
python main_v4.py
```

## For automation / scripting / CI-style runs
Use:

```bash
python cli_v3.py
```

## For migration work
Use as upgrade references:
- `main_clean.py`
- `core/adb_handler_v2.py`

---

# Consolidation plan

The current repository intentionally keeps the old and new paths side by side.

Recommended consolidation sequence:
1. validate `main_v4.py`
2. validate `cli_v3.py`
3. harden `monitoring_service.py`
4. harden `vision_service.py`
5. replace legacy `main.py` with the v4 path
6. migrate `adb_handler.py` to the v2 implementation
7. update docs and remove obsolete transitional files

---

# Safety

Use Poseidon only for:
- your own devices
- lab devices
- devices you are explicitly allowed to assess

Do not use it against third-party systems without authorization.

---

# Current recommended files

If you only want the strongest current path, focus on these files:
- `main_v4.py`
- `cli_v3.py`
- `core/adb_handler_v2.py`
- `services/monitoring_service.py`
- `services/vision_service.py`
- `modules/monitoring.py`
- `modules/ui_vision.py`

---

# Author workflow note

This repository is currently transitioning from a legacy menu-centric architecture toward a more modular structure with:
- cleaner entrypoints
- service-layer reuse
- CLI-based automation
- safer staged upgrades

That transition is already usable today through the v4 parallel path.

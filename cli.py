#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.device_manager import DeviceManager
from core.adb_handler import ADBHandler
from core.logger import logger
from services.monitoring_service_v2 import MonitoringServiceV2
from services.vision_service_v2 import VisionServiceV2
from utils.dependency_checker import check_all_dependencies

CONFIG_PATH = BASE_DIR / "config.json"


def default_config() -> dict:
    return {
        "version": "4.0-dev",
        "language": "de",
        "theme": "light",
        "global": {
            "backup_path": "./backups",
            "screenshot_path": "./screenshots",
            "record_duration": 30,
            "scrcpy_path": "scrcpy",
            "log_path": "./logs",
        },
        "devices": {},
    }


def load_config() -> dict:
    config = default_config()
    if not CONFIG_PATH.exists():
        return config
    try:
        raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        logger.warning(f"config.json konnte nicht sauber gelesen werden: {e}")
        return config

    legacy_global_keys = {"backup_path", "screenshot_path", "record_duration", "scrcpy_path", "log_path"}
    config.update({k: v for k, v in raw.items() if k not in legacy_global_keys and k != "global"})
    if isinstance(raw.get("global"), dict):
        config["global"].update(raw["global"])
    for key in legacy_global_keys:
        if key in raw:
            config["global"][key] = raw[key]
    config["devices"] = raw.get("devices", {})
    return config


def init_runtime():
    results, warnings = check_all_dependencies()
    if not results.get("adb"):
        print("ADB wurde nicht gefunden.")
        sys.exit(1)
    if warnings:
        for warning in warnings:
            logger.warning(warning)
    config = load_config()
    Path(config["global"].get("screenshot_path", "./screenshots")).mkdir(parents=True, exist_ok=True)
    Path(config["global"].get("backup_path", "./backups")).mkdir(parents=True, exist_ok=True)
    Path(config["global"].get("log_path", "./logs")).mkdir(parents=True, exist_ok=True)
    device_manager = DeviceManager(config)
    adb = ADBHandler(device_manager)
    monitoring = MonitoringServiceV2(device_manager, adb, export_dir=config["global"].get("log_path", "./logs"))
    vision = VisionServiceV2(device_manager, adb, screenshot_dir=config["global"].get("screenshot_path", "./screenshots"))
    return config, device_manager, adb, monitoring, vision


def print_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_devices_list(args) -> int:
    _, device_manager, _, _, _ = init_runtime()
    devices = device_manager.refresh_devices()
    payload = {"devices": devices, "count": len(devices)}
    if args.json:
        print_json(payload)
    else:
        print("Verbundene Geräte:" if devices else "Keine Geräte verbunden.")
        for device in devices:
            print(f"- {device}")
    return 0


def cmd_health_check(args) -> int:
    _, device_manager, adb, _, _ = init_runtime()
    serial = args.serial or device_manager.get_current_device()
    stdout, stderr, rc = adb.run("version", serial=serial, timeout=10)
    payload = {"ok": rc == 0, "serial": serial, "stdout": stdout, "stderr": stderr, "returncode": rc}
    if args.json:
        print_json(payload)
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0 if payload["ok"] else 1


def cmd_monitor_once(args) -> int:
    _, _, _, monitoring, _ = init_runtime()
    metrics = monitoring.collect_once(serial=args.serial)
    payload = metrics.to_dict()
    if args.export in ("csv", "both"):
        payload["csv_export"] = str(monitoring.export_csv(metrics))
    if args.export in ("jsonl", "both"):
        payload["jsonl_export"] = str(monitoring.export_jsonl(metrics))
    if args.json:
        print_json(payload)
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


def cmd_monitor_stream(args) -> int:
    _, _, _, monitoring, _ = init_runtime()
    iterations = args.count if args.count and args.count > 0 else None
    done = 0
    try:
        while True:
            metrics = monitoring.collect_once(serial=args.serial)
            payload = metrics.to_dict()
            if args.export in ("csv", "both"):
                payload["csv_export"] = str(monitoring.export_csv(metrics))
            if args.export in ("jsonl", "both"):
                payload["jsonl_export"] = str(monitoring.export_jsonl(metrics))
            if args.json:
                print_json(payload)
            else:
                print("-" * 40)
                for key, value in payload.items():
                    print(f"{key}: {value}")
            done += 1
            if iterations is not None and done >= iterations:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 130
    return 0


def cmd_vision_find_text(args) -> int:
    _, _, _, _, vision = init_runtime()
    image_path = vision.take_screenshot(serial=args.serial, filename="vision_v4_capture.png")
    matches = vision.find_text(args.query, image_path, min_confidence=args.min_confidence)
    payload = {"query": args.query, "image": str(image_path), "matches": [m.to_dict() for m in matches], "count": len(matches)}
    if args.annotate and matches:
        payload["annotated_image"] = str(vision.annotate_matches(image_path, matches, output_name="vision_v4_annotated.png"))
    if args.json:
        print_json(payload)
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


def cmd_vision_tap_text(args) -> int:
    _, _, adb, _, vision = init_runtime()
    image_path = vision.take_screenshot(serial=args.serial, filename="vision_v4_tap_capture.png")
    match = vision.best_match(args.query, image_path, min_confidence=args.min_confidence)
    if not match:
        payload = {"ok": False, "reason": "no_match", "query": args.query, "image": str(image_path)}
        if args.json:
            print_json(payload)
        else:
            print("Kein geeigneter OCR-Treffer gefunden.")
        return 1
    x = match.left + match.width // 2
    y = match.top + match.height // 2
    if not args.force:
        payload = {"ok": True, "dry_run": True, "query": args.query, "tap": {"x": x, "y": y}, "match": match.to_dict()}
        if args.json:
            print_json(payload)
        else:
            print(f"Dry run: würde auf ({x}, {y}) tippen für '{match.text}'. Mit --force ausführen.")
        return 0
    stdout, stderr, rc = adb.run_shell(f"input tap {x} {y}", serial=args.serial, timeout=10)
    payload = {"ok": rc == 0, "query": args.query, "tap": {"x": x, "y": y}, "match": match.to_dict(), "stdout": stdout, "stderr": stderr, "returncode": rc}
    if args.json:
        print_json(payload)
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0 if payload["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="poseidon-cli-v4", description="Headless CLI für Poseidon v4")
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    devices = sub.add_parser("devices", help="Geräteoperationen")
    devices_sub = devices.add_subparsers(dest="devices_command")
    devices_sub.required = True
    devices_list = devices_sub.add_parser("list", help="Verbundene Geräte auflisten")
    devices_list.add_argument("--json", action="store_true")
    devices_list.set_defaults(func=cmd_devices_list)

    health = sub.add_parser("health", help="Grundlegender Health Check")
    health_sub = health.add_subparsers(dest="health_command")
    health_sub.required = True
    health_check = health_sub.add_parser("check", help="ADB-Erreichbarkeit prüfen")
    health_check.add_argument("--serial")
    health_check.add_argument("--json", action="store_true")
    health_check.set_defaults(func=cmd_health_check)

    monitor = sub.add_parser("monitor", help="Monitoring-Funktionen")
    monitor_sub = monitor.add_subparsers(dest="monitor_command")
    monitor_sub.required = True
    monitor_once = monitor_sub.add_parser("once", help="Einmalige Metrik-Erfassung")
    monitor_once.add_argument("--serial")
    monitor_once.add_argument("--export", choices=["none", "csv", "jsonl", "both"], default="none")
    monitor_once.add_argument("--json", action="store_true")
    monitor_once.set_defaults(func=cmd_monitor_once)
    monitor_stream = monitor_sub.add_parser("stream", help="Metriken laufend ausgeben")
    monitor_stream.add_argument("--serial")
    monitor_stream.add_argument("--interval", type=float, default=2.0)
    monitor_stream.add_argument("--count", type=int, default=0)
    monitor_stream.add_argument("--export", choices=["none", "csv", "jsonl", "both"], default="none")
    monitor_stream.add_argument("--json", action="store_true")
    monitor_stream.set_defaults(func=cmd_monitor_stream)

    vision = sub.add_parser("vision", help="OCR/Vision-Funktionen")
    vision_sub = vision.add_subparsers(dest="vision_command")
    vision_sub.required = True
    vision_find = vision_sub.add_parser("find-text", help="Text per OCR auf Screenshot suchen")
    vision_find.add_argument("query")
    vision_find.add_argument("--serial")
    vision_find.add_argument("--min-confidence", type=float, default=-1.0)
    vision_find.add_argument("--annotate", action="store_true")
    vision_find.add_argument("--json", action="store_true")
    vision_find.set_defaults(func=cmd_vision_find_text)
    vision_tap = vision_sub.add_parser("tap-text", help="Besten OCR-Treffer antippen")
    vision_tap.add_argument("query")
    vision_tap.add_argument("--serial")
    vision_tap.add_argument("--min-confidence", type=float, default=-1.0)
    vision_tap.add_argument("--force", action="store_true")
    vision_tap.add_argument("--json", action="store_true")
    vision_tap.set_defaults(func=cmd_vision_tap_text)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)

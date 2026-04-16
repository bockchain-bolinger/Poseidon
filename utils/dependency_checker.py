import shutil
import subprocess
from typing import Dict, List, Tuple

def check_binary(name: str) -> bool:
    """Prüft, ob eine Binärdatei im System-Pfad verfügbar ist."""
    return shutil.which(name) is not None

def get_binary_version(name: str) -> str:
    """Versucht die Version einer Binärdatei abzufragen."""
    try:
        if name == "adb":
            res = subprocess.run(["adb", "--version"], capture_output=True, text=True, timeout=2)
            for line in res.stdout.splitlines():
                if "Android Debug Bridge version" in line:
                    return line.split()[-1]
        elif name == "scrcpy":
            res = subprocess.run(["scrcpy", "--version"], capture_output=True, text=True, timeout=2)
            first_line = res.stdout.splitlines()[0]
            return first_line.split()[-1]
        elif name == "ffmpeg":
            res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=2)
            first_line = res.stdout.splitlines()[0]
            return first_line.split()[2]
    except:
        pass
    return "unbekannt"

def check_all_dependencies() -> Tuple[Dict[str, bool], List[str]]:
    """
    Prüft alle benötigten und optionalen Abhängigkeiten.
    Gibt ein Dictionary mit Status und eine Liste mit Warnungen zurück.
    """
    deps = {
        "adb": {"required": True, "description": "Android Debug Bridge (für alle Funktionen)"},
        "scrcpy": {"required": False, "description": "Screen Copy (für Bildschirmspiegelung)"},
        "ffmpeg": {"required": False, "description": "FFmpeg (für Video-Konvertierung/GIFs)"},
        "nmap": {"required": False, "description": "Nmap (für Netzwerksuche)"}
    }
    
    results = {}
    warnings = []
    
    for name, info in deps.items():
        found = check_binary(name)
        results[name] = found
        if not found:
            status = "FEHLT" if info["required"] else "OPTIONAL FEHLT"
            warnings.append(f"{name}: {status} - {info['description']}")
            
    return results, warnings

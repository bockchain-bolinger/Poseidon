import subprocess
import sys
import os
import requests
from pathlib import Path
from utils.ui_helpers import confirm, wait_for_enter
from utils.ansi_colors import fg, style

def check_for_updates(current_version="3.0"):
    """
    Prüft auf GitHub nach einer neueren Version.
    """
    # Später: GitHub API URL nutzen
    # repo_url = "https://api.github.com/repos/arturik69/poseidon/releases/latest"
    # try:
    #     response = requests.get(repo_url, timeout=5)
    #     if response.status_code == 200:
    #         latest_version = response.json()["tag_name"].replace("v", "")
    # ...
    
    latest_version = "3.1" # Simulation
    if latest_version > current_version:
        return True, latest_version
    return False, latest_version

def perform_update():
    """Führt ein Git Pull durch (falls das Projekt in einem Git-Repo liegt)."""
    repo_path = Path(__file__).parent.parent
    if not (repo_path / ".git").exists():
        print("Kein Git-Repository gefunden. Update nur manuell möglich.")
        return False
    print("Führe git pull aus...")
    try:
        result = subprocess.run(["git", "pull"], cwd=repo_path, capture_output=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            print(f"{fg.GREEN}Update erfolgreich. Bitte starten Sie Poseidon neu.{style.RESET}")
            return True
        else:
            print(f"{fg.RED}Fehler beim Update:{style.RESET}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"Fehler: {e}")
        return False

def show_update_menu(device_manager, adb, config):
    """Menüpunkt für manuellen Update-Check (optional)."""
    from utils.ui_helpers import clear_screen, print_header, menu_prompt
    clear_screen()
    print_header("Updates", "Poseidon aktualisieren")
    has_update, latest = check_for_updates(config.get("version", "3.0"))
    if has_update:
        print(f"Neue Version {latest} verfügbar.")
        if confirm("Möchten Sie jetzt aktualisieren?"):
            perform_update()
    else:
        print("Sie haben die neueste Version.")
    wait_for_enter()

import os
from utils.ui_helpers import wait_for_enter, confirm
from utils.ansi_colors import fg, style
from utils.decorators import require_device

class AdvancedOps:
    def __init__(self, adb, serial):
        self.adb = adb
        self.serial = serial
        self.audit_log = "logs/audit.log"

    def _log_audit(self, action, target):
        with open(self.audit_log, "a") as f:
            f.write(f"[AUDIT] {action} | Target: {target}\n")

    def ghost_clean(self):
        """Bereinigt Spuren von ADB-Artefakten."""
        print(f"{fg.CYAN}Bereinige System-Artefakte...{style.RESET}")
        self.adb.run_shell("rm -rf /data/local/tmp/*", self.serial)
        self.adb.run_shell("rm -rf /sdcard/Android/data/*/cache/*", self.serial)
        self._log_audit("GhostClean", "System/Cache")
        print("Bereinigung abgeschlossen.")

    def dump_ui_tree(self):
        """Extrahiert die komplette UI-Struktur als XML."""
        print("Erstelle UI-Dump...")
        self.adb.run_shell("uiautomator dump /sdcard/ui_dump.xml", self.serial)
        self.adb.run(f"pull /sdcard/ui_dump.xml ./ui_dump.xml", self.serial)
        self._log_audit("UIDump", "UI-Structure")
        print("UI-Dump nach ./ui_dump.xml extrahiert.")

    def list_hidden_intents(self, package):
        """Listet versteckte Intents einer App auf."""
        print(f"Suche versteckte Intents für {package}...")
        out, _, _ = self.adb.run_shell(f"dumpsys package {package} | grep -E 'intent-filter|action'", self.serial)
        print(out)
        self._log_audit("IntentScan", package)

    def set_device_identity(self, model, brand):
        """Ändert die Identität des Geräts (erfordert Root)."""
        if not confirm("ACHTUNG: Erfordert Root. Wirklich build.prop überschreiben?"):
            return
        # Beispiel für ein Set-Command (muss remounted werden)
        self.adb.run_shell("mount -o remount,rw /system", self.serial)
        self.adb.run_shell(f"setprop ro.product.model '{model}'", self.serial)
        self.adb.run_shell(f"setprop ro.product.brand '{brand}'", self.serial)
        self._log_audit("IdentityChange", f"{model}/{brand}")
        print("Identity geändert (Reboot erforderlich).")

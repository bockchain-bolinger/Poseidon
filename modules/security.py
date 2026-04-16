from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from utils.ui_helpers import print_header, menu_prompt, wait_for_enter, confirm
from utils.decorators import require_device
from modules.advanced_ops import AdvancedOps

console = Console()

@require_device
def show_menu(device_manager, adb):
    serial = device_manager.get_current_device()
    ops = AdvancedOps(adb, serial)
    
    while True:
        print_header("ADVANCED SECURITY & OPS", "Underground Mode")
        table = Table(title="Select Option")
        table.add_column("ID", style="cyan")
        table.add_column("Action", style="magenta")
        
        menu_items = [
            ("1", "👻 Ghost Mode (Cleanup)"),
            ("2", "🔍 UI Tree Dump"),
            ("3", "🕵️ Hidden Intents Scan"),
            ("4", "🛡️ Security Audit"),
            ("5", "📜 Kernel Sniffer (dmesg)"),
            ("6", "🆔 Set Identity (Root)"),
            ("0", "Exit")
        ]
        
        for id, name in menu_items:
            table.add_row(id, name)
        console.print(table)

        choice = menu_prompt("Option", range(0, 7))
        if choice == 0: break
        elif choice == 1: ops.ghost_clean(); wait_for_enter()
        elif choice == 2: ops.dump_ui_tree(); wait_for_enter()
        elif choice == 3:
            pkg = console.input("[yellow]Package: [/]")
            if pkg: ops.list_hidden_intents(pkg); wait_for_enter()
        elif choice == 4:
            run_security_audit(adb, serial)
        elif choice == 5:
            console.print("[cyan]Sniffing Kernel Events... (Ctrl+C to stop)[/]")
            try: adb.run_shell("dmesg -w", serial)
            except KeyboardInterrupt: pass
        elif choice == 6:
            model = console.input("[yellow]New Model: [/]")
            brand = console.input("[yellow]New Brand: [/]")
            ops.set_device_identity(model, brand); wait_for_enter()

def run_security_audit(adb, serial):
    console.print("[bold yellow]Running Security Audit...[/]")
    out, _, _ = adb.run_shell("pm list permissions -d -g", serial)
    
    table = Table(title="Dangerous Permissions Found")
    table.add_column("Permission")
    for line in out.splitlines()[:15]:
        table.add_row(line)
    console.print(table)
    
    with open("logs/audit.log", "a") as f:
        f.write("[SECURITY_AUDIT] Scan run\n")
    wait_for_enter()

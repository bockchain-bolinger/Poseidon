import time
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from utils.decorators import require_device

console = Console()

def generate_layout(adb, serial):
    """Erstellt das Live-Dashboard Layout."""
    
    # Daten abrufen (mit Cache für nicht-zeitkritische Infos)
    bat_out, _, _ = adb.run_shell("dumpsys battery", serial, use_cache=True)
    bat_data = {l.split(":")[0].strip(): l.split(":")[-1].strip() for l in bat_out.splitlines() if ":" in l}
    
    # RAM/CPU
    top_out, _, _ = adb.run_shell("top -n 1 -b -m 5", serial, use_cache=False)
    
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
    
    layout["header"].update(Panel("[bold cyan]POSEIDON LIVE DASHBOARD[/]"))
    layout["left"].update(Panel(f"Battery: {bat_data.get('level', '?')}% | Status: {bat_data.get('status', '?')}", title="Battery"))
    layout["right"].update(Panel(top_out, title="CPU/RAM Usage"))
    
    return layout

@require_device
def show_dashboard(device_manager, adb):
    serial = device_manager.get_current_device()
    console.print("[yellow]Starting Dashboard...[/]")
    with Live(generate_layout(adb, serial), refresh_per_second=1):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

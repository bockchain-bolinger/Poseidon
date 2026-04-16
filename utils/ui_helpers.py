import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.status import Status
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
from .ansi_colors import fg, style

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title, subtitle=""):
    console.print(Panel(f"[bold cyan]{subtitle}[/]", title=f"[bold yellow]{title}[/]"))

def menu_prompt(prompt_text, valid_range=None):
    while True:
        choice = console.input(f"[bold yellow]{prompt_text}[/]: ")
        try:
            val = int(choice)
            if valid_range is None or val in valid_range:
                return val
            console.print("[red]Invalid selection.[/red]")
        except ValueError:
            console.print("[red]Please enter a number.[/red]")

def confirm(question):
    answer = console.input(f"[bold yellow]{question} (y/n)[/]: ").lower()
    return answer.startswith('y')

def wait_for_enter():
    console.input(f"\n[dim]Press Enter to continue...[/dim]")

# Integration für Fortschritt und Status
def show_progress(iterable, description="Processing..."):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task(description, total=len(iterable))
        for item in iterable:
            yield item
            progress.advance(task)

class SimpleProgressBar:
    def __init__(self, total, description="Progress"):
        self.progress = Progress()
        self.task = self.progress.add_task(description, total=total)
        self.progress.start()

    def update(self, n=1):
        self.progress.update(self.task, advance=n)

    def close(self):
        self.progress.stop()

def show_menu_generic(title, options, prompt="Option wählen"):
    """
    Einfache generische Menüanzeige für ältere Module.
    options erwartet eine Liste von Strings.
    Gibt die ausgewählte Nummer als int zurück.
    """
    print_header(title, "")
    for idx, option in enumerate(options, 1):
        print(f"{idx}. {option}")
    print("0. Zurück")
    return menu_prompt(prompt, range(0, len(options) + 1))

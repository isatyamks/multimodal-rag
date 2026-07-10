from rich.console import Console
from rich.panel import Panel

console = Console()

def print_phase(name: str, style: str = "bold cyan"):
    console.print(Panel(f"[{style}]{name}[/]", border_style=style, expand=False))

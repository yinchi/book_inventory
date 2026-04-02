"""Formatting functions for the book inventory application."""


def error(message: str) -> str:
    """Format an error message."""
    return f"[bright_red][bold]Error:[/bold] {message}[/bright_red]"


def warning(message: str) -> str:
    """Format a warning message."""
    return f"[yellow][bold]Warning:[/bold] {message}[/yellow]"


def success(message: str) -> str:
    """Format a success message."""
    return f"[green]{message}[/green]"

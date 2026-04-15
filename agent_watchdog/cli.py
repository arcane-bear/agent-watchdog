"""CLI commands for agent-watchdog."""

import sys
import time

import click
from rich.console import Console
from rich.live import Live
from rich.table import Table

from agent_watchdog import __version__
from agent_watchdog.db import (
    get_all_agents,
    ping_agent,
    register_agent,
    remove_agent,
)

console = Console()


def _format_elapsed(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}m"
    return f"{seconds / 3600:.1f}h"


def _agent_status(agent: dict) -> tuple[str, str]:
    """Returns (status_label, style) for an agent."""
    if agent["last_ping"] is None:
        return "waiting", "dim"
    elapsed = time.time() - agent["last_ping"]
    interval = agent["interval_seconds"]
    if elapsed <= interval:
        return "healthy", "green"
    if elapsed <= interval * 2:
        return "warning", "yellow"
    return "dead", "red"


def _build_table(agents: list[dict], title: str = "Agent Watchdog") -> Table:
    table = Table(title=title)
    table.add_column("Agent", style="bold")
    table.add_column("Interval", justify="right")
    table.add_column("Last Ping", justify="right")
    table.add_column("Elapsed", justify="right")
    table.add_column("Status", justify="center")

    for agent in agents:
        interval_str = f"{agent['interval_seconds']}s"
        if agent["last_ping"] is None:
            last_ping_str = "never"
            elapsed_str = "-"
        else:
            from datetime import datetime

            last_ping_str = datetime.fromtimestamp(agent["last_ping"]).strftime(
                "%H:%M:%S"
            )
            elapsed_str = _format_elapsed(time.time() - agent["last_ping"])

        status_label, style = _agent_status(agent)
        table.add_row(
            agent["name"],
            interval_str,
            last_ping_str,
            elapsed_str,
            f"[{style}]{status_label}[/{style}]",
        )

    return table


@click.group()
@click.version_option(version=__version__, prog_name="agent-watchdog")
def app():
    """Lightweight heartbeat monitor for AI agent loops."""


@app.command()
@click.argument("name")
@click.option(
    "--interval",
    "-i",
    type=int,
    required=True,
    help="Expected check-in interval in seconds.",
)
def register(name: str, interval: int):
    """Register an agent to monitor."""
    if interval <= 0:
        console.print("[red]Interval must be positive.[/red]")
        sys.exit(1)
    if register_agent(name, interval):
        console.print(
            f"[green]Registered[/green] [bold]{name}[/bold] (interval: {interval}s)"
        )
    else:
        console.print(f"[yellow]Agent '{name}' already exists.[/yellow]")
        sys.exit(1)


@app.command()
@click.argument("name")
def ping(name: str):
    """Send a heartbeat ping for an agent."""
    if ping_agent(name):
        console.print(f"[green]Pong[/green] [bold]{name}[/bold]")
    else:
        console.print(f"[red]Unknown agent '{name}'.[/red]")
        sys.exit(1)


@app.command()
def status():
    """Show status of all registered agents."""
    agents = get_all_agents()
    if not agents:
        console.print("[dim]No agents registered.[/dim]")
        return

    table = _build_table(agents)
    console.print(table)

    # Exit code 1 if any agent is dead
    for agent in agents:
        label, _ = _agent_status(agent)
        if label == "dead":
            sys.exit(1)


@app.command()
@click.argument("name")
def remove(name: str):
    """Remove a registered agent."""
    if remove_agent(name):
        console.print(f"[green]Removed[/green] [bold]{name}[/bold]")
    else:
        console.print(f"[red]Unknown agent '{name}'.[/red]")
        sys.exit(1)


@app.command()
@click.option("--refresh", "-r", type=float, default=5.0, help="Refresh interval in seconds.")
def watch(refresh: float):
    """Live-refreshing dashboard of all agents."""
    try:
        with Live(console=console, refresh_per_second=1) as live:
            while True:
                agents = get_all_agents()
                if not agents:
                    live.update("[dim]No agents registered. Waiting...[/dim]")
                else:
                    live.update(_build_table(agents, title="Agent Watchdog (live)"))
                time.sleep(refresh)
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped.[/dim]")

"""SQLite database for agent heartbeat tracking."""

import sqlite3
import time
from pathlib import Path
from typing import Optional


DB_DIR = Path.home() / ".watchdog"
DB_PATH = DB_DIR / "watchdog.db"


def _connect() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agents (
            name TEXT PRIMARY KEY,
            interval_seconds INTEGER NOT NULL,
            last_ping REAL,
            registered_at REAL NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def register_agent(name: str, interval: int) -> bool:
    """Register an agent. Returns True if newly created, False if already exists."""
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO agents (name, interval_seconds, last_ping, registered_at) VALUES (?, ?, NULL, ?)",
            (name, interval, time.time()),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def ping_agent(name: str) -> bool:
    """Record a heartbeat. Returns True if agent exists."""
    conn = _connect()
    cursor = conn.execute(
        "UPDATE agents SET last_ping = ? WHERE name = ?",
        (time.time(), name),
    )
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def remove_agent(name: str) -> bool:
    """Remove an agent. Returns True if it existed."""
    conn = _connect()
    cursor = conn.execute("DELETE FROM agents WHERE name = ?", (name,))
    conn.commit()
    removed = cursor.rowcount > 0
    conn.close()
    return removed


def get_agent(name: str) -> Optional[dict]:
    """Get a single agent by name."""
    conn = _connect()
    row = conn.execute("SELECT * FROM agents WHERE name = ?", (name,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_agents() -> list[dict]:
    """Get all registered agents."""
    conn = _connect()
    rows = conn.execute("SELECT * FROM agents ORDER BY name").fetchall()
    conn.close()
    return [dict(r) for r in rows]

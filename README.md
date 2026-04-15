# agent-watchdog

Lightweight heartbeat monitor for AI agent loops. A dead man's switch for your agents.

Register agents, have them ping on an interval, get alerted when they go silent.

## Install

```bash
pip install agent-watchdog
```

Or from source:

```bash
git clone https://github.com/arcane-bear/agent-watchdog.git
cd agent-watchdog
pip install -e .
```

## Usage

### Register an agent

```bash
watchdog register my-agent --interval 60
# Registered my-agent (interval: 60s)
```

### Send heartbeats

Your agent calls this periodically to say "I'm alive":

```bash
watchdog ping my-agent
# Pong my-agent
```

### Check status

```bash
watchdog status
```

```
        Agent Watchdog
┌────────────┬──────────┬───────────┬─────────┬─────────┐
│ Agent      │ Interval │ Last Ping │ Elapsed │ Status  │
├────────────┼──────────┼───────────┼─────────┼─────────┤
│ my-agent   │      60s │  14:32:01 │     12s │ healthy │
│ scraper    │     300s │  14:28:45 │   3.4m  │ healthy │
│ ingest-bot │      30s │  14:20:00 │  12.1m  │ dead    │
└────────────┴──────────┴───────────┴─────────┴─────────┘
```

Colors: **green** = healthy, **yellow** = warning (>1x interval), **red** = dead (>2x interval).

Exit code is `1` if any agent is dead — useful in CI/scripts.

### Live dashboard

```bash
watchdog watch
```

Refreshes every 5s. Ctrl+C to stop.

### Remove an agent

```bash
watchdog remove my-agent
# Removed my-agent
```

## How it works

All state lives in a local SQLite database at `~/.watchdog/watchdog.db`. No server, no config files, no external dependencies beyond `click` and `rich`.

Your agent process just needs to shell out to `watchdog ping <name>` on a regular interval. If the ping stops coming, `watchdog status` will flag it.

### Use in a Python agent

```python
import subprocess, threading

def heartbeat(name, interval):
    def _ping():
        while True:
            subprocess.run(["watchdog", "ping", name])
            threading.Event().wait(interval)
    t = threading.Thread(target=_ping, daemon=True)
    t.start()

# Start heartbeat in background
heartbeat("my-agent", 30)
```

### Use in a shell loop

```bash
while true; do watchdog ping my-agent; sleep 30; done &
```

## Requirements

- Python 3.9+
- click
- rich

## License

MIT

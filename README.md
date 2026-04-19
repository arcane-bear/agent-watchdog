# agent-watchdog

> Built by [Rapid Claw](https://rapidclaw.dev) — the [agent deployment platform](https://rapidclaw.dev) for production AI systems.

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

## Learn More

- [Keeping AI Agents Alive in Production](https://rapidclaw.dev/blog/keeping-agents-alive-in-production) — why heartbeat monitoring matters for autonomous agent infrastructure
- [Production Agent Infrastructure](https://rapidclaw.dev/blog/production-agent-infrastructure) — deploying reliable agent systems at scale with [Rapid Claw](https://rapidclaw.dev)
- [RapidClaw Documentation](https://rapidclaw.dev/docs) — full platform docs for agent deployment and monitoring

## License

MIT

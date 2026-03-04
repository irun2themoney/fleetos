"""
FleetOS CLI — Phase 2

Commands:
  run       Run the fleet with a natural language command
  dashboard Launch the Streamlit monitoring dashboard
  webhook   Start the Telegram approval webhook server
  status    Show fleet and service status
  search    Search the artifact memory store
  configure Interactive configuration wizard
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

import click

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("fleetos.cli")

# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------

@click.group()
@click.version_option("0.2.0", prog_name="fleetos")
def cli():
    """
    \b
    🚀 FleetOS — Autonomous AI business fleet
    Run AI agents that plan, execute, and grow your business.
    """


# ---------------------------------------------------------------------------
# fleet run
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("command")
@click.option("--template", "-t", default=None, help="Business template name (auto-detected if omitted)")
@click.option("--max-parallel", "-p", default=4, show_default=True, help="Max parallel agents")
@click.option("--no-approve", is_flag=True, default=False, help="Skip human approval gate")
@click.option("--json-out", is_flag=True, default=False, help="Output results as JSON")
def run(command: str, template: Optional[str], max_parallel: int, no_approve: bool, json_out: bool):
    """Run the fleet with a natural language COMMAND.

    \b
    Examples:
      fleetos run "Launch my newsletter to $15k MRR in 90 days"
      fleetos run "Build a lead-gen agency for SaaS companies" --template leadgen_agency_v1
    """
    click.echo(click.style("\n🚀 FleetOS — Launching fleet run\n", fg="cyan", bold=True))
    click.echo(f"   Command  : {command}")
    if template:
        click.echo(f"   Template : {template}")
    click.echo(f"   Parallel : {max_parallel}")
    click.echo()

    # Build initial state
    state = {
        "raw_command": command,
        "session_id": f"run_{int(time.time())}",
        "status": "starting",
    }
    if template:
        state["template_name"] = template
    if no_approve:
        state["approved"] = True  # pre-approve

    # Import and run graph
    try:
        from fleetos.core.graph import build_graph
    except ImportError as exc:
        click.echo(click.style(f"❌ Import error: {exc}", fg="red"))
        click.echo("   Run: pip install -r requirements.txt")
        sys.exit(1)

    graph = build_graph()

    # Step-through progress
    steps = [
        "Parsing command",
        "Planning fleet",
        "Verifying confidence",
        "Executing agents",
        "Collecting artifacts",
        "Storing memory",
        "Building report",
    ]

    with click.progressbar(
        steps,
        label=click.style("Running", fg="yellow"),
        item_show_func=lambda s: f"  {s}" if s else "",
    ) as bar:
        for _ in bar:
            time.sleep(0.1)  # visual pacing only

    # Actual run
    try:
        result = graph.invoke(state)
    except Exception as exc:
        click.echo(click.style(f"\n❌ Fleet run failed: {exc}", fg="red"))
        logger.exception(exc)
        sys.exit(1)

    # Handle pending approval
    if result.get("needs_approval") and not result.get("approved"):
        click.echo(click.style("\n⏸️  Human approval required\n", fg="yellow", bold=True))
        click.echo(f"   Confidence : {result.get('confidence', 0):.0f}/100")
        click.echo(f"   Risk level : {result.get('risk_level', '?').upper()}")
        click.echo()

        click.echo("Planned agents:")
        for agent in result.get("agents", []):
            click.echo(f"   • [{agent['role']}] {agent['task'][:90]}")
        click.echo()

        if click.confirm("Approve this fleet run?", default=True):
            result["approved"] = True
            result["approval_reason"] = "cli_manual"
            # Re-run from execute_parallel onwards
            try:
                result = graph.invoke({**result, "status": "executing"})
            except Exception as exc:
                click.echo(click.style(f"❌ Execution failed: {exc}", fg="red"))
                sys.exit(1)
        else:
            click.echo(click.style("Run rejected.", fg="red"))
            sys.exit(0)

    # Output
    if json_out:
        click.echo(json.dumps(result, indent=2, default=str))
    else:
        summary = result.get("summary", "No summary generated.")
        click.echo(click.style("\n" + "─" * 60, fg="green"))
        click.echo(summary)
        click.echo(click.style("─" * 60 + "\n", fg="green"))

        artifacts = result.get("results", [])
        if artifacts:
            click.echo(click.style(f"✅ {len(artifacts)} artifacts generated\n", fg="green"))

        errors = result.get("errors", [])
        if errors:
            click.echo(click.style(f"⚠️  {len(errors)} errors\n", fg="yellow"))
            for e in errors:
                click.echo(f"   [{e['role']}] {e['error']}")


# ---------------------------------------------------------------------------
# fleet dashboard
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--port", default=8501, show_default=True, help="Streamlit port")
def dashboard(port: int):
    """Launch the Streamlit monitoring dashboard."""
    import subprocess

    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"
    if not dashboard_path.exists():
        click.echo(click.style("❌ Dashboard not found", fg="red"))
        sys.exit(1)

    click.echo(click.style(f"🖥️  Launching dashboard on http://localhost:{port}", fg="cyan"))
    subprocess.run(
        ["streamlit", "run", str(dashboard_path), "--server.port", str(port)],
        check=False,
    )


# ---------------------------------------------------------------------------
# fleet webhook
# ---------------------------------------------------------------------------

@cli.command()
@click.option("--port", default=8443, show_default=True, help="Webhook server port")
def webhook(port: int):
    """Start the Telegram approval webhook server."""
    from fleetos.webhook import start_webhook_server

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        click.echo(click.style("⚠️  TELEGRAM_BOT_TOKEN not set in .env", fg="yellow"))
        click.echo("   Webhook will start but cannot communicate with Telegram.")

    click.echo(click.style(f"📡 Webhook server starting on port {port}…", fg="cyan"))
    click.echo(f"   Health check : http://localhost:{port}/health")
    click.echo(f"   Telegram POST: http://localhost:{port}/webhook")

    start_webhook_server(port=port)

    click.echo(click.style("✅ Webhook server running. Press Ctrl+C to stop.", fg="green"))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        from fleetos.webhook import stop_webhook_server
        stop_webhook_server()
        click.echo("\nWebhook server stopped.")


# ---------------------------------------------------------------------------
# fleet status
# ---------------------------------------------------------------------------

@cli.command()
def status():
    """Show service health and configuration status."""
    import urllib.request

    click.echo(click.style("\n🔍 FleetOS Status\n", fg="cyan", bold=True))

    # .env check
    env_path = Path(".env")
    click.echo(f"  .env file       : {'✅' if env_path.exists() else '❌ missing'}")

    # Python imports
    modules = {
        "langgraph": "LangGraph DAG",
        "streamlit": "Dashboard",
        "chromadb": "ChromaDB (vector store)",
        "redis": "Redis client",
        "aiohttp": "Async HTTP (Ollama)",
    }
    click.echo()
    click.echo("  Python packages:")
    for mod, label in modules.items():
        try:
            __import__(mod)
            click.echo(f"    ✅ {label} ({mod})")
        except ImportError:
            click.echo(click.style(f"    ❌ {label} ({mod}) — not installed", fg="yellow"))

    # Ollama
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    click.echo()
    click.echo(f"  Ollama ({ollama_url}):")
    try:
        with urllib.request.urlopen(f"{ollama_url}/api/tags", timeout=3) as resp:
            data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            click.echo(f"    ✅ Online — models: {', '.join(models) or 'none pulled'}")
    except Exception as exc:
        click.echo(click.style(f"    ❌ Offline ({exc})", fg="red"))

    # Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    click.echo()
    click.echo(f"  Redis ({redis_url}):")
    try:
        import redis as _redis
        r = _redis.from_url(redis_url, socket_connect_timeout=2)
        r.ping()
        click.echo("    ✅ Online")
    except Exception:
        click.echo(click.style("    ⚠️  Offline (non-critical for Phase 2)", fg="yellow"))

    click.echo()


# ---------------------------------------------------------------------------
# fleet search
# ---------------------------------------------------------------------------

@cli.command()
@click.argument("query")
@click.option("--limit", "-n", default=5, show_default=True, help="Max results")
def search(query: str, limit: int):
    """Search the artifact memory store for QUERY."""
    try:
        from fleetos.core.memory import Memory
        mem = Memory()
        results = mem.search(query, top_k=limit)

        if not results:
            click.echo(f"No artifacts found for: {query!r}")
            return

        click.echo(click.style(f"\n🔍 {len(results)} result(s) for {query!r}\n", fg="cyan"))
        for r in results:
            click.echo(click.style(f"  [{r.get('role', '?')}]", fg="yellow", bold=True))
            content = str(r.get("content", ""))[:300]
            click.echo(f"  {content}")
            click.echo()

    except Exception as exc:
        click.echo(click.style(f"❌ Search failed: {exc}", fg="red"))


# ---------------------------------------------------------------------------
# fleet configure
# ---------------------------------------------------------------------------

@cli.command()
def configure():
    """Interactive configuration wizard — writes settings to .env."""
    click.echo(click.style("\n⚙️  FleetOS Configuration Wizard\n", fg="cyan", bold=True))

    env_path = Path(".env")
    existing = {}

    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                existing[k.strip()] = v.strip()

    def _ask(key: str, prompt: str, default: str = "") -> str:
        cur = existing.get(key, default)
        val = click.prompt(prompt, default=cur)
        return val

    settings = {
        "OLLAMA_BASE_URL": _ask("OLLAMA_BASE_URL", "Ollama URL", "http://localhost:11434"),
        "OLLAMA_MODEL": _ask("OLLAMA_MODEL", "Ollama model", "llama3.1"),
        "TELEGRAM_BOT_TOKEN": _ask("TELEGRAM_BOT_TOKEN", "Telegram bot token (leave blank to skip)", ""),
        "TELEGRAM_CHAT_ID": _ask("TELEGRAM_CHAT_ID", "Telegram chat ID", ""),
        "WEBHOOK_PORT": _ask("WEBHOOK_PORT", "Webhook port", "8443"),
        "CHROMA_PATH": _ask("CHROMA_PATH", "ChromaDB path", "./data/chroma"),
        "REDIS_URL": _ask("REDIS_URL", "Redis URL", "redis://localhost:6379"),
        "LOG_LEVEL": _ask("LOG_LEVEL", "Log level (DEBUG/INFO/WARNING)", "INFO"),
    }

    lines = ["# FleetOS configuration — generated by `fleetos configure`\n"]
    for k, v in settings.items():
        lines.append(f"{k}={v}")

    env_path.write_text("\n".join(lines) + "\n")
    click.echo(click.style("\n✅ Configuration saved to .env\n", fg="green"))


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()

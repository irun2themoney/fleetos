"""
FleetOS CLI: Command-line interface for fleet operations.

Entry point: `fleetos run "Your natural language command"`
"""

import asyncio
import logging
import click
import json
from pathlib import Path
from typing import Dict, Any

from fleetos.core.planner import Planner
from fleetos.core.orchestrator import Orchestrator
from fleetos.core.memory import MemoryManager
from fleetos.core.verifier import Verifier

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_template(template_name: str) -> Dict[str, Any]:
    """
    Load a business template.

    Args:
        template_name: Template name (e.g., "newsletter", "leadgen")

    Returns:
        Template dictionary
    """
    template_path = Path(__file__).parent / "templates" / f"{template_name}_v1.json"

    if template_path.exists():
        with open(template_path) as f:
            return json.load(f)

    # Default template
    return {
        "roles": ["Strategy", "Content", "Marketing", "Sales"],
        "tools": [],
        "verification_rules": []
    }


@click.group()
def main():
    """FleetOS: Kubernetes-style orchestration for autonomous agents."""
    pass


@main.command()
@click.argument('command')
@click.option('--template', default='auto', help='Business template to use')
@click.option('--async', is_flag=True, help='Run asynchronously')
def run(command: str, template: str, async_mode: bool):
    """
    Run a FleetOS command.

    Example: fleetos run "Launch my newsletter to $15k MRR"
    """
    logger.info(f"FleetOS Command: {command}")

    # Phase 1: Initialize components
    planner = Planner()
    orchestrator = Orchestrator()
    memory = MemoryManager()
    verifier = Verifier()

    # Phase 2: Load template
    if template == 'auto':
        # Auto-detect template from command
        template_name = _detect_template(command)
    else:
        template_name = template

    template_data = load_template(template_name)
    logger.info(f"Using template: {template_name}")

    # Phase 3: Plan decomposition
    agents = planner.decompose(command, template_data)
    if not planner.validate_decomposition(agents):
        click.echo("Error: Invalid decomposition", err=True)
        return

    click.echo(f"✓ Decomposed into {len(agents)} roles")
    for agent in agents:
        click.echo(f"  - {agent['role']}")

    # Phase 4: Execute orchestration
    if async_mode:
        results = asyncio.run(orchestrator.run_parallel(agents, command))
    else:
        results = asyncio.run(orchestrator.run_parallel(agents, command))

    # Phase 5: Store results and show summary
    for artifact in results.get("artifacts", []):
        memory.store_artifact(
            artifact_type=artifact.get("role"),
            content=str(artifact),
            metadata={"command": command}
        )

    click.echo(f"✓ Fleet execution completed")
    click.echo(f"  Artifacts: {len(results.get('artifacts', []))}")
    click.echo(f"  Errors: {len(results.get('errors', []))}")

    # Show any errors
    if results.get("errors"):
        click.echo("\nErrors encountered:")
        for error in results["errors"]:
            click.echo(f"  - {error['role']}: {error['error']}")

    logger.info("Command execution complete")


@main.command()
def configure():
    """
    Interactive configuration wizard.

    Sets up: Telegram, OpenClaw, Ollama, integrations.
    """
    click.echo("FleetOS Configuration Wizard")
    click.echo("=" * 40)

    # Phase 1: Create .env if needed
    env_path = Path(".env")
    if not env_path.exists():
        click.echo("Creating .env file...")
        with open(".env.example") as f:
            example = f.read()

        with open(".env", "w") as f:
            f.write(example)

        click.echo("✓ Created .env (fill in your API keys)")

    # Phase 2: Test Ollama connection
    click.echo("\nTesting Ollama...")
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        if resp.status_code == 200:
            click.echo("✓ Ollama is running")
        else:
            click.echo("⚠ Ollama endpoint not responding")
    except Exception as e:
        click.echo(f"✗ Ollama connection failed: {e}")

    # Phase 3: Configure Telegram (if needed)
    if click.confirm("Configure Telegram for approvals?"):
        token = click.prompt("Telegram bot token")
        chat_id = click.prompt("Your Telegram chat ID")

        # Update .env
        with open(".env", "a") as f:
            f.write(f"\nTELEGRAM_BOT_TOKEN={token}\n")
            f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")

        click.echo("✓ Telegram configured")

    click.echo("\nConfiguration complete!")


@main.command()
def status():
    """Show FleetOS status and system information."""
    click.echo("FleetOS Status")
    click.echo("=" * 40)

    memory = MemoryManager()
    context = memory.get_company_context()

    click.echo(f"Artifacts stored: {context['artifacts_count']}")
    click.echo(f"Relationships: {context['relationships_count']}")
    click.echo(f"Timestamp: {context['timestamp']}")


@main.command()
@click.argument('query')
@click.option('--type', default=None, help='Filter by artifact type')
def search(query: str, type: str):
    """Search company memory for artifacts."""
    memory = MemoryManager()
    results = memory.search(query, artifact_type=type)

    click.echo(f"Search results for: {query}")
    click.echo("=" * 40)

    if not results:
        click.echo("No results found")
        return

    for result in results:
        click.echo(f"\n[{result['type']}] {result['artifact_id']}")
        click.echo(f"  Relevance: {result['relevance']:.2%}")
        click.echo(f"  Created: {result['created_at']}")


def _detect_template(command: str) -> str:
    """
    Auto-detect template from command.

    Args:
        command: User command

    Returns:
        Template name
    """
    command_lower = command.lower()

    if "newsletter" in command_lower:
        return "newsletter"
    elif "lead" in command_lower or "leads" in command_lower:
        return "leadgen_agency"
    elif "saas" in command_lower or "app" in command_lower:
        return "microsaas"
    else:
        return "newsletter"  # Default


if __name__ == "__main__":
    main()

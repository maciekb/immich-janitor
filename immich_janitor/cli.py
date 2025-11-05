"""CLI interface for Immich Janitor."""

import click
from rich.console import Console
from rich.table import Table

from immich_janitor.client import ImmichClient
from immich_janitor.config import load_config

# Load .env file at module import
load_config()

console = Console()


@click.group()
@click.option(
    "--api-url",
    envvar="IMMICH_API_URL",
    required=True,
    help="Immich API URL (or set IMMICH_API_URL env var)",
)
@click.option(
    "--api-key",
    envvar="IMMICH_API_KEY",
    required=True,
    help="Immich API key (or set IMMICH_API_KEY env var)",
)
@click.pass_context
def cli(ctx, api_url: str, api_key: str):
    """Immich Janitor - Manage your Immich library via API."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = ImmichClient(api_url=api_url, api_key=api_key)


@cli.command()
@click.option(
    "--limit",
    type=int,
    default=100,
    help="Maximum number of assets to list (default: 100)",
)
@click.option(
    "--pattern",
    help="Filter assets by filename pattern (regex)",
)
@click.pass_context
def list_assets(ctx, limit: int, pattern: str | None):
    """List assets from Immich library."""
    client: ImmichClient = ctx.obj["client"]
    
    try:
        with console.status("[bold green]Fetching assets..."):
            assets = client.get_all_assets(limit=limit, pattern=pattern)
        
        if not assets:
            console.print("[yellow]No assets found.[/yellow]")
            return
        
        # Create table
        table = Table(title=f"Assets ({len(assets)} found)")
        table.add_column("ID", style="cyan")
        table.add_column("Filename", style="magenta")
        table.add_column("Type", style="green")
        table.add_column("Created", style="blue")
        
        for asset in assets:
            table.add_row(
                asset.id[:8] + "...",
                asset.original_file_name,
                asset.type,
                asset.created_at.strftime("%Y-%m-%d %H:%M"),
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.argument("pattern")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be deleted without actually deleting",
)
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def delete_by_pattern(ctx, pattern: str, dry_run: bool, force: bool):
    """Delete assets matching a regex pattern."""
    client: ImmichClient = ctx.obj["client"]
    
    try:
        # First, list matching assets
        with console.status("[bold green]Finding matching assets..."):
            assets = client.get_all_assets(pattern=pattern)
        
        if not assets:
            console.print("[yellow]No assets matching pattern found.[/yellow]")
            return
        
        # Show what will be deleted
        console.print(f"\n[yellow]Found {len(assets)} asset(s) matching pattern '{pattern}':[/yellow]\n")
        
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Filename", style="magenta")
        table.add_column("Type", style="green")
        
        for asset in assets:
            table.add_row(
                asset.id[:8] + "...",
                asset.original_file_name,
                asset.type,
            )
        
        console.print(table)
        
        if dry_run:
            console.print("\n[blue]Dry run - no assets were deleted.[/blue]")
            return
        
        # Ask for confirmation
        if not force:
            confirm = click.confirm(
                f"\nAre you sure you want to delete {len(assets)} asset(s)?",
                default=False,
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        # Delete assets
        asset_ids = [asset.id for asset in assets]
        with console.status("[bold red]Deleting assets..."):
            client.delete_assets(asset_ids)
        
        console.print(f"[green]Successfully deleted {len(assets)} asset(s).[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


if __name__ == "__main__":
    cli()

"""CLI interface for Immich Janitor."""

import click
from rich.console import Console
from rich.table import Table

from immich_janitor.cli_duplicates import duplicates
from immich_janitor.cli_stats import stats
from immich_janitor.cli_trash import trash
from immich_janitor.client import ImmichClient
from immich_janitor.config import load_config
from immich_janitor.regex_helper import interactive_regex_builder

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


# Register command groups
cli.add_command(stats)
cli.add_command(duplicates)
cli.add_command(trash)


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
@click.argument("pattern", required=False)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive mode: build regex from examples",
)
@click.option(
    "--examples",
    help="Example filenames (comma-separated) for pattern detection",
)
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
def delete_by_pattern(ctx, pattern: str | None, interactive: bool, examples: str | None, dry_run: bool, force: bool):
    """Delete assets matching a regex pattern.
    
    You can provide a pattern directly, or use --interactive or --examples
    to build a pattern from example filenames.
    
    Examples:
    
        # Direct pattern
        immich-janitor delete-by-pattern "^IMG_\\d+\\.jpg$"
        
        # Interactive mode
        immich-janitor delete-by-pattern --interactive
        
        # Quick mode with examples
        immich-janitor delete-by-pattern --examples "IMG_001.jpg,IMG_002.jpg"
    """
    client: ImmichClient = ctx.obj["client"]
    
    try:
        # Handle interactive/examples mode
        if interactive or examples:
            if pattern:
                console.print("[yellow]Warning: Pattern argument ignored in interactive mode.[/yellow]")
            
            # Fetch all assets for testing patterns
            with console.status("[bold green]Fetching assets for pattern matching..."):
                all_assets = client.get_all_assets()
            
            if not all_assets:
                console.print("[yellow]No assets found in library.[/yellow]")
                return
            
            # Parse examples if provided
            example_list = None
            if examples:
                example_list = [e.strip() for e in examples.split(',') if e.strip()]
            
            # Run interactive builder
            pattern = interactive_regex_builder(examples=example_list, all_assets=all_assets)
            
            if not pattern:
                console.print("[yellow]Pattern selection cancelled.[/yellow]")
                return
        
        elif not pattern:
            console.print("[red]Error: Pattern required. Use --interactive or provide a pattern.[/red]")
            console.print("Try: immich-janitor delete-by-pattern --help")
            raise click.Abort()
        
        # First, list matching assets
        with console.status("[bold green]Finding matching assets..."):
            assets = client.get_all_assets(pattern=pattern)
        
        if not assets:
            console.print("[yellow]No assets matching pattern found.[/yellow]")
            return
        
        # Show what will be deleted
        console.print(f"\n[yellow]Found {len(assets)} asset(s) matching pattern '{pattern}':[/yellow]\n")
        
        # Show sample of matches
        sample_size = min(20, len(assets))
        table = Table(title=f"Sample Matches (showing {sample_size} of {len(assets)})")
        table.add_column("ID", style="cyan")
        table.add_column("Filename", style="magenta")
        table.add_column("Type", style="green")
        
        for asset in assets[:sample_size]:
            table.add_row(
                asset.id[:8] + "...",
                asset.original_file_name,
                asset.type,
            )
        
        console.print(table)
        
        if len(assets) > sample_size:
            console.print(f"\n[dim]... and {len(assets) - sample_size} more[/dim]")
        
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

"""CLI commands for trash management."""

import re
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table

from immich_janitor.client import ImmichClient
from immich_janitor.utils import format_size, is_older_than, parse_time_delta

console = Console()


@click.group()
def trash():
    """Manage trashed assets."""
    pass


@trash.command()
@click.option(
    "--older-than",
    help="Filter assets older than specified time (e.g., '30d', '7d')",
)
@click.pass_context
def list(ctx, older_than: str | None):
    """List assets in trash."""
    client: ImmichClient = ctx.obj["client"]
    
    try:
        with console.status("[bold green]Fetching trashed assets..."):
            assets = client.get_trash_assets()
        
        # Filter by age if specified
        if older_than:
            delta = parse_time_delta(older_than)
            assets = [
                asset
                for asset in assets
                if asset.deleted_at and is_older_than(asset.deleted_at, delta)
            ]
        
        if not assets:
            console.print("[green]Trash is empty! ✨[/green]")
            return
        
        # Show summary
        total_size = sum(asset.file_size_in_bytes or 0 for asset in assets)
        console.print(f"\n[yellow]Found {len(assets)} assets in trash[/yellow]")
        console.print(f"[blue]Total size: {format_size(total_size)}[/blue]\n")
        
        # Create table
        table = Table(title="🗑️  Trash")
        table.add_column("ID", style="dim")
        table.add_column("Filename", style="magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Size", style="green", justify="right")
        table.add_column("Deleted", style="red")
        
        for asset in assets:
            deleted_str = asset.deleted_at.strftime("%Y-%m-%d") if asset.deleted_at else "Unknown"
            
            table.add_row(
                asset.id[:12] + "...",
                asset.original_file_name,
                asset.type,
                format_size(asset.file_size_in_bytes),
                deleted_str,
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@trash.command()
@click.option(
    "--pattern",
    help="Restore assets matching regex pattern",
)
@click.option(
    "--all",
    "restore_all",
    is_flag=True,
    help="Restore all assets from trash",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be restored without actually restoring",
)
@click.option(
    "--force",
    is_flag=True,
    help="Skip confirmation prompt",
)
@click.pass_context
def restore(ctx, pattern: str | None, restore_all: bool, dry_run: bool, force: bool):
    """Restore assets from trash."""
    client: ImmichClient = ctx.obj["client"]
    
    if not pattern and not restore_all:
        console.print("[red]Error: Specify --pattern or --all[/red]")
        raise click.Abort()
    
    try:
        with console.status("[bold green]Fetching trashed assets..."):
            assets = client.get_trash_assets()
        
        if not assets:
            console.print("[green]Trash is empty![/green]")
            return
        
        # Filter by pattern if provided
        if pattern and not restore_all:
            regex = re.compile(pattern)
            assets = [
                asset
                for asset in assets
                if regex.search(asset.original_file_name)
            ]
        
        if not assets:
            console.print("[yellow]No assets matching criteria found in trash.[/yellow]")
            return
        
        # Show what will be restored
        console.print(f"\n[yellow]Found {len(assets)} asset(s) to restore[/yellow]\n")
        
        table = Table()
        table.add_column("Filename", style="magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Deleted", style="red")
        
        for asset in assets[:20]:  # Show first 20
            deleted_str = asset.deleted_at.strftime("%Y-%m-%d") if asset.deleted_at else "Unknown"
            table.add_row(
                asset.original_file_name,
                asset.type,
                deleted_str,
            )
        
        if len(assets) > 20:
            table.add_row("...", "...", "...")
        
        console.print(table)
        
        if dry_run:
            console.print("\n[blue]Dry run - no assets were restored.[/blue]")
            return
        
        # Ask for confirmation
        if not force:
            confirm = click.confirm(
                f"\nAre you sure you want to restore {len(assets)} asset(s)?",
                default=False,
            )
            if not confirm:
                console.print("[yellow]Restore cancelled.[/yellow]")
                return
        
        # Restore assets
        asset_ids = [asset.id for asset in assets]
        
        with console.status("[bold green]Restoring assets..."):
            # Restore in batches
            batch_size = 100
            for i in range(0, len(asset_ids), batch_size):
                batch = asset_ids[i:i + batch_size]
                client.restore_from_trash(batch)
        
        console.print(f"\n[green]✓ Successfully restored {len(assets)} asset(s)![/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@trash.command()
@click.option(
    "--older-than",
    help="Empty only assets older than specified time (e.g., '30d')",
)
@click.option(
    "--all",
    "empty_all",
    is_flag=True,
    help="Empty entire trash",
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
def empty(ctx, older_than: str | None, empty_all: bool, dry_run: bool, force: bool):
    """Permanently delete assets from trash."""
    client: ImmichClient = ctx.obj["client"]
    
    if not older_than and not empty_all:
        console.print("[red]Error: Specify --older-than or --all[/red]")
        raise click.Abort()
    
    try:
        with console.status("[bold green]Fetching trashed assets..."):
            assets = client.get_trash_assets()
        
        if not assets:
            console.print("[green]Trash is already empty![/green]")
            return
        
        # Filter by age if specified
        if older_than and not empty_all:
            delta = parse_time_delta(older_than)
            assets = [
                asset
                for asset in assets
                if asset.deleted_at and is_older_than(asset.deleted_at, delta)
            ]
        
        if not assets:
            console.print("[yellow]No assets matching criteria found.[/yellow]")
            return
        
        # Calculate space to be freed
        total_size = sum(asset.file_size_in_bytes or 0 for asset in assets)
        
        # Show warning
        console.print(f"\n[red]⚠️  WARNING: This will PERMANENTLY delete {len(assets)} asset(s)![/red]")
        console.print(f"[yellow]Space to be freed: {format_size(total_size)}[/yellow]\n")
        
        # Show sample
        console.print("[cyan]Sample of assets to be deleted:[/cyan]")
        table = Table()
        table.add_column("Filename", style="magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Deleted", style="red")
        
        for asset in assets[:20]:
            deleted_str = asset.deleted_at.strftime("%Y-%m-%d") if asset.deleted_at else "Unknown"
            table.add_row(
                asset.original_file_name,
                asset.type,
                deleted_str,
            )
        
        if len(assets) > 20:
            table.add_row("...", "...", "...")
        
        console.print(table)
        
        if dry_run:
            console.print("\n[blue]Dry run - no assets were deleted.[/blue]")
            return
        
        # Ask for confirmation
        if not force:
            console.print("\n[red bold]THIS CANNOT BE UNDONE![/red bold]")
            confirm = click.confirm(
                f"Are you ABSOLUTELY sure you want to permanently delete {len(assets)} asset(s)?",
                default=False,
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        # Empty trash
        asset_ids = [asset.id for asset in assets]
        
        with console.status("[bold red]Permanently deleting assets..."):
            client.empty_trash(asset_ids if not empty_all else None)
        
        console.print(f"\n[green]✓ Successfully deleted {len(assets)} asset(s)![/green]")
        console.print(f"[blue]Space freed: {format_size(total_size)}[/blue]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@trash.command()
@click.pass_context
def stats(ctx):
    """Show trash statistics."""
    client: ImmichClient = ctx.obj["client"]
    
    try:
        with console.status("[bold green]Fetching trashed assets..."):
            assets = client.get_trash_assets()
        
        if not assets:
            console.print("[green]Trash is empty! ✨[/green]")
            return
        
        # Calculate stats
        total_count = len(assets)
        total_size = sum(asset.file_size_in_bytes or 0 for asset in assets)
        
        image_count = sum(1 for asset in assets if asset.type == "IMAGE")
        video_count = sum(1 for asset in assets if asset.type == "VIDEO")
        
        # Date stats
        if any(asset.deleted_at for asset in assets):
            deleted_dates = [asset.deleted_at for asset in assets if asset.deleted_at]
            oldest_deletion = min(deleted_dates) if deleted_dates else None
            newest_deletion = max(deleted_dates) if deleted_dates else None
        else:
            oldest_deletion = newest_deletion = None
        
        # Create stats table
        table = Table(title="🗑️  Trash Statistics", show_header=False)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Assets", str(total_count))
        table.add_row("Total Size", format_size(total_size))
        table.add_row("", "")
        table.add_row("Images", f"{image_count} ({image_count/total_count*100:.1f}%)")
        table.add_row("Videos", f"{video_count} ({video_count/total_count*100:.1f}%)")
        table.add_row("", "")
        
        if oldest_deletion and newest_deletion:
            table.add_row("Oldest Deletion", oldest_deletion.strftime("%Y-%m-%d"))
            table.add_row("Newest Deletion", newest_deletion.strftime("%Y-%m-%d"))
            
            days_in_trash = (datetime.now(newest_deletion.tzinfo) - oldest_deletion).days
            table.add_row("Time Span", f"{days_in_trash} days")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()

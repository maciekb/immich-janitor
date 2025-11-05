"""CLI commands for duplicate management."""

import click
from rich.console import Console
from rich.table import Table

from immich_janitor.client import ImmichClient
from immich_janitor.utils import format_size

console = Console()


@click.group()
def duplicates():
    """Manage duplicate assets."""
    pass


@duplicates.command()
@click.pass_context
def find(ctx):
    """Find and list duplicate asset groups."""
    client: ImmichClient = ctx.obj["client"]
    
    try:
        with console.status("[bold green]Finding duplicates..."):
            groups = client.get_duplicates()
        
        if not groups:
            console.print("[green]No duplicates found! ✨[/green]")
            return
        
        # Summary stats
        total_groups = len(groups)
        total_duplicates = sum(g.asset_count for g in groups)
        total_wasted_space = sum(
            g.total_size - (g.assets[0].file_size_in_bytes or 0)
            for g in groups
            if g.assets
        )
        
        console.print(f"\n[yellow]Found {total_groups} duplicate groups with {total_duplicates} total assets[/yellow]")
        console.print(f"[red]Potential space savings: {format_size(total_wasted_space)}[/red]\n")
        
        # List groups
        for i, group in enumerate(groups, 1):
            console.print(f"\n[cyan]═══ Group {i}/{total_groups} (ID: {group.id}) ═══[/cyan]")
            
            table = Table(show_header=True)
            table.add_column("Asset ID", style="dim")
            table.add_column("Filename", style="magenta")
            table.add_column("Size", style="green", justify="right")
            table.add_column("Created", style="blue")
            
            for asset in group.assets:
                table.add_row(
                    asset.id[:12] + "...",
                    asset.original_file_name,
                    format_size(asset.file_size_in_bytes),
                    asset.created_at.strftime("%Y-%m-%d %H:%M"),
                )
            
            console.print(table)
            console.print(f"[dim]Total size: {format_size(group.total_size)}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@duplicates.command()
@click.option(
    "--keep",
    type=click.Choice(["oldest", "newest", "largest"]),
    default="oldest",
    help="Which asset to keep (default: oldest)",
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
def delete(ctx, keep: str, dry_run: bool, force: bool):
    """Delete duplicate assets, keeping one from each group."""
    client: ImmichClient = ctx.obj["client"]
    
    try:
        with console.status("[bold green]Finding duplicates..."):
            groups = client.get_duplicates()
        
        if not groups:
            console.print("[green]No duplicates found![/green]")
            return
        
        # Determine which assets to delete
        to_delete = []
        kept_assets = []
        
        for group in groups:
            if not group.assets:
                continue
            
            # Sort assets based on keep strategy
            if keep == "oldest":
                sorted_assets = sorted(group.assets, key=lambda a: a.created_at)
            elif keep == "newest":
                sorted_assets = sorted(group.assets, key=lambda a: a.created_at, reverse=True)
            else:  # largest
                sorted_assets = sorted(
                    group.assets,
                    key=lambda a: a.file_size_in_bytes or 0,
                    reverse=True
                )
            
            # Keep first, delete rest
            kept_assets.append(sorted_assets[0])
            to_delete.extend(sorted_assets[1:])
        
        if not to_delete:
            console.print("[green]No duplicates to delete![/green]")
            return
        
        # Calculate space savings
        space_saved = sum(asset.file_size_in_bytes or 0 for asset in to_delete)
        
        # Show what will be deleted
        console.print(f"\n[yellow]Found {len(groups)} duplicate groups[/yellow]")
        console.print(f"[green]Will keep {len(kept_assets)} assets (strategy: {keep})[/green]")
        console.print(f"[red]Will delete {len(to_delete)} duplicates[/red]")
        console.print(f"[blue]Space to be freed: {format_size(space_saved)}[/blue]\n")
        
        # Show sample
        console.print("[cyan]Sample of assets to be deleted:[/cyan]")
        table = Table()
        table.add_column("Filename", style="magenta")
        table.add_column("Size", style="green")
        table.add_column("Created", style="blue")
        
        for asset in to_delete[:10]:
            table.add_row(
                asset.original_file_name,
                format_size(asset.file_size_in_bytes),
                asset.created_at.strftime("%Y-%m-%d"),
            )
        
        if len(to_delete) > 10:
            table.add_row("...", "...", "...")
        
        console.print(table)
        
        if dry_run:
            console.print("\n[blue]Dry run - no assets were deleted.[/blue]")
            return
        
        # Ask for confirmation
        if not force:
            confirm = click.confirm(
                f"\nAre you sure you want to delete {len(to_delete)} duplicate assets?",
                default=False,
            )
            if not confirm:
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return
        
        # Delete duplicates
        asset_ids = [asset.id for asset in to_delete]
        
        with console.status("[bold red]Deleting duplicates..."):
            # Delete in batches
            batch_size = 100
            for i in range(0, len(asset_ids), batch_size):
                batch = asset_ids[i:i + batch_size]
                client.delete_assets(batch, force=False)  # Send to trash
        
        console.print(f"\n[green]✓ Successfully deleted {len(to_delete)} duplicate assets![/green]")
        console.print(f"[blue]Space freed: {format_size(space_saved)}[/blue]")
        console.print("[dim]Assets moved to trash. Use 'trash empty' to permanently delete.[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()

"""CLI commands for statistics."""

from collections import Counter
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table

from immich_janitor.client import ImmichClient
from immich_janitor.utils import format_size

console = Console()


@click.group()
def stats():
    """Show library statistics."""
    pass


@stats.command()
@click.pass_context
def overview(ctx):
    """Show general library statistics."""
    client: ImmichClient = ctx.obj["client"]
    
    try:
        with console.status("[bold green]Fetching assets..."):
            assets = client.get_all_assets()
        
        if not assets:
            console.print("[yellow]No assets found.[/yellow]")
            return
        
        # Calculate statistics
        total_count = len(assets)
        total_size = sum(asset.file_size_in_bytes or 0 for asset in assets)
        
        image_count = sum(1 for asset in assets if asset.type == "IMAGE")
        video_count = sum(1 for asset in assets if asset.type == "VIDEO")
        
        favorites_count = sum(1 for asset in assets if asset.is_favorite)
        archived_count = sum(1 for asset in assets if asset.is_archived)
        trashed_count = sum(1 for asset in assets if asset.is_trashed)
        
        # Date range (using photo taken date from EXIF when available)
        dates = [asset.photo_taken_at for asset in assets]
        oldest_date = min(dates) if dates else None
        newest_date = max(dates) if dates else None
        
        # Create overview table
        table = Table(title="📊 Library Statistics", show_header=False)
        table.add_column("Metric", style="cyan", width=30)
        table.add_column("Value", style="magenta")
        
        table.add_row("Total Assets", str(total_count))
        table.add_row("Total Size", format_size(total_size))
        table.add_row("", "")  # Empty row
        table.add_row("Images", f"{image_count} ({image_count/total_count*100:.1f}%)")
        table.add_row("Videos", f"{video_count} ({video_count/total_count*100:.1f}%)")
        table.add_row("", "")
        table.add_row("Favorites", str(favorites_count))
        table.add_row("Archived", str(archived_count))
        table.add_row("Trashed", str(trashed_count))
        table.add_row("", "")
        
        if oldest_date and newest_date:
            table.add_row("Oldest Asset", oldest_date.strftime("%Y-%m-%d"))
            table.add_row("Newest Asset", newest_date.strftime("%Y-%m-%d"))
            
            days_span = (newest_date - oldest_date).days
            table.add_row("Date Span", f"{days_span} days")
            
            if days_span > 0:
                avg_per_day = total_count / days_span
                table.add_row("Avg per Day", f"{avg_per_day:.1f} assets")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@stats.command()
@click.pass_context
def by_type(ctx):
    """Show breakdown by file type."""
    client: ImmichClient = ctx.obj["client"]
    
    try:
        with console.status("[bold green]Fetching assets..."):
            assets = client.get_all_assets()
        
        if not assets:
            console.print("[yellow]No assets found.[/yellow]")
            return
        
        # Count by file extension
        extensions = Counter()
        sizes_by_ext = {}
        
        for asset in assets:
            # Get extension from filename
            filename = asset.original_file_name
            ext = filename.rsplit(".", 1)[-1].upper() if "." in filename else "NO_EXT"
            
            extensions[ext] += 1
            sizes_by_ext[ext] = sizes_by_ext.get(ext, 0) + (asset.file_size_in_bytes or 0)
        
        # Create table
        table = Table(title="📁 Assets by File Type")
        table.add_column("Extension", style="cyan")
        table.add_column("Count", style="magenta", justify="right")
        table.add_column("Percentage", style="green", justify="right")
        table.add_column("Total Size", style="blue", justify="right")
        
        total_count = sum(extensions.values())
        
        # Sort by count descending
        for ext, count in extensions.most_common():
            percentage = count / total_count * 100
            size = sizes_by_ext.get(ext, 0)
            
            table.add_row(
                ext,
                str(count),
                f"{percentage:.1f}%",
                format_size(size),
            )
        
        console.print(table)
        console.print(f"\n[cyan]Total types: {len(extensions)}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()


@stats.command()
@click.option(
    "--group-by",
    type=click.Choice(["year", "month", "day"]),
    default="month",
    help="Grouping level (default: month)",
)
@click.pass_context
def by_date(ctx, group_by: str):
    """Show timeline statistics grouped by date."""
    client: ImmichClient = ctx.obj["client"]
    
    try:
        with console.status("[bold green]Fetching assets..."):
            assets = client.get_all_assets()
        
        if not assets:
            console.print("[yellow]No assets found.[/yellow]")
            return
        
        # Group by date (using photo taken date from EXIF when available)
        date_groups = Counter()
        
        for asset in assets:
            date = asset.photo_taken_at
            
            if group_by == "year":
                key = date.strftime("%Y")
            elif group_by == "month":
                key = date.strftime("%Y-%m")
            else:  # day
                key = date.strftime("%Y-%m-%d")
            
            date_groups[key] += 1
        
        # Create table
        table = Table(title=f"📅 Assets by {group_by.title()}")
        table.add_column("Date", style="cyan")
        table.add_column("Count", style="magenta", justify="right")
        table.add_column("Bar", style="green")
        
        # Sort by date
        max_count = max(date_groups.values()) if date_groups else 1
        
        for date_key in sorted(date_groups.keys()):
            count = date_groups[date_key]
            bar_length = int(count / max_count * 30)
            bar = "█" * bar_length
            
            table.add_row(date_key, str(count), bar)
        
        console.print(table)
        console.print(f"\n[cyan]Total periods: {len(date_groups)}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()

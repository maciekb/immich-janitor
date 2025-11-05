"""Interactive regex helper for pattern matching."""

import re
from collections import Counter
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.table import Table

from immich_janitor.models import Asset

console = Console()


@dataclass
class RegexSuggestion:
    """A suggested regex pattern with metadata."""

    pattern: str
    description: str
    priority: int  # Lower is better
    examples: list[str]  # Example filenames that match


class RegexHelper:
    """Helper for analyzing filenames and suggesting regex patterns."""

    def __init__(self, example_filenames: list[str]):
        """Initialize with example filenames.
        
        Args:
            example_filenames: List of example filenames to analyze
        """
        self.examples = example_filenames
        self.suggestions: list[RegexSuggestion] = []

    def analyze_patterns(self) -> list[RegexSuggestion]:
        """Analyze filenames and generate regex suggestions.
        
        Returns:
            List of RegexSuggestion objects, ordered by priority
        """
        self.suggestions = []
        
        # Extract components from examples
        prefixes = self._extract_prefixes()
        extensions = self._extract_extensions()
        has_numbers = self._check_for_numbers()
        date_patterns = self._extract_date_patterns()
        
        # Generate suggestions based on detected patterns
        
        # 1. Exact prefix + numbers + extension (most specific)
        if prefixes and extensions and has_numbers:
            for prefix in prefixes:
                for ext in extensions:
                    pattern = f"^{re.escape(prefix)}\\d+\\.{ext}$"
                    desc = f'Files starting with "{prefix}", followed by numbers, ending with ".{ext}"'
                    self.suggestions.append(
                        RegexSuggestion(pattern, desc, priority=1, examples=[])
                    )
        
        # 2. Multiple prefixes + numbers + extension
        if len(prefixes) > 1 and extensions and has_numbers:
            prefix_group = "|".join(re.escape(p) for p in prefixes)
            for ext in extensions:
                pattern = f"^({prefix_group})\\d+\\.{ext}$"
                desc = f'Files starting with any of: {", ".join(prefixes)}, then numbers and ".{ext}"'
                self.suggestions.append(
                    RegexSuggestion(pattern, desc, priority=2, examples=[])
                )
        
        # 3. Date patterns (YYYY-MM-DD or YYYYMMDD)
        if date_patterns:
            for date_type, date_regex in date_patterns.items():
                pattern = f".*{date_regex}.*"
                desc = f"Files containing {date_type} format dates"
                self.suggestions.append(
                    RegexSuggestion(pattern, desc, priority=3, examples=[])
                )
        
        # 4. Extension only (less specific)
        if extensions:
            for ext in extensions:
                pattern = f".*\\.{ext}$"
                desc = f'All files ending with ".{ext}"'
                self.suggestions.append(
                    RegexSuggestion(pattern, desc, priority=4, examples=[])
                )
        
        # 5. Prefix only (even less specific)
        if prefixes:
            for prefix in prefixes:
                pattern = f"^{re.escape(prefix)}.*"
                desc = f'All files starting with "{prefix}"'
                self.suggestions.append(
                    RegexSuggestion(pattern, desc, priority=5, examples=[])
                )
        
        # Sort by priority and remove duplicates
        seen = set()
        unique_suggestions = []
        for suggestion in sorted(self.suggestions, key=lambda s: s.priority):
            if suggestion.pattern not in seen:
                seen.add(suggestion.pattern)
                unique_suggestions.append(suggestion)
        
        return unique_suggestions[:5]  # Return top 5 suggestions

    def _extract_prefixes(self) -> list[str]:
        """Extract common prefixes from filenames."""
        # Find common prefixes (before first digit or underscore)
        prefixes = []
        for filename in self.examples:
            # Match prefix before numbers or underscore
            match = re.match(r'^([A-Za-z_]+)[_\d]', filename)
            if match:
                prefixes.append(match.group(1))
        
        # Return most common prefixes
        if not prefixes:
            return []
        
        counter = Counter(prefixes)
        # Return prefixes that appear in at least 50% of examples
        threshold = len(self.examples) * 0.3
        return [prefix for prefix, count in counter.most_common() if count >= threshold]

    def _extract_extensions(self) -> list[str]:
        """Extract common file extensions."""
        extensions = []
        for filename in self.examples:
            match = re.search(r'\.([a-zA-Z0-9]+)$', filename)
            if match:
                extensions.append(match.group(1).lower())
        
        if not extensions:
            return []
        
        counter = Counter(extensions)
        # Return extensions that appear in at least 30% of examples
        threshold = len(self.examples) * 0.3
        return [ext for ext, count in counter.most_common() if count >= threshold]

    def _check_for_numbers(self) -> bool:
        """Check if filenames contain numbers."""
        return any(re.search(r'\d', filename) for filename in self.examples)

    def _extract_date_patterns(self) -> dict[str, str]:
        """Detect date patterns in filenames."""
        patterns = {}
        
        # Check for YYYY-MM-DD
        if any(re.search(r'\d{4}-\d{2}-\d{2}', f) for f in self.examples):
            patterns['YYYY-MM-DD'] = r'\d{4}-\d{2}-\d{2}'
        
        # Check for YYYYMMDD
        if any(re.search(r'\d{8}', f) for f in self.examples):
            patterns['YYYYMMDD'] = r'\d{8}'
        
        # Check for YYYY_MM_DD
        if any(re.search(r'\d{4}_\d{2}_\d{2}', f) for f in self.examples):
            patterns['YYYY_MM_DD'] = r'\d{4}_\d{2}_\d{2}'
        
        return patterns

    def test_pattern(self, pattern: str, all_assets: list[Asset]) -> tuple[list[Asset], list[str]]:
        """Test a regex pattern against all assets.
        
        Args:
            pattern: Regex pattern to test
            all_assets: List of all assets to test against
            
        Returns:
            Tuple of (matching_assets, sample_filenames)
        """
        try:
            regex = re.compile(pattern)
        except re.error as e:
            console.print(f"[red]Invalid regex: {e}[/red]")
            return [], []
        
        matching_assets = [
            asset for asset in all_assets
            if regex.search(asset.original_file_name)
        ]
        
        # Get sample filenames (first 10)
        sample_filenames = [
            asset.original_file_name
            for asset in matching_assets[:10]
        ]
        
        return matching_assets, sample_filenames

    def explain_regex(self, pattern: str) -> str:
        """Generate human-readable explanation of regex pattern.
        
        Args:
            pattern: Regex pattern to explain
            
        Returns:
            Human-readable explanation
        """
        explanations = []
        
        # Start of string
        if pattern.startswith('^'):
            explanations.append("Must start with")
            pattern = pattern[1:]
        
        # End of string
        ends_with_dollar = pattern.endswith('$')
        if ends_with_dollar:
            pattern = pattern[:-1]
        
        # Common patterns
        parts = []
        
        # Escaped literal text
        literal_matches = re.findall(r'([^\\[\]().*+?{}|]+)', pattern)
        for literal in literal_matches:
            if literal and literal not in ['', ' ']:
                parts.append(f'"{literal}"')
        
        # Digits
        if r'\d+' in pattern:
            parts.append("one or more digits")
        elif r'\d' in pattern:
            parts.append("a digit")
        
        # Dots (literal)
        if r'\.' in pattern:
            parts.append("a dot")
        
        # Any character
        if '.*' in pattern:
            parts.append("any characters")
        
        # Character groups
        if '|' in pattern:
            parts.append("OR")
        
        explanation = " ".join(explanations + parts)
        
        if ends_with_dollar:
            explanation += " at the end"
        
        return explanation or "Complex pattern"


def interactive_regex_builder(
    examples: Optional[list[str]] = None,
    all_assets: Optional[list[Asset]] = None,
) -> Optional[str]:
    """Interactive workflow for building regex patterns.
    
    Args:
        examples: Optional list of example filenames
        all_assets: Optional list of all assets for testing
        
    Returns:
        Selected regex pattern or None if cancelled
    """
    console.print("\n[bold cyan]🔍 Interactive Regex Builder[/bold cyan]\n")
    
    # Get examples if not provided
    if not examples:
        console.print("Enter example filenames (comma-separated):")
        console.print("[dim]Example: IMG_001.jpg, IMG_002.jpg, DSC_1234.jpg[/dim]")
        examples_input = console.input("> ").strip()
        
        if not examples_input:
            console.print("[yellow]No examples provided. Cancelled.[/yellow]")
            return None
        
        examples = [e.strip() for e in examples_input.split(',') if e.strip()]
    
    if len(examples) < 2:
        console.print("[yellow]Please provide at least 2 examples.[/yellow]")
        return None
    
    # Analyze patterns
    helper = RegexHelper(examples)
    suggestions = helper.analyze_patterns()
    
    if not suggestions:
        console.print("[yellow]Could not detect any patterns. Try different examples.[/yellow]")
        return None
    
    # Display suggestions
    console.print(f"\n[bold]Analyzed {len(examples)} example(s)[/bold]\n")
    
    table = Table(title="📋 Suggested Patterns")
    table.add_column("#", style="cyan", width=3)
    table.add_column("Pattern", style="yellow")
    table.add_column("Description", style="green")
    
    if all_assets:
        table.add_column("Matches", style="magenta", justify="right")
    
    for idx, suggestion in enumerate(suggestions, 1):
        if all_assets:
            matching, _ = helper.test_pattern(suggestion.pattern, all_assets)
            match_count = len(matching)
            table.add_row(
                str(idx),
                suggestion.pattern,
                suggestion.description,
                str(match_count),
            )
        else:
            table.add_row(
                str(idx),
                suggestion.pattern,
                suggestion.description,
            )
    
    console.print(table)
    console.print()
    
    # Get user choice
    while True:
        console.print("Select pattern [1-{}] or enter your own regex (q to cancel):".format(len(suggestions)))
        choice = console.input("> ").strip()
        
        if choice.lower() == 'q':
            return None
        
        # Check if numeric choice
        if choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(suggestions):
                selected_pattern = suggestions[choice_num - 1].pattern
                break
        else:
            # Custom regex
            selected_pattern = choice
            break
    
    # Test and preview if assets available
    if all_assets:
        console.print(f"\n[bold]Testing pattern:[/bold] [yellow]{selected_pattern}[/yellow]\n")
        
        matching, sample_filenames = helper.test_pattern(selected_pattern, all_assets)
        
        console.print(f"[bold green]Found {len(matching)} matching files[/bold green]\n")
        
        if sample_filenames:
            console.print("[bold]Sample matches (first 10):[/bold]")
            for filename in sample_filenames:
                console.print(f"  ✓ {filename}")
            console.print()
        
        # Confirm
        if len(matching) > 0:
            confirm = console.input(f"Use this pattern? [y/N]: ").strip().lower()
            if confirm != 'y':
                return None
    
    return selected_pattern

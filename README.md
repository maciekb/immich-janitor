# Immich Janitor

CLI tool for managing your Immich library via the official Immich API.

## Features

### 📋 Asset Management
- List assets from your Immich library
- Delete assets matching regex patterns
- **🎯 Interactive Regex Builder** - Build patterns from example filenames (no regex knowledge required!)
- Filter and search through your media collection
- Pagination support for large libraries (auto-fetches all assets)

### 📊 Statistics & Analytics
- **Library Overview** - total assets, size, types breakdown
- **By File Type** - detailed breakdown of extensions and sizes  
- **By Date** - timeline view grouped by year/month/day

### 🔍 Duplicate Detection
- Find duplicate asset groups
- Smart deletion with keep strategies (oldest/newest/largest)
- Space savings calculation

### 🗑️ Trash Management
- List trashed assets
- Restore assets from trash (by pattern or all)
- Empty trash (permanently delete)
- Filter by deletion age
- Trash statistics

### 🛡️ Safety Features
- **Interactive pattern builder** with live preview and match counts
- Dry-run mode for all destructive operations
- Confirmation prompts (can be skipped with `--force`)
- Beautiful CLI interface with Rich tables
- Comprehensive error handling

## Installation

This project uses `uv` for Python package management. Make sure you have `uv` installed:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then, install the project:

```bash
# Clone the repository
git clone <your-repo-url>
cd immich-janitor

# Install dependencies
uv sync

# Install the CLI tool in development mode
uv pip install -e .
```

## Configuration

You need to provide your Immich API URL and API key. You can do this in two ways:

### Option 1: Environment Variables

```bash
export IMMICH_API_URL="http://your-immich-server:2283/api"
export IMMICH_API_KEY="your-api-key-here"
```

### Option 2: `.env` File

Create a `.env` file in your project directory:

```env
IMMICH_API_URL=http://your-immich-server:2283/api
IMMICH_API_KEY=your-api-key-here
```

### Getting Your API Key

1. Log in to your Immich web interface
2. Go to **Account Settings** (click your profile icon)
3. Navigate to **API Keys** section
4. Click **New API Key**
5. Give it a name and copy the generated key

> **Note**: The `.env` file is automatically loaded when you run the CLI, so you don't need to export variables manually if the file exists in your project directory.

## Usage

### List Assets

List all assets (limited to 100 by default):

```bash
immich-janitor list-assets
```

List with custom limit:

```bash
immich-janitor list-assets --limit 500
```

Filter by filename pattern (regex):

```bash
immich-janitor list-assets --pattern "IMG_.*\.jpg"
```

### Delete Assets by Pattern

Delete assets matching a regex pattern:

```bash
immich-janitor delete-by-pattern "IMG_[0-9]{4}\.jpg"
```

#### 🎯 Interactive Regex Builder (New!)

Don't know regex? No problem! Use the interactive mode to build patterns from example filenames:

**Interactive Mode** - Step-by-step pattern builder:
```bash
immich-janitor delete-by-pattern --interactive
```

The tool will:
1. Ask you for example filenames
2. Analyze patterns and suggest 3-5 regex options
3. Show how many files each pattern would match
4. Let you preview matches before deletion
5. Confirm before any deletions

**Quick Mode** - Provide examples directly:
```bash
immich-janitor delete-by-pattern --examples "IMG_001.jpg,IMG_002.jpg,DSC_1234.jpg"
```

**Example Session:**
```
🔍 Interactive Regex Builder

Analyzed 3 example(s)

                 📋 Suggested Patterns                              
┏━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ # ┃ Pattern         ┃ Description                   ┃ Matches ┃
┡━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ 1 │ ^IMG_\d+\.jpg$  │ Files starting with "IMG_",   │   1,234 │
│   │                 │ followed by numbers, ending   │         │
│   │                 │ with ".jpg"                   │         │
│ 2 │ ^(IMG|DSC)_\d+  │ Files starting with IMG or    │   2,456 │
│   │ \.jpg$          │ DSC, then numbers and ".jpg"  │         │
│ 3 │ .*\.jpg$        │ All files ending with ".jpg"  │  12,345 │
└───┴─────────────────┴───────────────────────────────┴─────────┘

Select pattern [1-3] or enter your own regex (q to cancel):
> 1

Testing pattern: ^IMG_\d+\.jpg$
Found 1,234 matching files

Sample matches (first 10):
  ✓ IMG_001.jpg
  ✓ IMG_002.jpg
  ...

Use this pattern? [y/N]: y
```

Dry-run mode (preview what would be deleted):

```bash
immich-janitor delete-by-pattern "IMG_.*" --dry-run
```

Skip confirmation prompt:

```bash
immich-janitor delete-by-pattern "IMG_.*" --force
```

### Command Line Options

You can also pass API credentials directly:

```bash
immich-janitor --api-url "http://localhost:2283/api" \
               --api-key "your-key" \
               list-assets
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Structure

```
immich_janitor/
├── __init__.py       # Package initialization
├── cli.py            # CLI interface (Click)
├── client.py         # Immich API client
├── config.py         # Configuration management
└── models.py         # Data models (Pydantic)
```

## API Documentation

This tool uses the official Immich API. For more information about the API endpoints:

- **API Documentation**: https://api.immich.app/
- **Immich GitHub**: https://github.com/immich-app/immich

### Key Endpoints Used

- `POST /search/metadata` - Search and list all assets
- `DELETE /assets` - Bulk delete assets
- `GET /assets/{id}` - Get asset details

## Safety Features

- **Dry-run mode**: Preview deletions without actually deleting
- **Confirmation prompts**: Asks for confirmation before deleting (unless `--force` is used)
- **Regex validation**: Validates regex patterns before execution
- **Error handling**: Comprehensive error messages and graceful failure handling

## Roadmap

Future features to be added iteratively:

- [ ] More filtering options (by date, type, size, etc.)
- [ ] Asset metadata operations
- [ ] Batch operations with progress bars
- [ ] Export/backup functionality
- [ ] Album management
- [ ] Statistics and reporting
- [ ] Configuration file support
- [ ] Multiple regex patterns support

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this tool for your needs.

## Disclaimer

⚠️ **Use with caution!** This tool can permanently delete your photos and videos. Always use `--dry-run` first to preview what will be deleted.

Make sure you have backups of your important media before using delete operations.

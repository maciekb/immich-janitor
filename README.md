# Immich Janitor

CLI tool for managing your Immich library via the official Immich API.

## Features

- 📋 List assets from your Immich library
- 🗑️ Delete assets matching regex patterns
- 🔍 Filter and search through your media collection
- 🛡️ Dry-run mode for safe operations
- 🎨 Beautiful CLI interface with Rich

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

- `GET /assets` - List all assets
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

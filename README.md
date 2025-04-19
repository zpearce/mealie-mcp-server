# Mealie MCP Server

This project enables AI assistants to interact with your Mealie recipe database through MCP client such as Claude Desktop.

## Prerequisites

- Python 3.12+
- Running [Mealie](https://mealie.io/) instance with API key
- Package manager [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Usage with Claude Desktop

Add the server to your `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mealie-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/repo/src",
        "run",
        "server.py"
      ],
      "env": {
        "MEALIE_BASE_URL": "https://your-mealie-instance.com",
        "MEALIE_API_KEY": "your-mealie-api-key"
      }
    }
  }
}
```

## Development

1. Clone the repository and navigate to the project directory

2. Install dependencies using uv:
```bash
uv sync
```

3. Copy the provided template file:
```bash
cp .env.template .env
```

4. Edit the `.env` file with your Mealie instance details:
```bash
MEALIE_BASE_URL=https://your-mealie-instance.com
MEALIE_API_KEY=your-mealie-api-key
```

5. Run MCP inspector
```bash
uv run mcp dev src/server.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

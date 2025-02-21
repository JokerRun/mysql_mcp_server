![Tests](https://github.com/designcomputer/mysql_mcp_server/actions/workflows/test.yml/badge.svg)
# MySQL MCP Server

A Model Context Protocol (MCP) server that enables secure interaction with MySQL databases. This server allows AI assistants to list tables, read data, and execute SQL queries through a controlled interface, making database exploration and analysis safer and more structured.

## Features

- List available MySQL tables as resources
- Read table contents
- Execute SQL queries with proper error handling
- Secure database access through environment variables
- Comprehensive logging

## Installation

```bash
pip install mysql-mcp-server
```

## Configuration

Set the following environment variables:

```bash
MYSQL_HOST=localhost     # Database host
MYSQL_PORT=3306         # Optional: Database port (defaults to 3306 if not specified)
MYSQL_USER=root
MYSQL_PASSWORD=000000
MYSQL_DATABASE=ruoyi-vue-pro
```

## Usage

### With Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mysql": {
      "command": "uv",
      "args": [
        "--directory", 
        "path/to/mysql_mcp_server_root",
        "run",
        "mysql_mcp_server"
      ],
      "env": {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3306",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "000000",
        "MYSQL_DATABASE": "ruoyi-vue-pro"
      }
    }
  }
}
```

### With Cursor

#### with docker
```bash
docker build -t mysql-mcp-server . # build images

docker run -i --rm -e MYSQL_HOST=$MYSQL_HOST -e MYSQL_PORT=$MYSQL_PORT -e MYSQL_USER=$MYSQL_USER -e MYSQL_PASSWORD=$MYSQL_PASSWORD -e MYSQL_DATABASE=$MYSQL_DATABASE mysql-mcp-server
# MYSQL_HOST=host.docker.internal for docker container
```

#### with uv
> [!TIP]
> Cursor can't provide environmental variables to MCP Servers.
> https://forum.cursor.com/t/how-to-use-the-mcp-servers-the-sse-url/46177/6?u=jokerrun
> Super Thanks to DaleLJefferson

add files: mysql_mcp_server_for_cursor_by_uv.sh
```bash
# mysql_mcp_server_for_cursor.sh
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root 
export MYSQL_PASSWORD=000000
export MYSQL_DATABASE=ruoyi-vue-pro
uv run --directory $this_repo_root mysql_mcp_server
```
Cursor MCP Server:
```
sh $this_repo_root/mysql_mcp_server_for_cursor_by_uv.sh
```

### As a standalone server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m mysql_mcp_server
```

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/mysql_mcp_server.git
cd mysql_mcp_server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## Security Considerations

- Never commit environment variables or credentials
- Use a database user with minimal required permissions
- Consider implementing query whitelisting for production use
- Monitor and log all database operations

## Security Best Practices

This MCP server requires database access to function. For security:

1. **Create a dedicated MySQL user** with minimal permissions
2. **Never use root credentials** or administrative accounts
3. **Restrict database access** to only necessary operations
4. **Enable logging** for audit purposes
5. **Regular security reviews** of database access

See [MySQL Security Configuration Guide](https://github.com/designcomputer/mysql_mcp_server/blob/main/SECURITY.md) for detailed instructions on:
- Creating a restricted MySQL user
- Setting appropriate permissions
- Monitoring database access
- Security best practices

⚠️ IMPORTANT: Always follow the principle of least privilege when configuring database access.

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

# Test Change

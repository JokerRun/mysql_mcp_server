import asyncio
import logging
import os
from mysql.connector import connect, Error
from mcp.server import Server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    GetPromptRequest,
    GetPromptResult,
    Prompt, 
    PromptMessage, 
    PromptArgument
)
from pydantic import AnyUrl

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mysql_mcp_server")

def get_db_config():
    """Get database configuration from environment variables."""
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "database": os.getenv("MYSQL_DATABASE"),
        "charset": "utf8mb4",
        "collation": "utf8mb4_general_ci"
    }
    
    if not all([config["user"], config["password"], config["database"]]):
        logger.error("Missing required database configuration. Please check environment variables:")
        logger.error("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE are required")
        raise ValueError("Missing required database configuration")
    
    return config

# Initialize server
app = Server("mysql_mcp_server")

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List MySQL tables as resources."""
    config = get_db_config()
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                logger.info(f"Found tables: {tables}")
                
                resources = []
                for table in tables:
                    resources.append(
                        Resource(
                            uri=f"mysql://{table[0]}/data",
                            name=f"Table: {table[0]}",
                            mimeType="text/plain",
                            description=f"Data in table: {table[0]}"
                        )
                    )
                return resources
    except Error as e:
        logger.error(f"Failed to list resources: {str(e)}")
        return []

@app.read_resource()
async def read_resource(uri: AnyUrl) -> str:
    """Read table contents."""
    config = get_db_config()
    uri_str = str(uri)
    logger.info(f"Reading resource: {uri_str}")
    
    if not uri_str.startswith("mysql://"):
        raise ValueError(f"Invalid URI scheme: {uri_str}")
        
    parts = uri_str[8:].split('/')
    table = parts[0]
    
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return "\n".join([",".join(columns)] + result)
                
    except Error as e:
        logger.error(f"Database error reading resource {uri}: {str(e)}")
        raise RuntimeError(f"Database error: {str(e)}")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available MySQL tools."""
    logger.info("Listing tools...")
    return [
        Tool(
            name="execute_sql",
            description="Execute an SQL query on the MySQL server",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute SQL commands."""
    config = get_db_config()
    logger.info(f"Calling tool: {name} with arguments: {arguments}")
    
    if name == "execute_sql":
        query = arguments.get("query")
        if not query:
            raise ValueError("Query is required")
        
        try:
            with connect(**config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    
                    # Special handling for SHOW TABLES
                    if query.strip().upper().startswith("SHOW TABLES"):
                        tables = cursor.fetchall()
                        result = ["Tables_in_" + config["database"]]  # Header
                        result.extend([table[0] for table in tables])
                        return [TextContent(type="text", text="\n".join(result))]
                    
                    # Regular SELECT queries
                    elif query.strip().upper().startswith("SELECT"):
                        columns = [desc[0] for desc in cursor.description]
                        rows = cursor.fetchall()
                        result = [",".join(map(str, row)) for row in rows]
                        return [TextContent(type="text", text="\n".join([",".join(columns)] + result))]
                    
                    # Non-SELECT queries
                    else:
                        conn.commit()
                        return [TextContent(type="text", text=f"Query executed successfully. Rows affected: {cursor.rowcount}")]
                    
        except Error as e:
            logger.error(f"Error executing SQL '{query}': {e}")
            return [TextContent(type="text", text=f"Error executing query: {str(e)}")]
            
    elif name == "prompt_sql":
        description = arguments.get("description")
        if not description:
            raise ValueError("Description is required")
            
        table_name = arguments.get("table_name", "")
        
        try:
            with connect(**config) as conn:
                with conn.cursor() as cursor:
                    if table_name:
                        cursor.execute(f"DESCRIBE {table_name}")
                        columns = cursor.fetchall()
                        schema_info = f"Table {table_name} columns:\n"
                        schema_info += "\n".join([f"- {col[0]} ({col[1]})" for col in columns])
                    else:
                        cursor.execute("SHOW TABLES")
                        tables = cursor.fetchall()
                        schema_info = "Available tables:\n"
                        schema_info += "\n".join([f"- {table[0]}" for table in tables])
                        
                    return [TextContent(type="text", text=f"""Database Schema Information:
{schema_info}

Your request: {description}

Please use this information to construct your SQL query.""")]
        
        except Error as e:
            logger.error(f"Error in prompt_sql: {str(e)}")
            return [TextContent(type="text", text=f"Error getting schema information: {str(e)}")]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


@app.list_resource_templates()
async def list_resource_templates() -> list[Resource]:
    """List available resource templates."""
    logger.info("Listing resource templates...")
    return []  # 返回空列表，因为MySQL服务器不需要资源模板

@app.list_prompts()
async def handle_list_prompts() -> list[Prompt]:
    # Implementation
    return [
        Prompt(
            name="generate_sql",
            description="Generate an SQL query based on the user's request",
            arguments=[
                PromptArgument(name="description", description="The user's request")
            ]
        )
    ]

@app.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> GetPromptResult:
    # Implementation
    if name == "generate_sql":
        description = arguments.get("description")
        if not description:
            raise ValueError("Description is required")
        
        return GetPromptResult(
            name="generate_sql",
            arguments={
                "description": description
            },
            messages=[
                PromptMessage(role="user", content=description)
            ]   
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")

async def main():
    """Main entry point to run the MCP server."""
    from mcp.server.stdio import stdio_server
    
    logger.info("Starting MySQL MCP server...")
    config = get_db_config()
    logger.info(f"Database config: {config['host']}/{config['database']} as {config['user']}")
    
    async with stdio_server() as (read_stream, write_stream):
        try:
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
        except Exception as e:
            logger.error(f"Server error: {str(e)}", exc_info=True)
            raise

if __name__ == "__main__":
    asyncio.run(main())
# src/mcp/server.py - Standard MCP Server for ADK
import os
import sqlite3
import json
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Get API key from environment
MCP_API_KEY = os.getenv("MCP_API_KEY", "banking-dev-token-2026")

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "banking.db")

# Create MCP server
server = Server("banking-server")

# Lazy load RAG to avoid startup crashes
_product_rag = None


def get_product_rag():
    """Lazy load RAG only when needed"""
    global _product_rag
    if _product_rag is None:
        try:
            import sys

            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from rag.product_knowledge import ProductRAG

            _product_rag = ProductRAG()
            print("✅ RAG initialized successfully")
        except Exception as e:
            print(f"⚠️  RAG initialization failed: {e}")
            _product_rag = False  # Mark as failed
    return _product_rag if _product_rag is not False else None


def _connect_db():
    """Create database connection"""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def _require_auth(api_key: str):
    """Validate API key"""
    if not api_key or api_key != MCP_API_KEY:
        raise PermissionError("Unauthorized: Invalid API key")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_customer_info",
            description="Get customer information by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID number (e.g., 1, 2, 3)",
                    },
                    "api_key": {
                        "type": "string",
                        "description": "API key for authentication",
                    },
                },
                "required": ["customer_id", "api_key"],
            },
        ),
        types.Tool(
            name="get_last_transactions",
            description="Get the last N transactions for a customer",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID number",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of transactions to return (default 5)",
                        "default": 5,
                    },
                    "api_key": {"type": "string", "description": "API key"},
                },
                "required": ["customer_id", "api_key"],
            },
        ),
        types.Tool(
            name="get_account_balance",
            description="Get current account balance",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID number",
                    },
                    "api_key": {"type": "string", "description": "API key"},
                },
                "required": ["customer_id", "api_key"],
            },
        ),
        types.Tool(
            name="search_bank_products",
            description="Search for bank products using natural language query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query about bank products",
                    },
                    "api_key": {"type": "string", "description": "API key"},
                },
                "required": ["query", "api_key"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute tool calls"""
    try:
        api_key = arguments.get("api_key", "")
        _require_auth(api_key)

        if name == "get_customer_info":
            conn = _connect_db()
            cursor = conn.cursor()
            customer_id = int(arguments["customer_id"])

            cursor.execute(
                """
                SELECT customer_id, first_name, last_name, age, gender,
                       email, account_type, account_balance
                FROM customers
                WHERE customer_id = ?
            """,
                (customer_id,),
            )

            row = cursor.fetchone()
            conn.close()

            if not row:
                result = {
                    "status": "error",
                    "error": f"Customer {customer_id} not found",
                }
            else:
                result = {
                    "status": "success",
                    "customer": {
                        "id": row[0],
                        "name": f"{row[1]} {row[2]}",
                        "age": row[3],
                        "gender": row[4],
                        "email": row[5],
                        "account_type": row[6],
                        "balance": float(row[7]),
                    },
                }

        elif name == "get_last_transactions":
            conn = _connect_db()
            cursor = conn.cursor()
            customer_id = int(arguments["customer_id"])
            limit = int(arguments.get("limit", 5))

            cursor.execute(
                """
                SELECT transaction_id, transaction_date, transaction_type,
                       transaction_amount, account_balance_after
                FROM transactions
                WHERE customer_id = ?
                ORDER BY transaction_date DESC
                LIMIT ?
            """,
                (customer_id, limit),
            )

            rows = cursor.fetchall()
            conn.close()

            transactions = [
                {
                    "id": row[0],
                    "date": row[1],
                    "type": row[2],
                    "amount": float(row[3]),
                    "balance_after": float(row[4]),
                }
                for row in rows
            ]

            result = {
                "status": "success",
                "customer_id": customer_id,
                "transactions": transactions,
                "count": len(transactions),
            }

        elif name == "get_account_balance":
            conn = _connect_db()
            cursor = conn.cursor()
            customer_id = int(arguments["customer_id"])

            cursor.execute(
                """
                SELECT account_balance FROM customers WHERE customer_id = ?
            """,
                (customer_id,),
            )

            row = cursor.fetchone()
            conn.close()

            if not row:
                result = {
                    "status": "error",
                    "error": f"Customer {customer_id} not found",
                }
            else:
                result = {
                    "status": "success",
                    "customer_id": customer_id,
                    "balance": float(row[0]),
                }

        elif name == "search_bank_products":
            query = arguments["query"]

            # Lazy load RAG
            rag = get_product_rag()

            if rag is None:
                result = {
                    "status": "error",
                    "error": "Product search unavailable. Run: python src/rag/create_vector_db.py",
                }
            else:
                products = rag.search_products(query, n_results=3)
                result = {
                    "status": "success",
                    "query": query,
                    "products": [p["product"] for p in products],
                    "count": len(products),
                }

        else:
            result = {"status": "error", "error": f"Unknown tool: {name}"}

        return [types.TextContent(type="text", text=json.dumps(result, indent=2))]

    except PermissionError as e:
        return [
            types.TextContent(
                type="text", text=json.dumps({"status": "error", "error": str(e)})
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"status": "error", "error": f"Error: {str(e)}"}),
            )
        ]


async def main():
    """Run the server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

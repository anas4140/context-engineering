"""
Module 10: MCP Server
=====================
A minimal MCP (Model Context Protocol) server exposing two tools:
  - calculator: evaluates a Python math expression
  - word_count: counts words in a string

Run standalone to test:
    python code/module10/mcp_server.py

Or let the MCP client start it automatically as a subprocess.
"""

import asyncio
import math
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

app = Server("course-tools")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="calculator",
            description=(
                "Evaluates a Python math expression and returns the result. "
                "Supports: +, -, *, /, **, sqrt(), sin(), cos(), log(), abs(), etc."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A valid Python math expression, e.g. 'sqrt(144)' or '2 ** 10'",
                    }
                },
                "required": ["expression"],
            },
        ),
        types.Tool(
            name="word_count",
            description="Counts the number of words in a string.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to count words in.",
                    }
                },
                "required": ["text"],
            },
        ),
        types.Tool(
            name="unit_convert",
            description="Converts a value between common units (temperature, length, weight).",
            inputSchema={
                "type": "object",
                "properties": {
                    "value":     {"type": "number", "description": "The numeric value to convert."},
                    "from_unit": {"type": "string", "description": "Source unit, e.g. 'celsius', 'km', 'kg'."},
                    "to_unit":   {"type": "string", "description": "Target unit, e.g. 'fahrenheit', 'miles', 'lbs'."},
                },
                "required": ["value", "from_unit", "to_unit"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "calculator":
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        allowed["abs"] = abs
        try:
            result = eval(arguments["expression"], {"__builtins__": {}}, allowed)
            return [types.TextContent(type="text", text=f"Result: {result}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    if name == "word_count":
        count = len(arguments["text"].split())
        return [types.TextContent(type="text", text=f"Word count: {count}")]

    if name == "unit_convert":
        v    = arguments["value"]
        frm  = arguments["from_unit"].lower().strip()
        to   = arguments["to_unit"].lower().strip()

        conversions = {
            ("celsius",    "fahrenheit"): lambda x: x * 9/5 + 32,
            ("fahrenheit", "celsius"):    lambda x: (x - 32) * 5/9,
            ("km",         "miles"):      lambda x: x * 0.621371,
            ("miles",      "km"):         lambda x: x * 1.60934,
            ("kg",         "lbs"):        lambda x: x * 2.20462,
            ("lbs",        "kg"):         lambda x: x * 0.453592,
            ("meters",     "feet"):       lambda x: x * 3.28084,
            ("feet",       "meters"):     lambda x: x * 0.3048,
        }
        fn = conversions.get((frm, to))
        if fn:
            result = round(fn(v), 4)
            return [types.TextContent(type="text", text=f"{v} {frm} = {result} {to}")]
        return [types.TextContent(type="text", text=f"Unsupported conversion: {frm} → {to}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())

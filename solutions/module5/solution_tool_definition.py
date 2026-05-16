"""
SOLUTION: Module 2, Lesson 3 — Advanced Prompting Strategies
Module 5, Lesson 2 — Designing and Integrating Tools

Hands-on task: Write a complete JSON Schema tool definition for
    search_products(query: str, category: str = None, on_sale_only: bool = False)

Run:
    python solutions/module5/solution_tool_definition.py
"""

import json
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()
client  = Anthropic()
console = Console()


# ─────────────────────────────────────────────
#  ANSWER: Complete JSON Schema tool definition
# ─────────────────────────────────────────────
search_products_tool = {
    "name": "search_products",
    # A good description:
    #  - States exactly what the tool does (not just "searches products")
    #  - Helps Claude decide WHEN to use it
    "description": (
        "Searches the ACME product catalogue by keyword and returns matching "
        "products with name, price, and availability. Use this when the user "
        "asks about products, prices, or stock availability."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                # A good parameter description tells Claude:
                #  - What the value represents
                #  - What format to use
                "description": (
                    "Keyword to search for in product names and descriptions. "
                    "Use specific product terms, e.g. 'smart fridge', 'air purifier'."
                ),
            },
            "category": {
                "type": "string",
                # enum restricts the value to a fixed set of options.
                # Without this, Claude might guess "Electronics" instead of "electronics".
                "enum": ["electronics", "apparel", "home_goods"],
                "description": (
                    "Optional product category to filter results. "
                    "Only use if the user specifies a category."
                ),
            },
            "on_sale_only": {
                "type": "boolean",
                "description": (
                    "If true, return only products currently on sale. "
                    "Default: false. Only set to true if the user explicitly "
                    "asks for sale items or discounts."
                ),
            },
        },
        # Only query is required — category and on_sale_only are optional
        "required": ["query"],
    },
}

# ─────────────────────────────────────────────
#  COMMON MISTAKES (for teaching purposes)
# ─────────────────────────────────────────────
# BAD: Missing descriptions — Claude can't tell what the parameters mean
bad_tool_no_descriptions = {
    "name": "search_products",
    "description": "Search products",   # Too vague — Claude doesn't know when to use it
    "input_schema": {
        "type": "object",
        "properties": {
            "query":        {"type": "string"},      # No description
            "category":     {"type": "string"},      # No enum — Claude might guess wrong values
            "on_sale_only": {"type": "boolean"},     # No description
        },
        "required": ["query"],
    },
}

# BAD: Wrong required fields — forces Claude to always pass category even when unknown
bad_tool_wrong_required = {
    "name": "search_products",
    "description": "Search the product catalogue.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query":        {"type": "string", "description": "Search keyword"},
            "category":     {"type": "string", "description": "Product category"},
            "on_sale_only": {"type": "boolean", "description": "Filter to sale items"},
        },
        # BUG: category should NOT be required — it's optional
        "required": ["query", "category"],
    },
}


def demo_tool_call(query: str, include_context: str = "") -> None:
    """
    Tests the tool definition by sending a query to Claude and
    showing which arguments it decides to use.
    """
    messages = [{"role": "user", "content": f"{include_context}{query}"}]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        tools=[search_products_tool],
        messages=messages,
    )

    console.print(f"\n[bold yellow]Query:[/bold yellow] {query}")

    if response.stop_reason == "tool_use":
        for block in response.content:
            if block.type == "tool_use":
                console.print(f"  [cyan]Tool called:[/cyan] {block.name}")
                console.print(f"  [cyan]Arguments:[/cyan]  {json.dumps(block.input, indent=4)}")
    else:
        console.print(f"  [dim]No tool call — Claude answered directly:[/dim]")
        for block in response.content:
            if hasattr(block, "text"):
                console.print(f"  {block.text}")


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 5, Lesson 2 — Tool Definition[/bold]\n")

    # ── Print the correct solution ───────────
    console.print("[bold cyan]Correct tool definition:[/bold cyan]")
    console.print(Panel(
        json.dumps(search_products_tool, indent=2),
        title="search_products — JSON Schema"
    ))

    # ── Test with various queries ─────────────
    console.print("\n[bold cyan]Live tests — watch how Claude fills in arguments:[/bold cyan]")

    demo_tool_call("Do you have any smart fridges?")
    demo_tool_call("Show me electronics on sale")
    demo_tool_call("What air purifiers are available in home goods?")
    demo_tool_call("Find me a SmartFridge, but only if it's discounted")

    console.print("\n[bold green]✓ Solution complete![/bold green]\n")

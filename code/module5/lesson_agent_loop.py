"""
Module 5: Agentic ReAct Loop with Function Calling
====================================================
This implements a complete working AI agent that can:
  - Reason about which tool to use (ReAct pattern)
  - Execute real Python functions as tools
  - Loop until the task is complete

Tools available to the agent:
  - calculator(expression)  — evaluates maths
  - get_weather(city)       — simulates a weather API
  - search_products(query)  — simulates a product search

Run:
    python code/module5/lesson_agent_loop.py
"""

import os
import json
import math
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv()
client  = Anthropic()
console = Console()

MODEL     = "claude-haiku-4-5-20251001"
MAX_TURNS = 10   # Safety limit — prevents infinite loops


# ─────────────────────────────────────────────
#  TOOL DEFINITIONS
#  These are the JSON Schema descriptions we
#  send to Claude so it knows what tools exist
#  and what arguments each one takes.
# ─────────────────────────────────────────────
TOOLS = [
    {
        "name":        "calculator",
        "description": (
            "Evaluates a mathematical expression and returns the numeric result. "
            "Use this for any arithmetic, algebra, or maths calculation. "
            "Supports: +, -, *, /, **, sqrt(), sin(), cos(), log(), etc."
        ),
        "input_schema": {
            "type":       "object",
            "properties": {
                "expression": {
                    "type":        "string",
                    "description": "A valid Python math expression, e.g. '2 ** 10' or 'sqrt(144)'",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name":        "get_weather",
        "description": (
            "Returns the current weather conditions for a given city. "
            "Use this when the user asks about weather, temperature, or climate in a location."
        ),
        "input_schema": {
            "type":       "object",
            "properties": {
                "city": {
                    "type":        "string",
                    "description": "City name, e.g. 'London' or 'New York'",
                },
                "unit": {
                    "type":        "string",
                    "enum":        ["celsius", "fahrenheit"],
                    "description": "Temperature unit. Default: celsius",
                },
            },
            "required": ["city"],
        },
    },
    {
        "name":        "search_products",
        "description": (
            "Searches the ACME product catalogue by keyword. "
            "Returns matching products with name, price, and availability."
        ),
        "input_schema": {
            "type":       "object",
            "properties": {
                "query": {
                    "type":        "string",
                    "description": "Search keyword, e.g. 'smart fridge' or 'air purifier'",
                },
                "on_sale_only": {
                    "type":        "boolean",
                    "description": "If true, only return products currently on sale. Default: false",
                },
            },
            "required": ["query"],
        },
    },
]


# ─────────────────────────────────────────────
#  TOOL IMPLEMENTATIONS
#  These are the actual Python functions that
#  run when Claude decides to call a tool.
# ─────────────────────────────────────────────
def calculator(expression: str) -> str:
    """
    Safely evaluates a mathematical expression.
    We expose math functions (sqrt, sin, etc.) but block dangerous operations.
    """
    # Allow only safe names from the math module
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    allowed_names["abs"] = abs

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Error evaluating '{expression}': {e}"


def get_weather(city: str, unit: str = "celsius") -> str:
    """
    Simulates a weather API response.
    In a real app this would call OpenWeatherMap or similar.
    """
    # Fake weather data for demo purposes
    weather_db = {
        "london":   {"temp_c": 12, "condition": "Cloudy", "humidity": 78},
        "new york": {"temp_c": 18, "condition": "Sunny",  "humidity": 55},
        "tokyo":    {"temp_c": 22, "condition": "Clear",  "humidity": 60},
        "dubai":    {"temp_c": 38, "condition": "Sunny",  "humidity": 40},
        "sydney":   {"temp_c": 20, "condition": "Partly cloudy", "humidity": 65},
    }

    key  = city.lower()
    data = weather_db.get(key, {"temp_c": 20, "condition": "Unknown", "humidity": 50})

    temp = data["temp_c"]
    if unit == "fahrenheit":
        temp = round(temp * 9 / 5 + 32, 1)
        unit_str = "°F"
    else:
        unit_str = "°C"

    return (
        f"Weather in {city.title()}: {data['condition']}, "
        f"{temp}{unit_str}, Humidity: {data['humidity']}%"
    )


def search_products(query: str, on_sale_only: bool = False) -> str:
    """
    Simulates a product catalogue search.
    In a real app this would query a database or Elasticsearch.
    """
    product_db = [
        {"name": "SmartFridge Series A", "price": 1299, "on_sale": False, "available": True},
        {"name": "SmartFridge Series B", "price": 999,  "on_sale": True,  "available": True},
        {"name": "AirPure 3000",          "price": 349,  "on_sale": False, "available": True},
        {"name": "AirPure Mini",          "price": 149,  "on_sale": True,  "available": False},
        {"name": "SmartOven Pro",         "price": 799,  "on_sale": False, "available": True},
    ]

    # Simple keyword search
    results = [
        p for p in product_db
        if query.lower() in p["name"].lower()
        and (not on_sale_only or p["on_sale"])
    ]

    if not results:
        return f"No products found matching '{query}'."

    lines = []
    for p in results:
        sale_tag  = " [ON SALE]"   if p["on_sale"]    else ""
        avail_tag = " — Out of stock" if not p["available"] else ""
        lines.append(f"• {p['name']}: ${p['price']}{sale_tag}{avail_tag}")

    return "\n".join(lines)


# ─────────────────────────────────────────────
#  TOOL DISPATCHER
#  Maps tool names to their Python functions.
#  When Claude calls a tool, we look up the
#  function here and execute it.
# ─────────────────────────────────────────────
TOOL_FUNCTIONS = {
    "calculator":      calculator,
    "get_weather":     get_weather,
    "search_products": search_products,
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Looks up a tool function by name and calls it with the given arguments.
    Returns the result as a string.
    """
    fn = TOOL_FUNCTIONS.get(tool_name)
    if fn is None:
        return f"Error: unknown tool '{tool_name}'"
    try:
        return fn(**tool_input)
    except Exception as e:
        return f"Error executing {tool_name}: {e}"


# ─────────────────────────────────────────────
#  THE AGENT LOOP (ReAct pattern)
#  Reason → Act → Observe → Repeat
#
#  Turn 1: User query + tools → Claude decides to call a tool
#  Turn 2: Tool result → Claude synthesises final answer
#  (May loop multiple times for complex tasks)
# ─────────────────────────────────────────────
def run_agent(user_query: str) -> str:
    """
    Runs the complete agent loop for a user query.
    Loops until Claude returns a final text answer or MAX_TURNS is reached.

    Returns:
        The agent's final text response
    """
    # The conversation history — grows with each turn
    messages = [{"role": "user", "content": user_query}]
    turn     = 0

    console.print(f"\n[bold yellow]User:[/bold yellow] {user_query}")

    while turn < MAX_TURNS:
        turn += 1
        console.print(f"\n[dim]--- Agent turn {turn} ---[/dim]")

        # ── Call Claude with tool definitions ──
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        # ── Check why Claude stopped ────────────
        # stop_reason == "tool_use" → Claude wants to call a tool
        # stop_reason == "end_turn" → Claude has a final answer
        if response.stop_reason == "end_turn":
            # Extract the final text from the response
            for block in response.content:
                if hasattr(block, "text"):
                    console.print(f"\n[bold green]Agent:[/bold green] {block.text}")
                    return block.text
            return "No text response found."

        if response.stop_reason == "tool_use":
            # Add Claude's response (which contains the tool_use block) to history
            messages.append({"role": "assistant", "content": response.content})

            # Process each tool call in the response
            # (Claude can request multiple tools in one turn)
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_name  = block.name
                    tool_input = block.input

                    console.print(
                        f"  [cyan]Tool call:[/cyan] {tool_name}("
                        f"{json.dumps(tool_input, ensure_ascii=False)})"
                    )

                    # Execute the actual Python function
                    result = execute_tool(tool_name, tool_input)
                    console.print(f"  [dim]Result: {result}[/dim]")

                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result,
                    })

            # Add all tool results back to the conversation
            # Claude will read these in the next turn to formulate its answer
            messages.append({"role": "user", "content": tool_results})

        else:
            # Unexpected stop reason
            console.print(f"[red]Unexpected stop_reason: {response.stop_reason}[/red]")
            break

    return "Max turns reached without a final answer."


if __name__ == "__main__":
    console.print("\n[bold]Module 5: AI Agent with Function Calling[/bold]\n")

    # Test queries that require different tools
    test_queries = [
        "What is the square root of 1764?",
        "What's the weather like in Tokyo today?",
        "Are there any SmartFridge models on sale right now?",
        "If a fridge costs $1299 and there's a 15% discount, what's the final price?",
    ]

    for query in test_queries:
        console.print(Rule())
        run_agent(query)

    console.print(f"\n[bold green]✓ Module 5 agent demo complete![/bold green]")
    console.print("Next: [italic]python code/module6/lesson1_evaluation.py[/italic]\n")

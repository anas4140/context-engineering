# **Module 10, Lesson 2: Building an MCP Server**

This lesson walks through building a Python MCP server with the official `mcp` library, then connecting a Claude-powered client to it.

---

## Learning Objectives

- **Build** a minimal MCP server exposing two tools
- **Connect** a Claude agent to the server via stdio transport
- **Call** MCP tools from Claude and return results

---

## 1. Server Structure

An MCP server is a Python script that:
1. Declares tools with `@server.call_tool()` and `@server.list_tools()`
2. Runs an event loop over stdio (or SSE for network transport)

```python
# mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import asyncio

app = Server("course-tools")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="calculator",
            description="Evaluates a Python math expression",
            inputSchema={
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
            },
        ),
        types.Tool(
            name="word_count",
            description="Counts words in a string",
            inputSchema={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        ),
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "calculator":
        import math
        allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
        try:
            result = eval(arguments["expression"], {"__builtins__": {}}, allowed)
            return [types.TextContent(type="text", text=f"Result: {result}")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {e}")]

    if name == "word_count":
        count = len(arguments["text"].split())
        return [types.TextContent(type="text", text=f"Word count: {count}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

Run the server standalone:
```bash
python code/module10/mcp_server.py
```

---

## 2. Client: Connecting to the Server

```python
# lesson1_mcp_client.py (simplified)
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["code/module10/mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools
            tools_result = await session.list_tools()
            print("Available tools:", [t.name for t in tools_result.tools])

            # Call a tool
            result = await session.call_tool("calculator", {"expression": "sqrt(144)"})
            print(result.content[0].text)   # "Result: 12.0"

asyncio.run(main())
```

---

## 3. Connecting MCP to Claude

The bridge: convert MCP tool schemas to Claude's format, then execute MCP tool calls when Claude requests them.

```python
def mcp_to_claude_tool(mcp_tool) -> dict:
    return {
        "name":         mcp_tool.name,
        "description":  mcp_tool.description,
        "input_schema": mcp_tool.inputSchema,
    }

async def run_agent_with_mcp(user_query: str, session: ClientSession):
    # 1. Fetch tools from server
    mcp_tools  = await session.list_tools()
    claude_tools = [mcp_to_claude_tool(t) for t in mcp_tools.tools]

    # 2. Send to Claude
    messages = [{"role": "user", "content": user_query}]
    response = client.messages.create(
        model=MODEL_FAST, max_tokens=512,
        tools=claude_tools, messages=messages,
    )

    # 3. Execute tool calls via MCP
    if response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                mcp_result = await session.call_tool(block.name, block.input)
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     mcp_result.content[0].text,
                })
        messages.append({"role": "user", "content": tool_results})

        # 4. Get final answer
        final = client.messages.create(
            model=MODEL_FAST, max_tokens=512,
            tools=claude_tools, messages=messages,
        )
        return final.content[0].text
```

---

## Key Takeaways

- An MCP server is a Python script with `@app.list_tools()` and `@app.call_tool()` handlers
- The client connects via stdio (local) or SSE (networked)
- Converting MCP → Claude tool format is a single-function transformation
- Tool execution flows: Claude requests → your app calls MCP server → result injected back

---

*Up next: Final Project refinements using all 10 modules*

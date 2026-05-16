# **Module 10, Lesson 1: Introduction to Model Context Protocol**

Model Context Protocol (MCP) is an open standard that lets AI models discover and call tools provided by external servers — without hardcoding tool definitions into your application. Think of it as a "USB standard for AI tools."

---

## Learning Objectives

- **Explain** what MCP is and why it exists
- **Compare** MCP tools to hand-rolled Claude tool definitions
- **Identify** when MCP is the right choice vs. inline tool definitions

---

## 1. The Problem MCP Solves

In Modules 5-7 you defined tools as Python dicts and implemented them as functions in the same file:

```python
TOOLS = [{"name": "calculator", "description": "...", "input_schema": {...}}]

def calculator(expression: str) -> str:
    return str(eval(expression))
```

This works for small projects. It breaks down when:

- The same tool needs to be shared across 10 different agents
- Tools live in different services (database, file system, external API)
- Non-developers need to add tools without touching Python code
- You want to use tools from a vendor without reading their implementation

**MCP separates the tool definition and implementation (the server) from the AI application that uses it (the client).**

---

## 2. MCP Architecture

```
┌──────────────────────┐     JSON-RPC over stdio/SSE     ┌─────────────────────┐
│   MCP Client         │ ◄──────────────────────────────► │   MCP Server        │
│  (your AI app)       │                                   │  (tool provider)    │
│                      │   list_tools() →                  │                     │
│  Claude              │   ← [{name, description,         │  calculator()        │
│  + tool definitions  │      input_schema}]               │  file_read()         │
│  from MCP            │                                   │  db_query()          │
└──────────────────────┘   call_tool(name, args) →        └─────────────────────┘
                           ← result
```

---

## 3. MCP vs. Inline Tool Definitions

| | Inline tools | MCP tools |
|--|--|--|
| Definition lives | Same Python file | Separate MCP server process |
| Reusability | Copy-paste across projects | One server, many clients |
| Discovery | Static, hardcoded | Dynamic: client calls `list_tools()` |
| Vendor support | Write yourself | Vendors ship pre-built MCP servers |
| Complexity | Simple | Adds a network/process boundary |
| Best for | Prototypes, single-agent apps | Production, multi-agent, shared tools |

---

## 4. The MCP Ecosystem

MCP servers exist for many common tools:
- **File system** — read/write local files
- **Web search** — Brave Search, Tavily
- **Databases** — PostgreSQL, SQLite
- **GitHub** — repos, PRs, issues
- **Slack, Google Drive, Notion** — productivity tools

You can also write your own in Python using the `mcp` library (Lesson 2).

---

## 5. How Claude Sees MCP Tools

From Claude's perspective, MCP tools are identical to inline tools — they arrive as JSON schemas in the `tools` parameter. The MCP client library handles discovery and schema conversion automatically:

```python
# Your app fetches tool schemas from the MCP server at startup
mcp_tools = await session.list_tools()

# Convert to Claude format and send normally
claude_tools = [convert_to_claude_format(t) for t in mcp_tools.tools]
response = client.messages.create(model=..., tools=claude_tools, messages=...)
```

---

## Key Takeaways

- MCP decouples tool implementation (server) from AI application (client)
- The client discovers tools dynamically via `list_tools()` — no hardcoding
- From Claude's perspective, MCP tools are identical to inline tool dicts
- Use inline tools for quick prototypes; switch to MCP for shared/production tooling

---

*Next: [Lesson 2 — Building an MCP Server](Lesson2_MCP_Server.md)*

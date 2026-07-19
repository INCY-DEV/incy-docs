# Docs for AI (MCP / llms.txt)

You can connect the INCY documentation to AI assistants (Claude Code, Codex, Cursor, etc.) so they automatically pull the current subscription formats, headers, deep links, and Premium API — and write your integration faster and more correctly, with no manual copy-paste.

There are two ways: an **MCP server** (a tool for the AI) and **llms.txt** (a machine-readable index).

## Option 1. MCP via GitMCP (recommended)

[GitMCP](https://gitmcp.io) is a free, public MCP server that reads documentation straight from our GitHub repository. Nothing to install — just add the URL.

**Server URL:**

```
https://gitmcp.io/INCY-DEV/incy-docs
```

### Claude Code

```bash
claude mcp add --transport http incy-docs https://gitmcp.io/INCY-DEV/incy-docs
```

### Cursor / Codex / other clients

Add the server to the client's MCP config:

```json
{
  "mcpServers": {
    "incy-docs": {
      "url": "https://gitmcp.io/INCY-DEV/incy-docs"
    }
  }
}
```

Once connected, the AI gets tools to search and read the INCY docs. For example, given "build an integration: hide the subscription URL and add a banner", the assistant will find the `hide-url` and `banner-text` headers in the docs and apply them correctly.

## Option 2. llms.txt

For tools that support the [llms.txt](https://llmstxt.org) standard, we publish two files:

| File | Contents |
| --- | --- |
| [`llms.txt`](https://docs.incy.cc/llms.txt) | Index: every documentation section with links and a short description |
| [`llms-full.txt`](https://docs.incy.cc/llms-full.txt) | The entire documentation in one file (full text) |

Just give the assistant the `https://docs.incy.cc/llms-full.txt` link and it gets the whole documentation at once.

## What you can ask the AI

- "Which subscription HTTP headers does INCY support, and what does each one do?"
- "Show the deep-link format for importing a subscription"
- "How do I configure fragmentation and domain fronting via the Premium API?"
- "Build an example full Xray config with routing for INCY"

The documentation is bilingual (RU by default, EN as suffixed copies), and llms.txt / GitMCP update automatically whenever the documentation changes.

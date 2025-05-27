
## [pattern] Server-side agents
**Problem**: Current MCP servers expose dozens of tools. Host LLMs get overwhelmed trying 
to master every API, leading to frequent failures and expensive retry cycles.

**Solution**: Put an expert agent inside each MCP server. The host LLM talks to the
agent in natural language instead of wrestling with raw APIs.

**Example**:
- Host LLM: "Get recent issues on `jlowin/fastmcp`"
- GitHub agent: Uses correct API internally, samples back if needed: "Found 150 issues. Want all or just the top 10?"
- Host LLM: "Just 10"

**Key benefit**: Host LLMs maintain a simple "rolodex" of expert agents instead of
memorizing hundreds of tool syntaxes.

**Technical note**: Uses MCP's sampling capability for clarification loops between
server agent and host LLM.

[Discussion that sparked idea](https://github.com/jlowin/fastmcp/discussions/591)

## [problem] Auth

- Make auth super simple. Every server that wants to protect resources needs to implement
auth in a spec compliant way. It's hairy.

## [pattern] Dynamic Tools [fastmcp-issue](https://github.com/jlowin/fastmcp/issues/572)

**The Core Problem**: 
Right now, everyone who connects to a FastMCP server sees the exact same tools. But users want different people
to see different tools from the same server.

**Explaining the GH issue**:
@guidodecaso's Example:
- Company has one server that connects to many different business systems
- When Person A connects, they see tools for "Customer Database" and "Email System"
- When Person B connects, they see tools for "Analytics Dashboard" and "Admin Panel"
- Same server, but it figures out who you are and shows you only your relevant tools
- @orhanrauf Adds Validation:
"We have exactly this use case too!"
Also wants to intercept and add logic before tools run

**The Technical Challenge**:
- Server needs to identify the user (through some kind of credentials)
- Server needs to fetch the right tools for that specific user (from databases, other systems, etc.)
- Server needs to route tool calls to the right backend systems


## [problem] Portable AI context

**The friction**: Every AI conversation starts from scratch. You lose valuable insights, have to re-explain preferences, and get locked into specific providers because switching means losing all your accumulated context.

**Examples of lost context**:
- Health routines and how to adapt workouts based on wearable data
- Code project patterns that work across different AI coding tools
- Fashion/relationship advice that took multiple conversations to refine
- Any principle or template you've developed through AI interaction

**Current workaround**: Copy-paste artifacts to Notion, but it's manual and hard to apply to new conversations.

**Potential solution**: Personal context bank as MCP server
- Dynamic context: Oura data, calendar, current projects (real-time)
- Persistent knowledge: Principles, templates, conversation artifacts you want to reuse
- Tools like `recall_insights(topic)`, `store_principle()`, `get_template()`

**Open questions**: 
- What's the right form factor for maintaining this context bank?
- How do you make it easy to use without becoming another system to manage?
- What's the minimum version I'd use?

**Goal**: Make your accumulated AI wisdom portable across providers and persistent across time.
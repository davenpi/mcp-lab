
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

## [pain] Auth

- Make auth super simple. Every server that wants to protect resources needs to implement
auth in a spec compliant way. It's hairy.

## [pattern] Dynamic Tool Surface [fastmcp-issue](https://github.com/jlowin/fastmcp/issues/572)

**The Core Problem**: 
Right now, everyone who connects to a FastMCP server sees the exact same tools. But users want different people to see different tools from the same server.

**The Use Case Evolution**:
@guidodecaso's Example:
- Company has one server that connects to many different business systems
- When Person A connects, they see tools for "Customer Database" and "Email System"
- When Person B connects, they see tools for "Analytics Dashboard" and "Admin Panel"
- Same server, but it figures out who you are and shows you only your relevant tools

**The Technical Challenge**:
- Server needs to identify the user (through some kind of credentials)
- Server needs to fetch the right tools for that specific user (from databases, other systems, etc.)
- Server needs to route tool calls to the right backend systems
- @orhanrauf Adds Validation:
"We have exactly this use case too!"
Also wants to intercept and add logic before tools run

**Why This Matters**:
This is moving from "one-size-fits-all servers" to "personalized, contextual tool serving." Think of it like:
> Old way: Everyone sees the same restaurant menu

> New way: Menu changes based on who you are, your dietary restrictions, what's available today

**The Big Picture**:
This suggests MCP servers are evolving from simple tool hosts to intelligent routing platforms that dynamically serve contextual capabilities based on user identity and available backend systems.
It's really about personalization and dynamic capability serving.


## [vision] The JARVIS Architecture: AI Agents + Dynamic Tool Serving

**The Core Vision**: 
Move from "chatbots with hardcoded tools" to "intelligent assistants that dynamically discover and serve contextual capabilities" - essentially building JARVIS from Iron Man.

**The JARVIS Pattern**:
- **Context-aware tool serving**: Different tools appear based on who you are, where you are, what you're doing
- **Seamless capability discovery**: "JARVIS, help me with the suit" → gets suit diagnostic tools automatically  
- **Removes cognitive overhead**: User focuses on intent, system figures out the right tools
- **Adaptive intelligence**: Same server, completely different experience per user/context

**Business Opportunities Unlocked**:
1. **AI-Native Enterprise Integration**: One server that gives every employee personalized tool access
2. **Multi-tenant AI Tooling Platforms**: "Shopify for AI Tools" - plug in your systems, get instant AI integration
3. **Smart Proxy/Gateway Services**: Replace API management with semantic tool serving
4. **Personalized AI Infrastructure-as-a-Service**: "ChatGPT for Your Company's Tools"

**Beyond Current Tech**:
- **Emergent tool discovery**: AI agents combine tools in ways humans never imagined
- **Collective intelligence networks**: Assistants learn from other users while protecting privacy
- **Adaptive reality systems**: Physical and digital environments reshape based on context
- **Reality-code fusion**: Voice commands control software, robots, and connected devices seamlessly

**Strategic Insight**: 
While everyone builds the "brain" of AI agents (LLMs, reasoning), there's huge opportunity in building the "nervous system" - how agents sense and interact with the world. MCP expertise + agent familiarity = rare and valuable skillset.

**The Ultimate Goal**: 
Computing that's invisible, contextual, and infinitely capable. You think about what you want to accomplish, and the right combination of digital and physical tools appears automatically.
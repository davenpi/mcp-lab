# Python SDK Improvement Guide (pymcp)

Guidelines for making the MCP Python SDK pristine and user-friendly.

## Documentation Style - "Narrative Documentation"

### Philosophy
Follow Stripe's approach: treat documentation like user stories. Focus on what developers want to accomplish, not just technical specifications.

### Principles
- **Action-oriented headings**: "Send your first request" not "Request objects"
- **Practical examples first**, theory second
- **Progressive disclosure**: Start simple, add complexity gradually
- **Copy-pasteable code** that actually works out of the box

### Docstring Style

**For classes** - Explain purpose and show basic usage:
```python
class ListToolsRequest(PaginatedRequest):
    """
    List all tools available on this MCP server.

    Use pagination for servers with many tools:
        request = ListToolsRequest(cursor="token_from_previous_response")
        
    Most servers return all tools in a single response.
    """
```

**For methods** - Focus on practical outcomes:
```python
def from_protocol(cls, data: dict[str, Any]) -> Self:
    """
    Convert raw JSON-RPC data into a typed Python object.
    
    Handles all the protocol complexity so you work with clean Python objects:
        data = {"method": "tools/list", "params": {...}}
        request = ListToolsRequest.from_protocol(data)
    """
```

## Code Organization

### File Structure
Break up the monolithic file into logical modules:

```
mcp/
├── types/
│   ├── __init__.py      # Export main types
│   ├── base.py          # Request, Result, Notification, Error
│   ├── initialization.py # Initialize flow
│   ├── tools.py         # Tool-related types
│   ├── resources.py     # Resource types
│   └── protocol.py      # JSON-RPC wrappers
└── __init__.py          # Clean public API
```

### Import Organization
```python
# Standard library
import traceback
from typing import Annotated, Any, Literal, TypeVar

# Third party
from pydantic import BaseModel, Field, field_validator

# Local
from .base import Request, Result
```

## Type Improvements

### Reduce Repetition
```python
# Define common unions once
AnyContent = TextContent | ImageContent | AudioContent | EmbeddedResource
ContentList = list[AnyContent]

# Then use throughout
class CallToolResult(Result):
    content: ContentList
```

### Better Generic Usage
```python
# Python 3.11+
from typing import Self

@classmethod
def from_protocol(cls, data: dict[str, Any]) -> Self:
    """More precise than type[RequestT] -> RequestT"""
```

## API Design Patterns

### Builder Pattern for Complex Objects
```python
class InitializeRequest:
    @classmethod
    def create(cls, client_name: str, version: str) -> "InitializeRequest":
        """Create a standard initialization request with sensible defaults."""
        return cls(
            client_info=Implementation(name=client_name, version=version),
            capabilities=ClientCapabilities()
        )
    
    @classmethod
    def create_with_tools(cls, client_name: str, version: str) -> "InitializeRequest":
        """Create an initialization request that supports tool calling."""
        return cls(
            client_info=Implementation(name=client_name, version=version),
            capabilities=ClientCapabilities(
                tools=ToolsCapability(list_changed=True)
            )
        )
```

### Validation Helpers
```python
def validate_uri_scheme(uri: str, allowed: list[str]) -> None:
    """Common URI validation logic for reuse across models."""
    scheme = str(uri).split("://")[0] if "://" in str(uri) else ""
    if scheme not in allowed:
        raise ValueError(
            f"URI scheme '{scheme}' not allowed. "
            f"Must be one of: {', '.join(allowed)}"
        )
```

### Actionable Error Messages
```python
# Instead of:
raise ValueError("priority must be between 0 and 1")

# Provide context and guidance:
raise ValueError(
    f"priority must be between 0 and 1, got {v}. "
    f"Use 0.0 for lowest priority, 1.0 for highest."
)
```

## Consistency Improvements

### Method Naming
Choose one pattern and stick to it:
```python
# Option 1: Protocol-specific
def to_protocol(self) -> dict[str, Any]:
def from_protocol(cls, data: dict) -> Self:

# Option 2: Generic
def to_dict(self) -> dict[str, Any]:
def from_dict(cls, data: dict) -> Self:
```

### Field Validation Pattern
Standardize validation approaches:
```python
@field_validator("field_name")
@classmethod
def validate_field_name(cls, v: ValueType | None) -> ValueType | None:
    """Consistent docstring format."""
    if v is not None and not meets_criteria(v):
        raise ValueError(f"descriptive error with got {v}")
    return v
```

## Python Conventions

### Model Attribute Documentation

**Recommended**: Multi-line with triple quotes
```python
class Tool(ProtocolModel):
    name: str
    description: str | None = None
    """
    Human-readable description of the tool.
    
    Clients can use this to improve LLM understanding of available tools.
    """
    
    input_schema: InputSchema = Field(alias="inputSchema")
    """JSON schema defining the tool's expected input parameters."""
```

**Why**: 
- More readable for complex descriptions
- Easier to add examples and formatting
- Consistent with class docstring style
- Better for IDE tooltip display

### Field Documentation Best Practices

1. **Start with purpose**: What is this field for?
2. **Add context**: How does it relate to the protocol?
3. **Include examples** for complex fields:

```python
uri_template: str = Field(alias="uriTemplate")
"""
URI template following RFC 6570 specification.

Example: "file:///logs/{date}.log" where {date} will be expanded
when requesting the actual resource.
"""
```

## Testing Structure

### Make Code Testable
- Separate validation logic from model definitions
- Make protocol conversion testable independently
- Provide test fixtures for common objects

```python
# tests/fixtures.py
def sample_tool() -> Tool:
    """Standard tool for testing."""
    return Tool(
        name="test_tool",
        description="A tool for testing",
        input_schema=InputSchema(
            properties={"param": {"type": "string"}},
            required=["param"]
        )
    )
```

## Progressive API Design

### Start Simple, Add Complexity
```python
# Basic usage should be trivial
request = ListToolsRequest()

# Advanced usage available when needed
request = ListToolsRequest(
    cursor="pagination_token",
    progress_token="track_progress"
)
```

### Sensible Defaults
Every optional field should have a default that works for 80% of use cases:

```python
class ClientCapabilities(ProtocolModel):
    """Default capabilities work for basic MCP usage."""
    
    experimental: dict[str, Any] | None = None
    roots: RootsCapability | None = None
    sampling: dict[str, Any] | None = None
```

---

## Key Principle: User Empathy

Every design choice should ask: "What would make this easier for a Python developer?" rather than "How do I perfectly mirror the spec?"

The goal is building something people actually want to use, not just something that implements a specification correctly.
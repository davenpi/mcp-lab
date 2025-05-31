# Protocol basics

Need to define how servers and clients talk. They send three kinds of messages.
All JSON RPC (remote procedure call) 2.0

**Request**

Note the ID. MCP requires this.
```typescript
{
  jsonrpc: "2.0";
  id: string | number;
  method: string;
  params?: {
    [key: string]: unknown;
  };
}
```
Also note we are omitting optional metadata here (progress tokens). Full types in the spec.

**Response**

Respond to request. Correlate with ID. Give a result OR an error, not both.
```typescript
{
  jsonrpc: "2.0";
  id: string | number;
  result?: {
    [key: string]: unknown;
  }
  error?: {
    code: number;
    message: string;
    data?: unknown;
  }
}
```

**Notification**

Don't respond to notifications. "Fire and forget". Progress, initialized, resource update, etc.

No IDs in notifications. 
```typescript
{
  jsonrpc: "2.0";
  method: string;
  params?: {
    [key: string]: unknown;
  };
}
```

Can batch requests and notifications, i.e., send a bunch in a group. Implementations
must be able to receive batches, don't need to send batches. Seems batches are
going away in the next spec
[draft](https://modelcontextprotocol.io/specification/draft/changelog).


### Note on Types in the Python SDK

It feels overcomplicated. Especially compared to the TypeScript schema. To just define a request we have:


```python

class RequestParams(BaseModel):
    class Meta(BaseModel):
        progressToken: ProgressToken | None = None
        """
        If specified, the caller requests out-of-band progress notifications for
        this request (as represented by notifications/progress). The value of this
        parameter is an opaque token that will be attached to any subsequent
        notifications. The receiver is not obligated to provide these notifications.
        """

        model_config = ConfigDict(extra="allow")

    meta: Meta | None = Field(alias="_meta", default=None)

RequestParamsT = TypeVar("RequestParamsT", bound=RequestParams | dict[str, Any] | None)
MethodT = TypeVar("MethodT", bound=str)

class Request(BaseModel, Generic[RequestParamsT, MethodT]):
    """Base class for JSON-RPC requests."""

    method: MethodT
    params: RequestParamsT
    model_config = ConfigDict(extra="allow")

RequestId = str | int

class JSONRPCRequest(Request[dict[str, Any] | None, str]):
    """A request that expects a response."""

    jsonrpc: Literal["2.0"]
    id: RequestId
    method: str
    params: dict[str, Any] | None = None
```

Using Pydantic makes sense. But here we've got to understand generic types and
type variables. We've then got to trace those classes around. Also why are we
redeclaring `method` and `params` in `JSONRPCRequest`? I thought declaring the
`Request` class with these specific types will take care of the job.


Compare this to the schema where we have

```typescript

export type ProgressToken = string | number;

export interface Request {
  method: string;
  params?: {
    _meta?: {
      progressToken?: ProgressToken;
    };
    [key: string]: unknown;
  };
}

export type RequestId = string | number;

export interface JSONRPCRequest extends Request {
  jsonrpc: typeof JSONRPC_VERSION;
  id: RequestId;
}
```

The Python implementation is heavy! It shows up throughout the SDK as well. Module
docstring in `types.py` shows they outsourced to Claude and may be more focused on the
TypeScript SDK.

# Lifecycle

We need to standardize how servers and clients start communicating and manage ongoing
connections with each other. The goal of the lifecyle is to be "transport agnostic" so
that the same procedure is used if the client+server are communicating by mail, HTTP,
stdio, whatever.

Steps are 
1. Initialization
2. Operation
3. Shutdown

## Initialization

This ALWAYS comes first. Obvious but important. No batching.

Client sends an `Initialize` request to the server. Main aim here to the let the
server know 
  - What version of the protocol client we are following
  - What our capabilities are (only `roots` and `sampling`
  defined in the spec—more on those later. Can also declare `experimental`)
  - Basic info about name and version string (currently an `Implementation` in the spec).

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05", // Should be the most recent version we support
    "capabilities": {
      "roots": {
        "listChanged": true // If true, can send notifications when the "roots" list changes.
      },
      "sampling": {}
    },
    "clientInfo": {
      "name": "ExampleClient",
      "version": "1.0.0"
    }
  }
}
```

Server responds with an `InitializeResult`. Main aim is to communicate:
- We heard your `Intialize` request.
- Ensure protocol version compatibility. If the server supports the same version in the
client, it must respond with that version
- Declare capabilities (logging, prompts, tools, resources, completions, experimental?).
So
- Share name and version info
- Provide hints on how to interact with this server (optional instructions)

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "logging": {},
      "prompts": {
        "listChanged": true 
      },
      "resources": {
        "subscribe": true, // Client can subscribe to resource updates
        "listChanged": true
      },
      "tools": {
        "listChanged": true // Supports notifications when tool list changes
      }
    },
    "serverInfo": {
      "name": "ExampleServer",
      "version": "1.0.0"
    },
    "instructions": "Optional instructions for the client" // Can pass on to host LLM.
  }
}
```

If the protocol versions are compatible (server responds with a version client supports),
the client MUST send an `Initialized` notification.

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

This three message exchange is what we mean by "Initialization".

Spec encourages we don't send any other messages until initialization is complete.
If we do send a message, try to keep it to a ping. Makes sense.


### Where does Initialization happen in the SDK?

Initialization happens in session context. I.e., 
`with ClientSession as session`, `result = session.initialize()`.
The method constructs the `Initialize` request, sends it, waits for a server response,
and sends the `Initialized` notification, and returns the `result`. It also checks the
protocol version in there. If the version is not supported, raises a `RuntimeError`.

`ClientSession.initialize()` calls on the underlying `BaseSession.send_request()`
to send the request and listen for responses. Was confused about stream reading in the
`BaseSession`. It's using `_receive_loop` to forward message from the client read stream to
temporary streams created inside the `send_request` method. Nice! Apparently this allows
multiple concurrent requests to each wait on their *own* response while sharing the
same underlying transport.

**Read**
`test_session.py` modules in client and server tests. Mainly understand first
`initialize` test on each.

### Misc notes from looking at code

- `ServerSession` and `ClientSession` init look a bit different. Server as `init_options`.
- `ServerSession` has `check_client_capability` but `ClientSession` can't do the same.
Currently not using the `InitializeResult` except responding to it and checking protocol info.

**Typing is super confusing**
- Hard to understand `test_server_session_initialize`. The
messages in `server_session.incoming_messages` are supposed to be
`ServerRequestResponder` types, but then we look and see they can actually be
exceptions or client notifications.

```python
ServerRequestResponder = (
    RequestResponder[types.ClientRequest, types.ServerResult]
    | types.ClientNotification
    | Exception
)
```
The indirection is super confusing. Also, notifications and exceptions are responders.
We also end up having to check types again at runtime! This defeats the purpose of
static typing.

Maybe try

```python
# Clear, separate types
IncomingRequest = RequestResponder[types.ClientRequest, types.ServerResult]
IncomingNotification = types.ClientNotification
IncomingError = Exception

# Honest naming for the union
IncomingMessage = IncomingRequest | IncomingNotification | IncomingError

# Or better yet - separate streams with clear purposes
@property
def incoming_requests(self) -> MemoryObjectReceiveStream[IncomingRequest]:
    """Stream of requests that expect responses"""

@property  
def incoming_notifications(self) -> MemoryObjectReceiveStream[IncomingNotification]:
    """Stream of one-way notifications"""
```
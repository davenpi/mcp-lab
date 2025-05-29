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


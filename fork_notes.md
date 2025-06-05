## Why is it `Annotations` and not `Annotation`?

```typescript
export interface Annotations {
  /**
   * Describes who the intended customer of this object or data is.
   *
   * It can include multiple entries to indicate content useful for multiple audiences (e.g., `["user", "assistant"]`).
   */
  audience?: Role[];

  /**
   * Describes how important this data is for operating the server.
   *
   * A value of 1 means "most important," and indicates that the data is
   * effectively required, while 0 means "least important," and indicates that
   * the data is entirely optional.
   *
   * @TJS-type number
   * @minimum 0
   * @maximum 1
   */
  priority?: number;
}
```

## Session code may simplify a lot

May be able to get rid of `RequestResponder` entirely. No more nested context.
Just register handlers and then
```python
async def handle_message(self, raw_message: dict[str, Any]) -> dict[str, Any] | None:
    jsonrpc_msg = JSONRPCRequest.model_validate(raw_message)
    
    # Simple cancellation - one scope per request
    with anyio.CancelScope() as scope:
        self.in_flight[jsonrpc_msg.id] = scope
        
        try:
            request_cls = self.request_types[jsonrpc_msg.method]
            handler = self.handlers[jsonrpc_msg.method]
            
            request = jsonrpc_msg.to_request(request_cls)
            result = await handler(request)  # Handler just returns result
            
            # Session automatically sends response - no way to send twice!
            if result:
                return JSONRPCResponse.from_result(result, jsonrpc_msg.id).to_wire()
                
        finally:
            self.in_flight.pop(jsonrpc_msg.id, None)
```

## Spec JSON RPC for paginated request

Do we need to handle paginated requests too?

## Arguments about non DRY `from_protocol`

It's how we document the protocol.

The repetition is intentional semantic ownership, not accidental code duplication. Each concrete request class knows exactly what fields it expects and how to parse them, making the code locally reasoned about and independently evolvable. Abstracting this into the base class would force it to make assumptions about unknown fields, creating a dumping ground for edge cases that violates single responsibility. We're optimizing for clarity and maintainability of 12 known, stable request types rather than premature abstraction for hypothetical future changes. The 5-line from_protocol methods make each class independently understandable without hunting through inheritance hierarchies, and when InitializeRequest eventually needs special parsing logic, you modify just that class rather than adding complexity to a shared abstraction.

## Test philosophy reminders

Test names should be **behavioral specifications**, not just descriptions of what the test does.

Compare:
- `test_handles_malformed_input()` ← What does it do?
- `test_rejects_missing_method()` ← What should happen?

The second one tells you immediately what behavior broke when the test fails.

And yes, you should test every behavior you're afraid of breaking. This includes:

**Things you're afraid will break accidentally:**
- `test_preserves_progress_token_through_roundtrip()`
- `test_converts_snake_case_to_camelCase_in_output()`
- `test_ignores_unknown_fields_without_error()`

**Things you're afraid people will do wrong:**
- `test_rejects_request_without_method_field()`
- `test_rejects_invalid_client_info_structure()`

**Things you want to guarantee for your users:**
- `test_serialized_output_matches_typescript_spec()`
- `test_deserialization_never_silently_corrupts_data()`

The key insight: **your tests are documentation of what your code promises to do**. When someone reads `test_ignores_unknown_fields_without_error()`, they immediately understand that your SDK won't crash on unexpected protocol extensions.

Each test name should complete the sentence: "This SDK guarantees that it will..."
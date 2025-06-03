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
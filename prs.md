# Pain points to raise on the SDK code

- `Completions` capability not declared in `ServerCapabilites`
-  Can't call something like `check_server_capability` on client session since we don't
do anything else with the data after `ClientSession.initialize`.

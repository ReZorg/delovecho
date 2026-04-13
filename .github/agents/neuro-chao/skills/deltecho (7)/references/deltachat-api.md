# DeltaChat JSON-RPC API Quick Reference

This is a summary of key `deltachat-rpc-client` methods.

## Account Management

- `rpc.add_account()`: Creates a new, unconfigured account. Returns `account_id`.
- `rpc.batch_set_config(account_id, config_dict)`: Sets multiple configuration values for an account.
- `rpc.configure(account_id)`: Finalizes account setup and tests the connection.
- `rpc.get_all_accounts()`: Returns a list of all configured accounts.
- `rpc.get_chat_securejoin_qr_code(account_id)`: Gets the invite link/QR code for the bot's account.

## Message Handling

- `rpc.send_msg(account_id, chat_id, MsgData_object)`: Sends a message to a chat.
- `rpc.get_next_msgs(account_id)`: Polls for a list of unread message IDs.
- `rpc.wait_next_msgs(account_id)`: Asynchronously waits for new messages (less recommended).
- `rpc.get_messages(account_id, list_of_ids)`: Fetches full message objects for a list of IDs.
- `rpc.markseen_msgs(account_id, list_of_ids)`: Marks messages as read in the local database.

## Chat & Group Management

- `rpc.create_group(name)`: Creates a new group chat.
- `rpc.create_broadcast(name)`: Creates a new broadcast channel.
- `rpc.secure_join(qr_data)`: Joins a group using an invite QR code.
- `bot.get_chat(account_id, chat_id)`: Retrieves a `Chat` object.
- `bot.get_self_chat(account_id)`: Gets the special "self" chat for notes.

## Event Handling (`deltabot-cli`)

- `@cli.on(events.NewMessage)`: Decorator for functions that handle new incoming messages.
- `@cli.on(events.RawEvent)`: Decorator to log all raw events from the core.
- `event.msg`: The `Message` object associated with the event.
- `event.command`, `event.payload`: Parsed command and payload from messages starting with `/`.

## Key Objects

- `MsgData(text="...")`: Object used to create a new message for sending.
- `Message` (from `get_messages`): Contains all metadata about a received message (sender, chat ID, text, file attachments, etc.).
- `Chat`: Contains metadata about a chat (type, members, name, etc.).

# DeltaChat Bot Orchestration Patterns

Common patterns for building robust DeltaChat bots.

## 1. Command Router

Use a dictionary to map commands from `event.command` to handler functions.

```python
async def handle_help(bot, acc_id, event):
    # ...

async def handle_status(bot, acc_id, event):
    # ...

COMMANDS = {
    "/help": handle_help,
    "/status": handle_status,
}

@cli.on(events.NewMessage)
def route_command(bot, acc_id, event):
    if event.command in COMMANDS:
        handler = COMMANDS[event.command]
        asyncio.create_task(handler(bot, acc_id, event))
```

## 2. State Machine

Manage multi-step conversations using a state dictionary, keyed by `chat_id`.

```python
USER_STATES = {}

@cli.on(events.NewMessage)
def handle_stateful_convo(bot, acc_id, event):
    chat_id = event.msg.chat_id
    state = USER_STATES.get(chat_id, "START")

    if state == "START" and event.command == "/order":
        bot.rpc.send_msg(acc_id, chat_id, MsgData(text="What size? (small/medium/large)"))
        USER_STATES[chat_id] = "AWAITING_SIZE"
    elif state == "AWAITING_SIZE":
        # ... process size and move to next state
        bot.rpc.send_msg(acc_id, chat_id, MsgData(text="What toppings?"))
        USER_STATES[chat_id] = "AWAITING_TOPPINGS"
    # ...
```

## 3. Scheduler

Use `asyncio` to run periodic tasks, like sending reminders or fetching data.

```python
async def send_daily_report(bot, acc_id, chat_id):
    while True:
        await asyncio.sleep(24 * 3600) # wait 24 hours
        report = # ... generate report
        bot.rpc.send_msg(acc_id, chat_id, MsgData(text=report))

@cli.on(events.Startup)
def start_scheduler(bot, acc_id, event):
    # Start the scheduler for a specific chat
    report_chat_id = 123
    asyncio.create_task(send_daily_report(bot, acc_id, report_chat_id))
```

## 4. Multi-Account Orchestrator

Handle events for multiple bot accounts, routing logic based on `acc_id`.

```python
@cli.on(events.NewMessage)
def multi_account_handler(bot, acc_id, event):
    if acc_id == 1:
        # Logic for the first bot account
        pass
    elif acc_id == 2:
        # Logic for the second bot account
        pass
```

## 5. File & WebXDC Handler

Process incoming files and WebXDC messages.

```python
@cli.on(events.NewMessage)
def file_handler(bot, acc_id, event):
    msg = event.msg
    if msg.file:
        logging.info(f"Received file: {msg.file_name} ({msg.file_bytes} bytes)")
        # bot.rpc.get_file(acc_id, msg.id) -> to download the file

    if msg.webxdc_info:
        logging.info(f"Received WebXDC app: {msg.webxdc_info}")
        # Logic to interact with the WebXDC app
```

#!/usr/bin/env python3

from deltabot_cli import BotCli
from deltachat_rpc_client import MsgData, events

cli = BotCli("echobot_minimal")

@cli.on(events.NewMessage)
def echo(bot, acc_id, event):
    msg = event.msg
    reply = MsgData(text=f"Echo: {msg.text}")
    bot.rpc.send_msg(acc_id, msg.chat_id, reply)

if __name__ == "__main__":
    cli.start()

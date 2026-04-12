#!/usr/bin/env python3

import asyncio
import logging

from deltabot_cli import BotCli
from deltachat_rpc_client import MsgData, events

# These would be imported from the skill's scripts
from rag_integration import RAGIntegration
from cognitive_pipeline import CognitivePipeline

# --- Initialization ---
logging.basicConfig(level=logging.INFO)

# Initialize cognitive components
rag = RAGIntegration(db_path="my_bot_kb.db")
cognitive_pipeline = CognitivePipeline()

# Initialize the bot CLI
cli = BotCli("cognitive_bot")

# --- Event Handlers ---

@cli.on(events.NewMessage)
def process_new_message(bot, acc_id, event):
    """Main handler for incoming messages."""
    msg = event.msg
    chat = bot.get_chat(acc_id, msg.chat_id)
    logging.info(f"Received message in chat {msg.chat_id} of type {chat.chat_type}")

    # Ignore own messages
    if msg.from_id == bot.get_self_contact(acc_id).id:
        return

    # 1. Set Persona based on chat type
    cognitive_pipeline.set_persona(chat.chat_type)

    # 2. Augment with RAG
    logging.info(f"Querying RAG with: {msg.text}")
    rag_context = rag.build_rag_context(msg.text)
    if rag_context:
        augmented_text = f"{msg.text}\n\n--- From Knowledge Base ---\n{rag_context}"
        logging.info("Augmented message with RAG context.")
    else:
        augmented_text = msg.text

    # 3. Process through cognitive pipeline
    response_text = cognitive_pipeline.process_message(augmented_text)

    # 4. Send Response
    reply = MsgData(text=response_text)
    bot.rpc.send_msg(acc_id, msg.chat_id, reply)
    logging.info(f"Sent cognitive reply to chat {msg.chat_id}")

@cli.on(events.RawEvent)
def log_event(bot, acc_id, event):
    """Log all raw events for debugging."""
    bot.logger.debug(event)

# --- CLI Commands for the Bot ---

@cli.command("add-knowledge")
def add_knowledge_command(bot, acc_id, payload):
    """Command to add new knowledge to the RAG system. Usage: /add-knowledge <text>"""
    if not payload:
        bot.rpc.send_msg(acc_id, bot.get_self_chat(acc_id).id, MsgData(text="Usage: /add-knowledge <text_to_add>"))
        return

    logging.info(f"Adding knowledge: {payload}")
    source_id = rag.add_knowledge_source("text", payload)
    rag.process_source(source_id)
    bot.rpc.send_msg(acc_id, bot.get_self_chat(acc_id).id, MsgData(text=f"Added and processed knowledge source ID: {source_id}"))

@cli.command("status")
def status_command(bot, acc_id, payload):
    """Command to get the bot's cognitive status."""
    status_text = (
        f"**Cognitive Status**\n"
        f"- Persona: {cognitive_pipeline.persona}\n"
        f"- Valence: {cognitive_pipeline.valence:.2f}\n"
        f"- Arousal: {cognitive_pipeline.arousal:.2f}"
    )
    bot.rpc.send_msg(acc_id, event.msg.chat_id, MsgData(text=status_text))


if __name__ == "__main__":
    # This block allows the script to be run directly to start the bot.
    cli.start()

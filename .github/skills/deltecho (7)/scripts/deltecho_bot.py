#!/usr/bin/env python3

import asyncio
import logging

from deltabot_cli import BotCli
from deltachat_rpc_client import MsgData, events

from rag_integration import RAGIntegration
from cognitive_pipeline import CognitivePipeline
# from reservoir_nodes import DeltaChatMessageNode, ConversationStateNode, CognitiveResponseNode
# from reservoirpy.nodes import Reservoir, Ridge

# Initialize cognitive components
rag = RAGIntegration()
cognitive_pipeline = CognitivePipeline()

# # Initialize Reservoir
# msg_encoder = DeltaChatMessageNode()
# reservoir = Reservoir(100, lr=0.5, sr=0.9)
# readout = Ridge(ridge=1e-6)
# esn = msg_encoder >> reservoir >> readout

cli = BotCli("deltecho")

@cli.on(events.NewMessage)
def process_new_message(bot, acc_id, event):
    msg = event.msg
    chat = bot.get_chat(acc_id, msg.chat_id)

    # 1. Set Persona
    cognitive_pipeline.set_persona(chat.chat_type)

    # 2. Augment with RAG
    rag_context = rag.build_rag_context(msg.text)
    augmented_text = f"{msg.text}\n\n--- Knowledge Base ---\n{rag_context}"

    # 3. Process through cognitive pipeline
    response_text = cognitive_pipeline.process_message(augmented_text)

    # 4. Update Reservoir (conceptual)
    # esn.run(msg.to_json()) # to_json() is not a real method, conceptual
    # response_vector = model.encode(response_text) # conceptual
    # esn.train(msg_vector, response_vector) # conceptual

    # 5. Send Response
    reply = MsgData(text=response_text)
    bot.rpc.send_msg(acc_id, msg.chat_id, reply)
    logging.info(f"Sent reply to chat {msg.chat_id}")

@cli.on(events.RawEvent)
def log_event(bot, acc_id, event):
    bot.logger.info(event)

@cli.command("add-knowledge")
def add_knowledge_command(bot, acc_id, payload):
    source_id = rag.add_knowledge_source('text', payload)
    rag.process_source(source_id)
    bot.rpc.send_msg(acc_id, bot.get_self_chat(acc_id).id, MsgData(text=f"Added and processed knowledge source ID: {source_id}"))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli.start()

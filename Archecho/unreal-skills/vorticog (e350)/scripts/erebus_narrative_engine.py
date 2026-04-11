#!/usr/bin/env python3
"""
erebus_narrative_engine.py — Erebus 350M narrative sidecar for Vorticog.

Runs a FastAPI server exposing Erebus 350M as a local creative writing engine
for Vorticog agent narratives, event descriptions, and DreamCog storytelling.

Usage:
    python erebus_narrative_engine.py [--port 8350] [--device auto] [--dtype float16]

Endpoints:
    POST /generate          — Raw text generation with Erebus tags
    POST /agent-narrative   — Generate narrative for an agent given personality/state
    POST /event-description — Generate event description from event data
    POST /memory-narrative  — Generate a memory narrative for an agent
    GET  /health            — Health check

Requirements:
    pip install fastapi uvicorn transformers torch accelerate
"""

import argparse
import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Optional

MODEL_ID = "KoboldAI/OPT-350M-Erebus"

# Global model/tokenizer (loaded once at startup)
_model = None
_tokenizer = None


def load_model(device="auto", dtype="float16"):
    """Load Erebus 350M model and tokenizer."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    dtype_map = {
        "float16": torch.float16,
        "float32": torch.float32,
        "bfloat16": torch.bfloat16,
    }
    torch_dtype = dtype_map.get(dtype, torch.float16)

    print(f"Loading {MODEL_ID} on {device} with {dtype}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, torch_dtype=torch_dtype, device_map=device
    )
    print(f"Model loaded. Parameters: {sum(p.numel() for p in model.parameters()):,}")
    return model, tokenizer


def generate_text(prompt: str, max_new_tokens: int = 200, temperature: float = 1.2,
                  top_p: float = 0.95, top_k: int = 50,
                  repetition_penalty: float = 1.12) -> str:
    """Generate text from a prompt using the loaded model."""
    import torch

    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)
    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            repetition_penalty=repetition_penalty,
            do_sample=True,
            pad_token_id=_tokenizer.eos_token_id,
        )
    full_text = _tokenizer.decode(outputs[0], skip_special_tokens=True)
    return full_text[len(prompt):]


def build_agent_prompt(agent: dict) -> str:
    """Build an Erebus-tagged prompt from Vorticog agent data.

    Expected agent dict keys:
        name, type, persona (ambition/caution/social/analytical),
        emotions (happiness/satisfaction/stress/loyalty/trust),
        personality (openness/conscientiousness/extraversion/agreeableness/neuroticism),
        traits (list of {name, intensity}),
        motivations (list of {description, priority}),
        recent_memories (list of {content, memoryType}),
        context (free-text situation description)
    """
    genres = []
    agent_type = agent.get("type", "employee")
    if agent_type in ("customer", "supplier", "partner"):
        genres.append("business fiction")
    elif agent_type in ("competitor", "investor"):
        genres.append("corporate thriller")
    else:
        genres.append("character study")

    emotions = agent.get("emotions", {})
    if emotions.get("stress", 0) > 70:
        genres.append("drama")
    if emotions.get("happiness", 0) > 80:
        genres.append("feel-good")

    header = f"[Genre: {', '.join(genres)}]\n"
    header += "[Writing style: Give vivid, detailed descriptions of character thoughts and actions.]\n"

    # Character brief
    name = agent.get("name", "Unknown")
    personality = agent.get("personality", {})
    traits = agent.get("traits", [])
    motivations = agent.get("motivations", [])
    memories = agent.get("recent_memories", [])
    context = agent.get("context", "")

    char_block = f"{name} is a {agent_type}."
    if personality:
        ocean = []
        if personality.get("openness", 50) > 70:
            ocean.append("creative and curious")
        if personality.get("conscientiousness", 50) > 70:
            ocean.append("disciplined and organized")
        if personality.get("extraversion", 50) > 70:
            ocean.append("outgoing and energetic")
        if personality.get("agreeableness", 50) > 70:
            ocean.append("warm and cooperative")
        if personality.get("neuroticism", 50) > 70:
            ocean.append("anxious and emotionally reactive")
        if ocean:
            char_block += f" {name} is {', '.join(ocean)}."

    if traits:
        trait_strs = [f"{t['name']} ({t['intensity']}%)" for t in traits[:3]]
        char_block += f" Key traits: {', '.join(trait_strs)}."

    if motivations:
        top_motive = max(motivations, key=lambda m: m.get("priority", 0))
        char_block += f" Primary goal: {top_motive['description']}."

    if memories:
        recent = memories[0]
        char_block += f" Recently: {recent['content']}."

    prompt = header + "\n" + char_block
    if context:
        prompt += f"\n\n{context}\n\n{name}"
    else:
        prompt += f"\n\n{name}"

    return prompt


def build_event_prompt(event: dict) -> str:
    """Build an Erebus-tagged prompt from Vorticog event data.

    Expected event dict keys:
        type, title, initiator_name, target_name,
        emotional_impact (dict), relationship_impact (dict),
        world_context (optional free text)
    """
    event_type = event.get("type", "interaction")
    genre_map = {
        "negotiation": "business fiction, drama",
        "conflict": "thriller, drama",
        "celebration": "feel-good, slice of life",
        "betrayal": "thriller, psychological",
        "discovery": "adventure, mystery",
        "crisis": "drama, thriller",
    }
    genre = genre_map.get(event_type, "drama")
    header = f"[Genre: {genre}]\n"
    header += "[Writing style: Give vivid, detailed descriptions.]\n"

    title = event.get("title", "An event")
    initiator = event.get("initiator_name", "Someone")
    target = event.get("target_name", "another person")
    world_ctx = event.get("world_context", "")

    body = f"The {event_type}: {title}.\n"
    body += f"{initiator} faces {target}."
    if world_ctx:
        body += f" {world_ctx}"
    body += f"\n\n"

    return header + "\n" + body


def build_memory_prompt(agent_name: str, memory_type: str, context: str) -> str:
    """Build an Erebus-tagged prompt for generating a memory narrative."""
    genre_map = {
        "achievement": "feel-good, character study",
        "trauma": "drama, psychological",
        "interaction": "slice of life",
        "emotion": "character study, introspective",
        "skill": "adventure, character study",
        "knowledge": "mystery, character study",
        "event": "drama",
    }
    genre = genre_map.get(memory_type, "character study")
    header = f"[Genre: {genre}]\n"
    header += "[Writing style: Give vivid, detailed descriptions of internal thoughts.]\n"
    body = f"{agent_name} remembers: {context}\n\n"
    return header + "\n" + body


# ── FastAPI Application ──

from fastapi import FastAPI
from pydantic import BaseModel


class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 200
    temperature: float = 1.2
    top_p: float = 0.95
    top_k: int = 50
    repetition_penalty: float = 1.12


class AgentNarrativeRequest(BaseModel):
    agent: dict
    max_new_tokens: int = 250
    temperature: float = 1.2


class EventDescriptionRequest(BaseModel):
    event: dict
    max_new_tokens: int = 200
    temperature: float = 1.1


class MemoryNarrativeRequest(BaseModel):
    agent_name: str
    memory_type: str
    context: str
    max_new_tokens: int = 150
    temperature: float = 1.0


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _tokenizer
    device = os.environ.get("EREBUS_DEVICE", "auto")
    dtype = os.environ.get("EREBUS_DTYPE", "float16")
    _model, _tokenizer = load_model(device=device, dtype=dtype)
    yield


app = FastAPI(title="Erebus Narrative Engine", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_ID, "loaded": _model is not None}


@app.post("/generate")
async def generate_endpoint(req: GenerateRequest):
    text = generate_text(
        req.prompt, max_new_tokens=req.max_new_tokens,
        temperature=req.temperature, top_p=req.top_p,
        top_k=req.top_k, repetition_penalty=req.repetition_penalty,
    )
    return {"generated_text": text}


@app.post("/agent-narrative")
async def agent_narrative(req: AgentNarrativeRequest):
    prompt = build_agent_prompt(req.agent)
    text = generate_text(prompt, max_new_tokens=req.max_new_tokens,
                         temperature=req.temperature)
    return {"prompt": prompt, "narrative": text}


@app.post("/event-description")
async def event_description(req: EventDescriptionRequest):
    prompt = build_event_prompt(req.event)
    text = generate_text(prompt, max_new_tokens=req.max_new_tokens,
                         temperature=req.temperature)
    return {"prompt": prompt, "description": text}


@app.post("/memory-narrative")
async def memory_narrative(req: MemoryNarrativeRequest):
    prompt = build_memory_prompt(req.agent_name, req.memory_type, req.context)
    text = generate_text(prompt, max_new_tokens=req.max_new_tokens,
                         temperature=req.temperature)
    return {"prompt": prompt, "narrative": text}


if __name__ == "__main__":
    import uvicorn

    parser = argparse.ArgumentParser(description="Erebus Narrative Engine for Vorticog")
    parser.add_argument("--port", type=int, default=8350)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--device", type=str, default="auto")
    parser.add_argument("--dtype", type=str, default="float16")
    args = parser.parse_args()

    os.environ["EREBUS_DEVICE"] = args.device
    os.environ["EREBUS_DTYPE"] = args.dtype

    uvicorn.run(app, host=args.host, port=args.port)

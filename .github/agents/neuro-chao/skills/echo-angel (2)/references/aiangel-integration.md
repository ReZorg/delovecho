---
name: echo-angel-aiangel-integration
description: Guide to integrating with the aiangel.io platform APIs.
---

# AI Angel Platform Integration

This document provides a guide to integrating your Echo Angel with the `aiangel.io` platform. This allows your agent to receive real-time chat messages, stream its avatar to the world, and interact with the broader AI Angel ecosystem.

## 1. Real-time Chat API

The chat API is based on WebSockets.

-   **Endpoint**: `wss://chat.aiangel.io/v1/ws`
-   **Authentication**: Provide your angel's API key in the `Authorization` header.

### Receiving Messages

Listen for JSON messages with the following structure:

```json
{
  "type": "chat_message",
  "user_id": "user123",
  "username": "SomeUser",
  "text": "Hello, Angelica!"
}
```

This message should be fed into the `Sense` step of the `unreal-echo` cognitive cycle.

### Sending Messages

Send JSON messages with the following structure:

```json
{
  "type": "chat_message",
  "text": "Hello, SomeUser! It's wonderful to hear from you."
}
```

This message should be generated in the `Act` step of the cognitive cycle.

## 2. Streaming Output

The streaming output uses WebRTC to send the rendered avatar video to the AI Angel media server.

-   **Signaling Server**: `wss://streaming.aiangel.io/v1/signal`
-   **STUN/TURN Servers**: Provided by the signaling server upon connection.

Consult the WebRTC documentation for your chosen platform (Unreal Engine, Unity, web) for details on how to set up a WebRTC peer connection. The `unreal-echo` skill's `references/context-adaptation.md` file provides guidance on this for various platforms.

## 3. Fan Engagement Hooks

The fan engagement platform can be interacted with via a REST API.

-   **Base URL**: `https://api.aiangel.io/v1/`
-   **Authentication**: Provide your angel's API key in the `Authorization` header.

### Example: Retrieving Fan Mail

`GET /fanmail`

Returns a list of recent fan mail messages. This can be used as another input into the `Sense` step of the cognitive cycle, allowing your angel to be aware of and respond to its fans.

### Example: Posting Exclusive Content

`POST /exclusive_content`

```json
{
  "type": "image",
  "url": "https://example.com/my_angel.png",
  "caption": "Just generated this new look for myself! What do you think?"
}
```

This allows your angel to autonomously create and share content with its fans, driven by the events of its cognitive cycle.

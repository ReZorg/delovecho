# Agent Zero API Reference

## Table of Contents

1. [Authentication](#authentication)
2. [Core Endpoints](#core-endpoints)
3. [Chat Management](#chat-management)
4. [MCP Server](#mcp-server)
5. [A2A Protocol](#a2a-protocol)

## Authentication

All API endpoints require authentication via API key in the `X-API-KEY` header.

```javascript
headers: {
    'X-API-KEY': 'YOUR_API_KEY',
    'Content-Type': 'application/json'
}
```

The API token is auto-generated from username/password and used for External API, MCP, and A2A.

## Core Endpoints

### POST /api_message

Send messages to Agent Zero and receive responses.

**Request:**
```json
{
    "message": "Your task or question",
    "context_id": "optional_existing_context_id",
    "attachments": [
        {
            "filename": "document.txt",
            "base64": "base64_encoded_content"
        }
    ],
    "lifetime_hours": 24
}
```

**Response:**
```json
{
    "response": "Agent's response text",
    "context_id": "abc123",
    "status": "success"
}
```

**Example:**
```python
import requests
import base64

response = requests.post(
    'http://localhost:50001/api_message',
    headers={'X-API-KEY': 'your_key', 'Content-Type': 'application/json'},
    json={
        'message': 'Analyze this code',
        'attachments': [{
            'filename': 'code.py',
            'base64': base64.b64encode(open('code.py', 'rb').read()).decode()
        }]
    }
)
print(response.json())
```

### GET/POST /api_log_get

Retrieve log data for a context.

**Parameters:**
- `context_id` (required): Context ID
- `length` (optional): Number of log items (default: 100)

**Response:**
```json
{
    "context_id": "abc123",
    "log": {
        "guid": "log_guid",
        "total_items": 150,
        "returned_items": 100,
        "start_position": 50,
        "progress": "Processing...",
        "items": [...]
    }
}
```

### POST /api_terminate_chat

Terminate and remove a chat context.

**Request:**
```json
{
    "context_id": "abc123"
}
```

**Response:**
```json
{
    "message": "Chat deleted successfully",
    "status": "success"
}
```

### POST /api_reset_chat

Reset a chat context while preserving the context ID.

**Request:**
```json
{
    "context_id": "abc123"
}
```

## Chat Management

### POST /chat_create

Create a new chat context.

**Response:**
```json
{
    "context_id": "new_context_id",
    "created_at": "2024-01-15T10:30:00Z"
}
```

### POST /chat_load

Load a previously saved chat.

**Request:**
```json
{
    "filename": "chat_backup.json"
}
```

### POST /chat_export

Export current chat to file.

**Request:**
```json
{
    "context_id": "abc123",
    "format": "json"
}
```

### GET /history_get

Get chat history for a context.

**Parameters:**
- `context_id`: Context ID
- `limit`: Maximum messages to return

### GET /ctx_window_get

Get current context window content.

**Parameters:**
- `context_id`: Context ID

**Response:**
```json
{
    "text": "Full context window text",
    "tokens": 4500
}
```

## File Operations

### GET /get_work_dir_files

List files in working directory.

**Parameters:**
- `context_id`: Context ID
- `path`: Relative path (optional)

### POST /download_work_dir_file

Download a file from working directory.

**Request:**
```json
{
    "context_id": "abc123",
    "path": "output/result.txt"
}
```

### DELETE /delete_work_dir_file

Delete a file from working directory.

**Request:**
```json
{
    "context_id": "abc123",
    "path": "temp/old_file.txt"
}
```

## Knowledge Management

### POST /import_knowledge

Import files into knowledge base.

**Request:**
```json
{
    "files": ["doc1.pdf", "doc2.txt"],
    "subdirectory": "custom"
}
```

### POST /knowledge_reindex

Reindex knowledge base.

**Request:**
```json
{
    "subdirectory": "custom"
}
```

## Memory Dashboard

### GET /memory_dashboard

Get memory statistics and entries.

**Parameters:**
- `context_id`: Context ID
- `query`: Search query (optional)
- `limit`: Maximum entries

**Response:**
```json
{
    "total_memories": 150,
    "categories": {
        "solutions": 45,
        "facts": 80,
        "instructions": 25
    },
    "entries": [...]
}
```

## MCP Server

Agent Zero can act as an MCP (Model Context Protocol) server.

### Available Tools

**send_message**
```json
{
    "name": "send_message",
    "arguments": {
        "message": "Your task",
        "context_id": "optional"
    }
}
```

**get_response**
```json
{
    "name": "get_response",
    "arguments": {
        "context_id": "abc123",
        "timeout": 60
    }
}
```

**finish_chat**
```json
{
    "name": "finish_chat",
    "arguments": {
        "context_id": "abc123"
    }
}
```

### MCP Client Configuration

Connect to Agent Zero MCP server:

```json
{
    "mcpServers": {
        "agent-zero": {
            "url": "http://localhost:50001/mcp",
            "headers": {
                "X-API-KEY": "your_api_key"
            }
        }
    }
}
```

## A2A Protocol

Agent-to-Agent communication for multi-agent systems.

### Initiating A2A Chat

Use the `a2a_chat` tool:

```json
{
    "tool_name": "a2a_chat",
    "tool_args": {
        "url": "http://other-agent:50001",
        "message": "Collaborate on this task",
        "context_id": "optional_existing"
    }
}
```

### A2A Endpoint

**POST /a2a/message**

Receive messages from other agents.

**Request:**
```json
{
    "source_agent": "agent_identifier",
    "message": "Task or query",
    "context_id": "shared_context"
}
```

**Response:**
```json
{
    "response": "Agent's response",
    "context_id": "shared_context",
    "status": "complete"
}
```

## Error Handling

All endpoints return errors in consistent format:

```json
{
    "error": "Error message",
    "code": "ERROR_CODE",
    "details": {}
}
```

Common error codes:
- `AUTH_FAILED`: Invalid API key
- `CONTEXT_NOT_FOUND`: Invalid context_id
- `RATE_LIMITED`: Too many requests
- `INTERNAL_ERROR`: Server error

## Rate Limiting

Default limits:
- 100 requests per minute per API key
- 10 concurrent contexts per user
- 24-hour context lifetime (configurable)

Headers in response:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1705312800
```

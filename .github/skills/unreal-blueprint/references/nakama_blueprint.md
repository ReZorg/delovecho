# Nakama Multiplayer Blueprint Patterns

## Overview

Nakama is an open-source game server that provides authentication, matchmaking, real-time multiplayer, and social features. These Blueprint patterns enable multiplayer DTE cognitive avatar synchronization.

## Authentication Blueprint

```
Event BeginPlay (or Custom Event: InitializeHiro)
├─ Create Default Client
│   ├─ Server Key: "defaultkey"
│   ├─ Host: "localhost" (or production server)
│   ├─ Port: 7350
│   ├─ Use SSL: false (true for production)
│   └─ Enable Debug: true (false for production)
├─ SET → NakamaClient variable
├─ Make Literal String → UserID (e.g., "TestRicard05")
├─ AuthenticateCustom
│   ├─ Client: NakamaClient
│   ├─ User ID: UserID
│   ├─ Username: (optional display name)
│   ├─ Create Account: true
│   ├─ Vars: Make Map (optional key-value metadata)
│   ├─ On Success → SET Session variable
│   │   └─ Call "JoinOrCreateMatch"
│   └─ On Error → Break Nakama Error
│       └─ Append "AuthError" + Message → Print String (Development Only)
```

## Match Management

```
Custom Event: JoinOrCreateMatch
├─ Create Match (Session, NakamaClient)
│   ├─ On Success → SET MatchID
│   │   └─ Start Expression Sync Timer (10 Hz)
│   └─ On Error → Join Match by ID (fallback)
```

## Expression State Synchronization

Sync AU values across the network at 10 Hz (sufficient for facial animation):

```
Custom Event: SyncExpressionState (Timer, 0.1s interval)
├─ Get BP_ExpressionBridge → Get ActionUnitValues (Map<String, Float>)
├─ Serialize to JSON: {"AU1":0.3,"AU6":0.5,"AU12":0.7,...}
├─ Send Match State
│   ├─ Opcode: 1 (expression data)
│   ├─ Data: JSON string
│   └─ Presences: empty (broadcast to all)
```

## Receiving Remote Expression Data

```
Event: On Match State Received
├─ Switch on Opcode
│   ├─ Case 1 (Expression):
│   │   ├─ Get Sender UserID
│   │   ├─ Find Remote Character by UserID
│   │   ├─ Deserialize JSON → Map<String, Float>
│   │   └─ Apply to Remote Character's BP_ExpressionBridge
│   ├─ Case 2 (Cognitive State):
│   │   └─ Update remote character's cognitive display
│   └─ Case 3 (Chat Message):
│       └─ Display in chat UI
```

## Bandwidth Optimization

Full AU map at 10 Hz = ~200 bytes/tick = 2 KB/s per character. For large sessions, use delta compression:

```
Custom Event: SyncExpressionDelta
├─ Compare current AUs with last-sent AUs
├─ Only include AUs that changed by > 0.05
├─ Serialize delta: {"AU12":0.7,"AU6":0.5} (only changed values)
├─ Send Match State (Opcode: 4, delta)
└─ Update last-sent cache
```

This reduces bandwidth to ~50-100 bytes/tick for typical conversations.

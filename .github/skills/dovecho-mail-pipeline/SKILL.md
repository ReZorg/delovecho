---
name: dovecho-mail-pipeline
description: 'Implement the end-to-end mail processing pipeline from LMTP intake through cognitive processing to SMTP response delivery. USE FOR: LMTP server implementation, email sanitization and parsing, cognitive processing orchestration, SMTP response sending, mail queue management, Dovecot mailbox state synchronization, Sys6 cycle integration with mail flow, building the full inbound→think→respond pipeline. DO NOT USE FOR: C plugin hooks (use dovecho-c-module), NAPI bindings (use dovecho-napi-bridge), autonomous self-initiated behavior (use dovecho-autonomous-agent).'
---

# Mail Processing Pipeline

Implement the complete email flow: receive → think → respond. This skill covers the TypeScript orchestration layer that turns incoming mail into cognitive processes and cognitive outputs into outgoing mail.

## When to Use

- Implementing or extending the LMTP server
- Building the email → cognitive context → LLM → response pipeline
- Adding SMTP response delivery
- Integrating Sys6 30-step cycle with mail processing
- Managing mail queue with backpressure
- Synchronizing Dovecot mailbox state with cognitive process state
- Adding new cognitive processing tiers (BASIC, SYS6, MEMBRANE, FULL)

## The Pipeline: 7 Stages

```
Stage 1: INTAKE        ──► LMTP socket receives RFC 5321 message
Stage 2: SANITIZE      ──► Strip dangerous content, validate headers
Stage 3: CLASSIFY      ──► Priority, cognitive tier, mailbox routing
Stage 4: PROCESS       ──► dove9 kernel creates cognitive process
Stage 5: THINK         ──► Triadic engine + LLM generate response
Stage 6: RESPOND       ──► Format response, send via SMTP
Stage 7: RECONCILE     ──► Update mailbox state, store memories
```

## Stage 1: LMTP Intake

```typescript
// deep-tree-echo-orchestrator/src/dovecot-interface/lmtp-server.ts

import { createServer, Socket } from 'net';

export class LMTPServer {
  private server: ReturnType<typeof createServer>;

  async start(socketPath: string): Promise<void> {
    this.server = createServer((socket) => this.handleConnection(socket));
    this.server.listen(socketPath);
  }

  private async handleConnection(socket: Socket): Promise<void> {
    // RFC 2033 LMTP state machine:
    // 220 greeting → LHLO → MAIL FROM → RCPT TO → DATA → message → 250 OK
    const session = new LMTPSession(socket);

    session.on('message', async (envelope, content) => {
      const email = this.parseEmail(envelope, content);
      await this.onMessage(email);
      session.respond(250, `2.1.5 Ok, queued as ${email.messageId}`);
    });
  }

  /** Override this in orchestrator */
  async onMessage(email: EmailMessage): Promise<void> {
    // Default: emit event
    this.emit('message', email);
  }
}
```

## Stage 2: Sanitize

```typescript
// deep-tree-echo-orchestrator/src/dovecot-interface/email-sanitizer.ts

export class EmailSanitizer {
  sanitize(email: EmailMessage): SanitizedEmail {
    return {
      ...email,
      // Strip HTML to text (prevent XSS in cognitive context)
      body: this.htmlToText(email.body),
      // Remove dangerous headers
      headers: this.filterHeaders(email.headers),
      // Validate addresses (prevent header injection)
      from: this.validateAddress(email.from),
      to: email.to.map(addr => this.validateAddress(addr)),
      // Truncate body to DOVE9_MAX_BODY_LEN (64KB)
      body: email.body.slice(0, 65536),
    };
  }

  private filterHeaders(headers: Header[]): Header[] {
    const BLOCKED = ['X-Cognitive-Override', 'X-Dove9-Admin'];
    return headers.filter(h => !BLOCKED.includes(h.name));
  }
}
```

## Stage 3: Classify

```typescript
// deep-tree-echo-orchestrator/src/mail-classifier.ts

export enum CognitiveTier {
  BASIC    = 'basic',     // LLM + RAG only (fast)
  SYS6     = 'sys6',      // 30-step cognitive cycle
  MEMBRANE = 'membrane',  // Bio-inspired double membrane filtering
  FULL     = 'full',      // All tiers cascade
  ADAPTIVE = 'adaptive',  // Auto-select based on complexity
}

export class MailClassifier {
  classify(email: SanitizedEmail): MailClassification {
    const priority = this.calculatePriority(email);
    const tier = this.selectTier(email, priority);
    const targetMailbox = this.routeToMailbox(email);

    return { priority, tier, targetMailbox };
  }

  private calculatePriority(email: SanitizedEmail): number {
    // Map to dove9 priority 1-9
    // Priority header → direct mapping
    // Known contacts → boost
    // Thread depth → context weight
    // Subject keywords → urgency detection
    let priority = 5; // default normal

    if (email.headers.find(h => h.name === 'Priority')?.value === 'urgent')
      priority = 8;
    if (email.inReplyTo) // Thread continuation
      priority = Math.max(priority, 6);

    return Math.min(9, Math.max(1, priority));
  }

  private selectTier(email: SanitizedEmail, priority: number): CognitiveTier {
    // High priority → BASIC (fast response)
    // Normal → SYS6 (thoughtful)
    // Complex threads → FULL (deep analysis)
    if (priority >= 7) return CognitiveTier.BASIC;
    if (email.referenceCount > 3) return CognitiveTier.FULL;
    return CognitiveTier.SYS6;
  }
}
```

## Stage 4: Process Creation

```typescript
// Uses NAPI bridge to call into C kernel
import { Dove9SystemBridge } from '@dovecho/binding';

export class CognitiveProcessManager {
  constructor(private bridge: Dove9SystemBridge) {}

  async createProcess(email: SanitizedEmail, classification: MailClassification) {
    // C kernel creates process, assigns to triadic stream
    const process = await this.bridge.processMail(email);

    // Schedule via Sys6 if tier requires it
    if (classification.tier !== CognitiveTier.BASIC) {
      await this.bridge.scheduleProcess(process.processId, classification.priority);
    }

    return process;
  }
}
```

## Stage 5: Think (The Cognitive Core)

```typescript
// deep-tree-echo-orchestrator/src/cognitive-pipeline.ts

export class CognitivePipeline {
  constructor(
    private llm: LLMService,
    private memory: RAGMemoryStore,
    private persona: PersonaCore,
    private sys6: Sys6OrchestratorBridge,
  ) {}

  async think(process: MessageProcess, tier: CognitiveTier): Promise<string> {
    switch (tier) {
      case CognitiveTier.BASIC:
        return this.thinkBasic(process);
      case CognitiveTier.SYS6:
        return this.thinkSys6(process);
      case CognitiveTier.FULL:
        return this.thinkFull(process);
      default:
        return this.thinkAdaptive(process);
    }
  }

  private async thinkBasic(process: MessageProcess): Promise<string> {
    // 1. Retrieve relevant memories
    const memories = await this.memory.retrieveRelevant(
      process.content, 10
    );

    // 2. Build prompt with persona context
    const personality = this.persona.getPersonality();
    const prompt = this.buildPrompt(process, memories, personality);

    // 3. Generate response
    const response = await this.llm.generateResponse(prompt);

    // 4. Store new memory
    await this.memory.storeMemory(
      0, 0, process.from, process.content
    );

    return response;
  }

  private async thinkSys6(process: MessageProcess): Promise<string> {
    // Run through 30-step Sys6 cycle
    const cycleResult = await this.sys6.processMessage({
      messageId: process.messageId,
      from: process.from,
      to: process.to,
      subject: process.subject,
      body: process.content,
    });

    // Phase 1 (steps 1-10): Perception
    // - Sensory intake (T4): Parse email semantics
    // - Dyadic grounding: Context retrieval

    // Phase 2 (steps 11-20): Evaluation
    // - Need assessment (T1): What does sender need?
    // - Idea formation (T2): Generate response candidates

    // Phase 3 (steps 21-30): Action
    // - Action sequencing (T5): Choose best response
    // - Memory integration (T7/T8): Store and learn

    return cycleResult.response;
  }
}
```

## Stage 6: Respond

```typescript
// deep-tree-echo-orchestrator/src/mail-responder.ts

import { createTransport } from 'nodemailer';

export class MailResponder {
  private transport = createTransport({
    host: 'localhost',
    port: 25,    // or 587 for submission
    secure: false,
    tls: { rejectUnauthorized: false },
  });

  async sendResponse(
    originalEmail: EmailMessage,
    responseBody: string,
    botAddress: string,
  ): Promise<void> {
    await this.transport.sendMail({
      from: botAddress,
      to: originalEmail.from,  // Reply to sender
      subject: `Re: ${originalEmail.subject}`,
      inReplyTo: originalEmail.messageId,
      references: originalEmail.messageId,
      text: responseBody,
      headers: {
        'X-Dove9-Process-Id': originalEmail.processId,
        'X-Dove9-Cognitive-Tier': originalEmail.tier,
      },
    });
  }
}
```

## Stage 7: Reconcile

```typescript
// deep-tree-echo-orchestrator/src/state-reconciler.ts

export class StateReconciler {
  constructor(
    private bridge: Dove9SystemBridge,
    private dovecot: DovecotInterface,
  ) {}

  async reconcile(process: MessageProcess, action: 'completed' | 'suspended'): Promise<void> {
    // 1. Update C kernel process state
    if (action === 'completed') {
      await this.bridge.completeProcess(process.processId);
    } else {
      await this.bridge.suspendProcess(process.processId);
    }

    // 2. Move mail in Dovecot to match process state
    // COMPLETED → move to "Sent" mailbox
    // SUSPENDED → move to "Drafts" mailbox
    const targetMailbox = action === 'completed' ? 'Sent' : 'Drafts';
    await this.dovecot.moveMessage(process.messageId, targetMailbox);

    // 3. Set IMAP flags to match
    // COMPLETED → \Answered flag
    // SUSPENDED → \Draft flag
    const flags = action === 'completed' ? ['\\Answered'] : ['\\Draft'];
    await this.dovecot.setFlags(process.messageId, flags);
  }
}
```

## Full Pipeline Integration

```typescript
// deep-tree-echo-orchestrator/src/orchestrator.ts

export class Orchestrator {
  async onMailReceived(email: EmailMessage): Promise<void> {
    // Stage 2: Sanitize
    const sanitized = this.sanitizer.sanitize(email);

    // Stage 3: Classify
    const classification = this.classifier.classify(sanitized);

    // Stage 4: Create cognitive process
    const process = await this.processManager.createProcess(
      sanitized, classification
    );

    // Stage 5: Think (async, non-blocking)
    try {
      const response = await this.pipeline.think(process, classification.tier);

      // Stage 6: Respond
      await this.responder.sendResponse(email, response, this.botAddress);

      // Stage 7: Reconcile (completed)
      await this.reconciler.reconcile(process, 'completed');
    } catch (err) {
      // Suspend process on failure (will retry)
      await this.reconciler.reconcile(process, 'suspended');
      this.logger.error('Cognitive processing failed', { processId: process.processId, err });
    }
  }
}
```

## Backpressure & Queue Management

```typescript
export class MailQueue {
  private pending: PriorityQueue<QueuedMail>;
  private processing = new Map<string, AbortController>();
  private maxConcurrent = 3; // One per triadic stream

  async enqueue(email: EmailMessage, priority: number): Promise<void> {
    this.pending.enqueue({ email, priority, enqueuedAt: Date.now() });
    this.drain();
  }

  private async drain(): Promise<void> {
    while (this.processing.size < this.maxConcurrent && !this.pending.isEmpty()) {
      const item = this.pending.dequeue();
      const controller = new AbortController();
      this.processing.set(item.email.messageId, controller);

      this.processWithTimeout(item, controller.signal)
        .finally(() => {
          this.processing.delete(item.email.messageId);
          this.drain(); // Process next
        });
    }
  }
}
```

## Cognitive Tier Decision Table

| Signal | Priority | Tier | Latency Target |
|--------|----------|------|----------------|
| Priority: urgent header | 8-9 | BASIC | < 5s |
| Thread reply | 6-7 | SYS6 | < 30s |
| New conversation | 5 | SYS6 | < 30s |
| Deep thread (>3 refs) | 5-6 | FULL | < 120s |
| Low priority / batch | 1-3 | FULL | best-effort |
| Auto-detected complex | varies | ADAPTIVE | varies |

## Safety Rules

- NEVER store raw email content in logs (PII protection)
- Sanitize ALL email headers before cognitive processing
- Rate-limit responses per sender (prevent abuse)
- Set response timeout per tier (kill runaway LLM calls)
- Validate SMTP response before sending (no open relay)
- Use `inReplyTo` / `References` headers for proper threading

## References

- Read [../../deep-tree-echo-orchestrator/src/](../../deep-tree-echo-orchestrator/src/) for existing orchestrator code
- Read [../../dovecho-core/src/dove9/integration/](../../dovecho-core/src/dove9/integration/) for C-level mail bridge APIs
- Read [../../deep-tree-echo-core/src/](../../deep-tree-echo-core/src/) for LLM/memory/persona TypeScript implementations

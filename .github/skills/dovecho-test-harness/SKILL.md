---
name: dovecho-test-harness
description: 'Test the full cognitive mail pipeline without requiring a live Dovecot server, real SMTP, or actual LLM inference. USE FOR: writing unit/integration/e2e tests for dovecho-core C kernel, NAPI bridge, mail pipeline stages, autonomous agent behavior, Sys6 cycle determinism, mock LMTP/SMTP, simulated multi-turn conversations, cognitive process assertions, performance/load testing. DO NOT USE FOR: C plugin hooks (use dovecho-c-module), production mail processing (use dovecho-mail-pipeline), self-initiated behavior design (use dovecho-autonomous-agent).'
---

# Dovecho Test Harness

Test the entire cognitive mail server stack — from the C kernel through the NAPI bridge to the TypeScript orchestrator — without a live Dovecot, real SMTP, or actual LLM calls. The harness makes deterministic testing possible for what is inherently a non-deterministic cognitive system.

## When to Use

- Writing tests for ANY part of the dovecho stack
- Mocking LMTP intake and SMTP delivery
- Simulating multi-turn email conversations
- Asserting on Sys6 cycle state transitions (deterministic stepping)
- Verifying cognitive pipeline stage outputs
- Testing autonomous behavior (dream states, proactive outreach)
- Performance and load testing under simulated mail volume
- Testing the C↔TypeScript NAPI boundary
- End-to-end integration: inject email → verify response sent

## Test Pyramid for Dovecho

```
                 ┌─────────┐
                 │  E2E    │  Full pipeline: LMTP → think → SMTP
                ┌┴─────────┴┐
                │ Integration │  Multi-stage: classify → process → respond
              ┌─┴────────────┴─┐
              │    Component    │  Single stage isolation (sanitizer, classifier, etc.)
            ┌─┴────────────────┴─┐
            │       Unit          │  C kernel functions, TS utility functions
          ┌─┴──────────────────────┴─┐
          │      C Kernel (CTest)     │  dove9 C library tests via CMake/CTest
          └───────────────────────────┘
```

## Layer 1: C Kernel Tests (CTest)

Already built — 27 tests in dovecho-core/src/dove9/CMakeLists.txt. Use CMake presets:

```bash
# Build and run C kernel tests
cmake --preset dev
cmake --build build-dev -j8
ctest --test-dir build-dev --output-on-failure
```

For new C test files, follow the existing pattern:

```c
/* dovecho-core/src/dove9/tests/test_new_feature.c */
#include "dove9-system.h"
#include <assert.h>
#include <stdio.h>

static void test_specific_behavior(void) {
    struct dove9_system sys;
    dove9_system_init(&sys, NULL);

    /* Exercise the behavior */
    int result = dove9_some_function(&sys, input);

    /* Assert */
    assert(result == expected);

    dove9_system_cleanup(&sys);
}

int main(void) {
    test_specific_behavior();
    printf("PASS: test_new_feature\n");
    return 0;
}
```

Register in CMakeLists.txt:

```cmake
dove9_add_test(test_new_feature tests/test_new_feature.c)
```

## Layer 2: Mock Infrastructure (TypeScript)

### Mock LMTP Server

Accepts mail delivery requests and queues them for inspection.

```typescript
// tests/mocks/mock-lmtp-server.ts

import { EventEmitter } from 'events';

export interface DeliveredMessage {
  from: string;
  to: string[];
  subject: string;
  body: string;
  headers: Record<string, string>;
  receivedAt: number;
}

export class MockLMTPServer extends EventEmitter {
  private deliveries: DeliveredMessage[] = [];
  private shouldReject = false;

  /** Simulate an incoming email delivery */
  async deliver(message: Partial<DeliveredMessage>): Promise<void> {
    if (this.shouldReject) {
      throw new Error('451 Temporary failure');
    }

    const full: DeliveredMessage = {
      from: message.from ?? 'test@example.com',
      to: message.to ?? ['bot@dovecho.local'],
      subject: message.subject ?? 'Test Subject',
      body: message.body ?? 'Test body',
      headers: message.headers ?? {},
      receivedAt: Date.now(),
    };

    this.deliveries.push(full);
    this.emit('delivery', full);
  }

  /** Get all delivered messages */
  getDeliveries(): DeliveredMessage[] {
    return [...this.deliveries];
  }

  /** Get last N deliveries */
  getLastDeliveries(n: number): DeliveredMessage[] {
    return this.deliveries.slice(-n);
  }

  /** Set rejection mode for testing error paths */
  setRejectMode(reject: boolean): void {
    this.shouldReject = reject;
  }

  /** Reset state between tests */
  reset(): void {
    this.deliveries = [];
    this.shouldReject = false;
  }
}
```

### Mock SMTP Sender

Captures outbound emails instead of actually sending them.

```typescript
// tests/mocks/mock-smtp-sender.ts

export interface SentMessage {
  from: string;
  to: string;
  subject: string;
  body: string;
  inReplyTo?: string;
  sentAt: number;
}

export class MockSMTPSender {
  private sent: SentMessage[] = [];
  private failNext = false;

  async send(message: Omit<SentMessage, 'sentAt'>): Promise<void> {
    if (this.failNext) {
      this.failNext = false;
      throw new Error('Connection refused');
    }
    this.sent.push({ ...message, sentAt: Date.now() });
  }

  getSent(): SentMessage[] { return [...this.sent]; }
  getLastSent(): SentMessage | undefined { return this.sent.at(-1); }

  /** Make next send() fail */
  failOnNextSend(): void { this.failNext = true; }

  reset(): void {
    this.sent = [];
    this.failNext = false;
  }
}
```

### Mock LLM Service

Returns deterministic responses for testing. Supports canned responses and response latency simulation.

```typescript
// tests/mocks/mock-llm-service.ts

export class MockLLMService {
  private cannedResponses: Map<string, string> = new Map();
  private defaultResponse = 'This is a mock LLM response.';
  private callLog: Array<{ prompt: string; response: string; latency: number }> = [];
  private latencyMs = 0;

  /** Register a canned response for a prompt pattern */
  whenPromptContains(pattern: string, response: string): this {
    this.cannedResponses.set(pattern, response);
    return this;
  }

  /** Set simulated latency */
  withLatency(ms: number): this {
    this.latencyMs = ms;
    return this;
  }

  async generate(prompt: string): Promise<string> {
    // Simulate latency
    if (this.latencyMs > 0) {
      await new Promise(r => setTimeout(r, this.latencyMs));
    }

    // Find matching canned response
    let response = this.defaultResponse;
    for (const [pattern, canned] of this.cannedResponses) {
      if (prompt.includes(pattern)) {
        response = canned;
        break;
      }
    }

    this.callLog.push({ prompt, response, latency: this.latencyMs });
    return response;
  }

  getCallLog() { return [...this.callLog]; }
  getCallCount() { return this.callLog.length; }
  reset(): void {
    this.callLog = [];
    this.cannedResponses.clear();
  }
}
```

### Mock Memory Store

In-memory RAG store that supports all query patterns without vector DB.

```typescript
// tests/mocks/mock-memory-store.ts

export interface MemoryEntry {
  id: string;
  content: string;
  attention: number;
  createdAt: number;
  associations: string[];
}

export class MockMemoryStore {
  private memories: Map<string, MemoryEntry> = new Map();

  async store(content: string, attention = 0.5): Promise<string> {
    const id = `mem-${this.memories.size + 1}`;
    this.memories.set(id, {
      id, content, attention, createdAt: Date.now(), associations: [],
    });
    return id;
  }

  async retrieveRelevant(query: string, k: number): Promise<MemoryEntry[]> {
    // Simple keyword matching (no embeddings needed for tests)
    const queryWords = query.toLowerCase().split(/\s+/);
    return [...this.memories.values()]
      .filter(m => queryWords.some(w => m.content.toLowerCase().includes(w)))
      .sort((a, b) => b.attention - a.attention)
      .slice(0, k);
  }

  async updateAttention(id: string, attention: number): Promise<void> {
    const mem = this.memories.get(id);
    if (mem) mem.attention = attention;
  }

  async findDecayingMemories(threshold: number): Promise<MemoryEntry[]> {
    return [...this.memories.values()].filter(m => m.attention < threshold);
  }

  async archiveMemory(id: string): Promise<void> {
    this.memories.delete(id);
  }

  getAll(): MemoryEntry[] { return [...this.memories.values()]; }
  getCount(): number { return this.memories.size; }

  reset(): void { this.memories.clear(); }
}
```

## Layer 3: Deterministic Sys6 Cycle Testing

The C scheduler supports non-timer mode where you manually advance steps. This is essential for deterministic tests.

```typescript
// tests/helpers/deterministic-scheduler.ts

export class DeterministicScheduler {
  private bridge: Dove9SystemBridge;

  constructor(bridge: Dove9SystemBridge) {
    this.bridge = bridge;
    // CRITICAL: start in non-timer mode (manual stepping)
    this.bridge.startScheduler({ timerMode: false });
  }

  /** Advance exactly N steps and collect events */
  async advanceSteps(n: number): Promise<SchedulerEvent[]> {
    const events: SchedulerEvent[] = [];
    for (let i = 0; i < n; i++) {
      const event = await this.bridge.advanceStep();
      if (event) events.push(event);
    }
    return events;
  }

  /** Advance to next grand cycle boundary */
  async advanceToGrandCycleBoundary(): Promise<SchedulerEvent[]> {
    const events: SchedulerEvent[] = [];
    const state = await this.bridge.getSchedulerState();
    const stepsRemaining = GRAND_CYCLE_LENGTH - (state.current_step % GRAND_CYCLE_LENGTH);
    return this.advanceSteps(stepsRemaining);
  }

  /** Advance to next idle step (no pending processes) */
  async advanceToIdle(): Promise<SchedulerEvent[]> {
    const events: SchedulerEvent[] = [];
    for (let i = 0; i < GRAND_CYCLE_LENGTH; i++) {
      const event = await this.bridge.advanceStep();
      if (event) events.push(event);
      const pending = await this.bridge.getPendingCount();
      if (pending === 0) break;
    }
    return events;
  }

  /** Get exact cycle position for assertions */
  async getPosition(): Promise<CyclePositions> {
    return this.bridge.getCyclePositions();
  }
}
```

## Layer 4: Conversation Simulator

Simulate multi-turn email conversations for integration testing.

```typescript
// tests/helpers/conversation-simulator.ts

export class ConversationSimulator {
  private turns: ConversationTurn[] = [];

  constructor(
    private lmtp: MockLMTPServer,
    private smtp: MockSMTPSender,
    private pipeline: CognitivePipeline,
  ) {}

  /** Define a conversation script and execute it */
  async playScript(script: ConversationScript): Promise<ConversationResult> {
    const results: ConversationTurn[] = [];

    for (const turn of script.turns) {
      // Deliver the human's message
      await this.lmtp.deliver({
        from: turn.from,
        to: [script.botAddress],
        subject: turn.subject,
        body: turn.body,
      });

      // Let the pipeline process it
      // (In real system this happens via event; in test we call directly)
      const lastDelivery = this.lmtp.getLastDeliveries(1)[0];
      await this.pipeline.processIncoming(lastDelivery);

      // Capture the bot's response
      const response = this.smtp.getLastSent();

      results.push({
        human: turn.body,
        bot: response?.body ?? '[NO RESPONSE]',
        turnNumber: results.length + 1,
      });
    }

    return { turns: results, totalTurns: results.length };
  }
}

export interface ConversationScript {
  botAddress: string;
  turns: Array<{
    from: string;
    subject: string;
    body: string;
  }>;
}
```

## Layer 5: Test Fixture Builder

Composable fixture that wires up all mocks into a ready-to-test pipeline.

```typescript
// tests/helpers/dovecho-test-fixture.ts

export class DovechoTestFixture {
  readonly lmtp = new MockLMTPServer();
  readonly smtp = new MockSMTPSender();
  readonly llm = new MockLLMService();
  readonly memory = new MockMemoryStore();
  readonly scheduler: DeterministicScheduler;
  readonly pipeline: CognitivePipeline;
  readonly conversation: ConversationSimulator;

  private constructor(bridge: Dove9SystemBridge) {
    this.scheduler = new DeterministicScheduler(bridge);
    this.pipeline = new CognitivePipeline({
      llm: this.llm,
      memory: this.memory,
      sender: this.smtp,
    });
    this.conversation = new ConversationSimulator(
      this.lmtp, this.smtp, this.pipeline,
    );
  }

  static async create(): Promise<DovechoTestFixture> {
    // Initialize C kernel through NAPI bridge
    const bridge = await Dove9SystemBridge.create({ testMode: true });
    return new DovechoTestFixture(bridge);
  }

  /** Reset all state between tests */
  reset(): void {
    this.lmtp.reset();
    this.smtp.reset();
    this.llm.reset();
    this.memory.reset();
  }

  /** Teardown — release native resources */
  async destroy(): Promise<void> {
    // Cleanup NAPI bridge / C allocations
  }
}
```

## Example Tests

### Unit Test: Mail Classifier

```typescript
// tests/unit/mail-classifier.test.ts

describe('MailClassifier', () => {
  it('classifies high-priority mail to SYS6 tier', () => {
    const classifier = new MailClassifier();
    const result = classifier.classify({
      from: 'boss@company.com',
      subject: 'URGENT: Server Down',
      body: 'The production server is not responding.',
      headers: { 'X-Priority': '1' },
    });
    expect(result.tier).toBe('SYS6');
    expect(result.priority).toBeGreaterThanOrEqual(7);
  });

  it('classifies newsletters as BASIC tier', () => {
    const classifier = new MailClassifier();
    const result = classifier.classify({
      from: 'noreply@newsletter.example.com',
      subject: 'Weekly Digest #47',
      body: 'Here are this weeks top stories...',
      headers: { 'List-Unsubscribe': '<mailto:unsub@example.com>' },
    });
    expect(result.tier).toBe('BASIC');
    expect(result.priority).toBeLessThanOrEqual(3);
  });
});
```

### Integration Test: Full Pipeline

```typescript
// tests/integration/pipeline.test.ts

describe('CognitivePipeline', () => {
  let fixture: DovechoTestFixture;

  beforeEach(async () => {
    fixture = await DovechoTestFixture.create();
    fixture.llm.whenPromptContains('hello', 'Hello! How can I help you?');
  });

  afterEach(async () => {
    fixture.reset();
    await fixture.destroy();
  });

  it('processes incoming mail and sends response', async () => {
    await fixture.lmtp.deliver({
      from: 'user@example.com',
      subject: 'Hello',
      body: 'Hey, just saying hello!',
    });

    const deliveries = fixture.lmtp.getDeliveries();
    await fixture.pipeline.processIncoming(deliveries[0]);

    const sent = fixture.smtp.getSent();
    expect(sent).toHaveLength(1);
    expect(sent[0].to).toBe('user@example.com');
    expect(sent[0].body).toContain('Hello');
  });
});
```

### Sys6 Cycle Determinism Test

```typescript
// tests/integration/sys6-determinism.test.ts

describe('Sys6 Deterministic Stepping', () => {
  let fixture: DovechoTestFixture;

  beforeEach(async () => {
    fixture = await DovechoTestFixture.create();
  });

  it('completes a full grand cycle in exactly 60 steps', async () => {
    const events = await fixture.scheduler.advanceSteps(60);

    const grandBoundary = events.filter(
      e => e.type === 'GRAND_CYCLE_BOUNDARY'
    );
    expect(grandBoundary).toHaveLength(1);
  });

  it('fires Sys6 boundary every 30 steps', async () => {
    const events = await fixture.scheduler.advanceSteps(60);

    const sys6Boundaries = events.filter(
      e => e.type === 'SYS6_CYCLE_BOUNDARY'
    );
    expect(sys6Boundaries).toHaveLength(2); // Steps 30 and 60
  });

  it('fires Dove9 boundary every 12 steps', async () => {
    const events = await fixture.scheduler.advanceSteps(60);

    const dove9Boundaries = events.filter(
      e => e.type === 'DOVE9_CYCLE_BOUNDARY'
    );
    expect(dove9Boundaries).toHaveLength(5); // Steps 12, 24, 36, 48, 60
  });
});
```

### Autonomous Agent Test

```typescript
// tests/integration/autonomous.test.ts

describe('Autonomous Agent', () => {
  let fixture: DovechoTestFixture;

  beforeEach(async () => {
    fixture = await DovechoTestFixture.create();
    fixture.llm.whenPromptContains('[Internal]', 'I am thinking about things.');
  });

  it('generates internal monologue during idle steps', async () => {
    // No mail delivered → all steps are idle
    await fixture.scheduler.advanceSteps(60);

    // Check that internal thoughts were generated
    const sent = fixture.smtp.getSent();
    const internalMsgs = sent.filter(s => s.to === 'bot@dovecho.local');
    expect(internalMsgs.length).toBeGreaterThan(0);
  });

  it('wakes from dream state when mail arrives', async () => {
    // Advance 5 grand cycles to enter dream state
    await fixture.scheduler.advanceSteps(300);

    // Now deliver mail
    await fixture.lmtp.deliver({
      from: 'user@example.com',
      subject: 'Wake up!',
      body: 'Are you there?',
    });

    // Process
    const delivery = fixture.lmtp.getLastDeliveries(1)[0];
    await fixture.pipeline.processIncoming(delivery);

    // Should get a response (not stuck in dream)
    const sent = fixture.smtp.getSent();
    const responses = sent.filter(s => s.to === 'user@example.com');
    expect(responses).toHaveLength(1);
  });
});
```

### Multi-Turn Conversation Test

```typescript
// tests/e2e/conversation.test.ts

describe('Multi-Turn Conversation', () => {
  let fixture: DovechoTestFixture;

  beforeEach(async () => {
    fixture = await DovechoTestFixture.create();
    fixture.llm
      .whenPromptContains('hello', 'Hi there! Whats on your mind?')
      .whenPromptContains('meaning of life', 'Thats a deep question. Let me think...');
  });

  it('handles 3-turn conversation with memory', async () => {
    const result = await fixture.conversation.playScript({
      botAddress: 'bot@dovecho.local',
      turns: [
        { from: 'alice@example.com', subject: 'Hi', body: 'hello!' },
        { from: 'alice@example.com', subject: 'Re: Hi', body: 'Whats the meaning of life?' },
        { from: 'alice@example.com', subject: 'Re: Hi', body: 'Thanks for thinking about it' },
      ],
    });

    expect(result.totalTurns).toBe(3);
    expect(result.turns[0].bot).toContain('Hi there');
    expect(result.turns[1].bot).toContain('deep question');

    // Memory should have stored the conversation
    const memories = fixture.memory.getAll();
    expect(memories.length).toBeGreaterThan(0);
  });
});
```

## Running Tests

```bash
# C kernel tests only
cmake --preset dev && cmake --build build-dev -j8 && ctest --test-dir build-dev

# TypeScript tests (all layers)
pnpm test

# Specific test layer
pnpm test -- --testPathPattern="tests/unit"
pnpm test -- --testPathPattern="tests/integration"
pnpm test -- --testPathPattern="tests/e2e"

# With coverage
pnpm test -- --coverage

# Watch mode during development
pnpm test -- --watch --testPathPattern="tests/integration/pipeline"
```

## Safety Rules

- Mock LLM MUST be used in all tests — never call real LLM providers
- Mock SMTP MUST be used — never send real emails from tests
- C kernel tests run in isolated processes (CTest handles this)
- Reset ALL mock state between tests (use fixture.reset())
- Destroy native resources after each suite (use fixture.destroy())
- Tests must be deterministic: no `Date.now()` without mocking, no real timers
- Use DeterministicScheduler (manual stepping) — never real scheduler timers in tests

## References

- [../../dovecho-core/src/dove9/CMakeLists.txt](../../dovecho-core/src/dove9/CMakeLists.txt) — C kernel test registration
- [../../dovecho-core/src/dove9/integration/dove9-sys6-mail-scheduler.h](../../dovecho-core/src/dove9/integration/dove9-sys6-mail-scheduler.h) — Scheduler constants and event types
- [../../jest.config.js](../../jest.config.js) — Root Jest configuration

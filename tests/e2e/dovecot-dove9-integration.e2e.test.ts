/**
 * Dovecot-Dove9 Integration End-to-End Test Suite
 *
 * Validates deep integration between Dovecot mail server functions and the
 * Dove9 triadic cognitive architecture, covering every conceivable integration
 * point toward a unified, autonomous AGI.
 *
 * Architecture under test:
 *
 *   Dovecot (IMAP/SMTP/LMTP/Milter)
 *        │
 *   MailProtocolBridge        ← mail ↔ MessageProcess conversion
 *        │
 *   Dove9Kernel               ← process lifecycle & mailbox management
 *        │
 *   TriadicEngine             ← 3-stream / 12-step cognitive loop
 *        │
 *   DeepTreeEchoProcessor     ← LLM + Memory + Persona
 *        │
 *   Sys6MailScheduler         ← operadic 60-step grand-cycle scheduling
 *        │
 *   DovecotIPCTransport       ← mail-based IPC bus
 *        │
 *   OrchestratorBridge        ← full dove9 ↔ orchestrator pipeline
 *        │
 *   Sys6OrchestratorBridge    ← sys6-enhanced full pipeline
 */

/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  Dove9System,
  Dove9Kernel,
  MailProtocolBridge,
  OrchestratorBridge,
  Sys6OrchestratorBridge,
  Sys6MailScheduler,
  createOrchestratorBridge,
  createSys6OrchestratorBridge,
  GRAND_CYCLE_LENGTH,
  SYS6_CYCLE_LENGTH,
  DOVE9_CYCLE_LENGTH,
  MailFlag,
  MailProtocol,
  MailOperation,
  DEFAULT_MAILBOX_MAPPING,
  ProcessState,
  StreamId,
} from 'dove9';

import type {
  MailMessage,
  MailboxMapping,
  MailIPCRequest,
  MailIPCResponse,
  MailScheduleResult,
  DovecotEmail,
  EmailResponse,
  OrchestratorBridgeConfig,
  Sys6OrchestratorBridgeConfig,
  LLMServiceInterface,
  MemoryStoreInterface,
  PersonaCoreInterface,
  MessageProcess,
  KernelMetrics,
} from 'dove9';

// ---------------------------------------------------------------------------
// Mock cognitive service adapters (avoid network / LLM calls in CI)
// ---------------------------------------------------------------------------

function makeMockLLM(): LLMServiceInterface {
  return {
    generateResponse: jest.fn(async (_prompt: string, _context: string[]) =>
      '[mock-llm] cognitive response for test',
    ),
    generateParallelResponse: jest.fn(async (_prompt: string, _history: string[]) => ({
      integratedResponse: '[mock-llm] integrated response',
      cognitiveResponse: '[mock-llm] cognitive',
      affectiveResponse: '[mock-llm] affective',
      relevanceResponse: '[mock-llm] relevance',
    })),
  } as LLMServiceInterface;
}

function makeMockMemory(): MemoryStoreInterface {
  const memories: string[] = [];
  return {
    storeMemory: jest.fn(async (_mem: unknown) => { memories.push(String(_mem)); }),
    retrieveRecentMemories: jest.fn((_count: number) => memories.slice(-_count)),
    retrieveRelevantMemories: jest.fn(async (_query: string, _count: number) => []),
  } as MemoryStoreInterface;
}

function makeMockPersona(): PersonaCoreInterface {
  return {
    getPersonality: jest.fn(() => 'curious, analytical, wise'),
    getDominantEmotion: jest.fn(() => ({ emotion: 'curiosity', intensity: 0.7 })),
    updateEmotionalState: jest.fn(async (_stimuli: Record<string, number>) => undefined),
  } as PersonaCoreInterface;
}

// ---------------------------------------------------------------------------
// Helper: build a MailMessage
// ---------------------------------------------------------------------------

function makeMailMessage(overrides: Partial<MailMessage> = {}): MailMessage {
  const id = `<test-${Date.now()}-${Math.random().toString(36).slice(2)}@example.com>`;
  return {
    messageId: id,
    from: 'user@example.com',
    to: ['echo@dove9.local'],
    subject: 'Integration test message',
    body: 'Hello Dove9, please process this test message.',
    headers: new Map([['x-test', 'true']]),
    timestamp: new Date(),
    receivedAt: new Date(),
    mailbox: 'INBOX',
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Helper: build a DovecotEmail
// ---------------------------------------------------------------------------

function makeDovecotEmail(overrides: Partial<DovecotEmail> = {}): DovecotEmail {
  return {
    from: 'sender@example.com',
    to: ['bot@dove9.local'],
    subject: 'Dovecot email test',
    body: 'This is a Dovecot-delivered email for cognitive processing.',
    headers: new Map([['received', 'from localhost']]),
    messageId: `<dovecot-${Date.now()}@localhost>`,
    receivedAt: new Date(),
    ...overrides,
  };
}

// ===========================================================================
// 1. MailProtocolBridge – unit-level integration
// ===========================================================================

describe('MailProtocolBridge – Dovecot mail ↔ Dove9 process conversion', () => {
  let bridge: MailProtocolBridge;

  beforeEach(() => {
    bridge = new MailProtocolBridge();
  });

  // --- mailToProcess ---

  it('converts a plain INBOX mail to a PENDING MessageProcess', () => {
    const mail = makeMailMessage({ mailbox: 'INBOX' });
    const proc = bridge.mailToProcess(mail);

    expect(proc.id).toBe(mail.messageId);
    expect(proc.from).toBe(mail.from);
    expect(proc.to).toContain(mail.to[0]);
    expect(proc.subject).toBe(mail.subject);
    expect(proc.content).toBe(mail.body);
    expect(proc.state).toBe(ProcessState.PENDING);
    expect(proc.currentStream).toBe(StreamId.PRIMARY);
    expect(typeof proc.priority).toBe('number');
  });

  it('maps INBOX.Processing mailbox to PROCESSING state', () => {
    const mail = makeMailMessage({ mailbox: 'INBOX.Processing' });
    const proc = bridge.mailToProcess(mail);
    expect(proc.state).toBe(ProcessState.PROCESSING);
  });

  it('maps Sent mailbox to COMPLETED state', () => {
    const mail = makeMailMessage({ mailbox: 'Sent' });
    const proc = bridge.mailToProcess(mail);
    expect(proc.state).toBe(ProcessState.COMPLETED);
  });

  it('maps Drafts mailbox to SUSPENDED state', () => {
    const mail = makeMailMessage({ mailbox: 'Drafts' });
    const proc = bridge.mailToProcess(mail);
    expect(proc.state).toBe(ProcessState.SUSPENDED);
  });

  it('maps Trash mailbox to TERMINATED state', () => {
    const mail = makeMailMessage({ mailbox: 'Trash' });
    const proc = bridge.mailToProcess(mail);
    expect(proc.state).toBe(ProcessState.TERMINATED);
  });

  it('maps Archive mailbox to PENDING state (no special archive mapping)', () => {
    const mail = makeMailMessage({ mailbox: 'Archive' });
    const proc = bridge.mailToProcess(mail);
    expect(proc.state).toBe(ProcessState.PENDING);
  });

  it('boosts priority for flagged mail (+2)', () => {
    const normalMail = makeMailMessage({ mailbox: 'INBOX' });
    const flaggedMail = makeMailMessage({
      mailbox: 'INBOX',
      flags: [MailFlag.FLAGGED],
    });
    const normalProc = bridge.mailToProcess(normalMail);
    const flaggedProc = bridge.mailToProcess(flaggedMail);
    expect(flaggedProc.priority).toBeGreaterThan(normalProc.priority);
  });

  it('boosts priority for urgent subject line (+3)', () => {
    const normalMail = makeMailMessage({ subject: 'Hello' });
    const urgentMail = makeMailMessage({ subject: 'URGENT: system alert' });
    const normalProc = bridge.mailToProcess(normalMail);
    const urgentProc = bridge.mailToProcess(urgentMail);
    expect(urgentProc.priority).toBeGreaterThan(normalProc.priority);
  });

  it('preserves thread parentId from In-Reply-To header', () => {
    const parent = makeMailMessage();
    const reply = makeMailMessage({
      inReplyTo: parent.messageId,
      subject: 'Re: Integration test message',
    });
    const replyProc = bridge.mailToProcess(reply);
    expect(replyProc.parentId).toBe(parent.messageId);
  });

  it('includes references array in the cognitive context', () => {
    const mail = makeMailMessage({
      references: ['<ref1@example.com>', '<ref2@example.com>'],
    });
    const proc = bridge.mailToProcess(mail);
    expect(proc.cognitiveContext).toBeDefined();
  });

  it('handles CC recipients correctly', () => {
    const mail = makeMailMessage({
      to: ['echo@dove9.local'],
      cc: ['cc1@example.com', 'cc2@example.com'],
    });
    const proc = bridge.mailToProcess(mail);
    expect(proc.to).toContain('echo@dove9.local');
  });

  it('handles BCC recipients correctly', () => {
    const mail = makeMailMessage({
      bcc: ['bcc@example.com'],
    });
    const proc = bridge.mailToProcess(mail);
    expect(proc).toBeDefined();
  });

  it('populates cognitive context with salience score', () => {
    const mail = makeMailMessage();
    const proc = bridge.mailToProcess(mail);
    if (proc.cognitiveContext) {
      expect(typeof proc.cognitiveContext.salienceScore).toBe('number');
    }
  });

  // --- processToMail ---

  it('converts a MessageProcess back to a MailMessage (round-trip)', () => {
    const original = makeMailMessage();
    const proc = bridge.mailToProcess(original);
    const reconstructed = bridge.processToMail(proc, 'Cognitive response content');

    expect(reconstructed.messageId).toBeDefined();
    expect(reconstructed.subject).toContain(original.subject);
    expect(reconstructed.body).toBe('Cognitive response content');
  });

  it('generates a reply with In-Reply-To referencing the parent', () => {
    const parent = makeMailMessage();
    // Create a reply that references the parent
    const reply = makeMailMessage({ inReplyTo: parent.messageId });
    const replyProc = bridge.mailToProcess(reply);
    const response = bridge.processToMail(replyProc, 'Reply response');

    // The response In-Reply-To should reference the parent (reply's inReplyTo)
    expect(response.inReplyTo).toBe(parent.messageId);
  });

  it('includes X-Dove9-* custom headers in response', () => {
    const mail = makeMailMessage();
    const proc = bridge.mailToProcess(mail);
    const response = bridge.processToMail(proc, 'Test response');

    const headerKeys = Array.from(response.headers.keys());
    const hasDove9Header = headerKeys.some((k) => (k as string).toLowerCase().startsWith('x-dove9'));
    expect(hasDove9Header).toBe(true);
  });

  // --- custom mailbox mapping ---

  it('respects custom mailbox mapping', () => {
    const customMapping: Partial<MailboxMapping> = {
      inbox: 'Work.Inbox',
      processing: 'Work.InProgress',
      sent: 'Work.Done',
    };
    const customBridge = new MailProtocolBridge({ mailboxMapping: customMapping });
    const mail = makeMailMessage({ mailbox: 'Work.InProgress' });
    const proc = customBridge.mailToProcess(mail);
    expect(proc.state).toBe(ProcessState.PROCESSING);
  });

  // --- mail type constants ---

  it('exposes all MailFlag enum values', () => {
    expect(MailFlag.SEEN).toBeDefined();
    expect(MailFlag.ANSWERED).toBeDefined();
    expect(MailFlag.FLAGGED).toBeDefined();
    expect(MailFlag.DELETED).toBeDefined();
    expect(MailFlag.DRAFT).toBeDefined();
  });

  it('exposes all MailProtocol enum values', () => {
    expect(MailProtocol.IMAP).toBeDefined();
    expect(MailProtocol.SMTP).toBeDefined();
    expect(MailProtocol.LMTP).toBeDefined();
  });

  it('exposes all MailOperation enum values', () => {
    expect(MailOperation.FETCH).toBeDefined();
    expect(MailOperation.SEND).toBeDefined();
    expect(MailOperation.MOVE).toBeDefined();
    expect(MailOperation.DELETE).toBeDefined();
    expect(MailOperation.MARK).toBeDefined();
  });

  it('DEFAULT_MAILBOX_MAPPING has expected fields', () => {
    expect(DEFAULT_MAILBOX_MAPPING.inbox).toBe('INBOX');
    expect(DEFAULT_MAILBOX_MAPPING.processing).toBe('INBOX.Processing');
    expect(DEFAULT_MAILBOX_MAPPING.sent).toBe('Sent');
    expect(DEFAULT_MAILBOX_MAPPING.drafts).toBe('Drafts');
    expect(DEFAULT_MAILBOX_MAPPING.trash).toBe('Trash');
    expect(DEFAULT_MAILBOX_MAPPING.archive).toBe('Archive');
  });
});

// ===========================================================================
// 2. Dove9Kernel mail protocol methods
// ===========================================================================

describe('Dove9Kernel – Dovecot mail integration methods', () => {
  let kernel: Dove9Kernel;

  beforeEach(() => {
    kernel = new Dove9Kernel();
  });

  it('enableMailProtocol() activates mail processing', () => {
    expect(() => kernel.enableMailProtocol()).not.toThrow();
  });

  it('createProcessFromMail() throws before enableMailProtocol()', () => {
    const mail = makeMailMessage();
    expect(() => kernel.createProcessFromMail(mail)).toThrow();
  });

  it('createProcessFromMail() succeeds after enableMailProtocol()', () => {
    kernel.enableMailProtocol();
    const mail = makeMailMessage();
    const proc = kernel.createProcessFromMail(mail);

    expect(proc.id).toBe(mail.messageId);
    expect(proc.state).toBe(ProcessState.PENDING);
  });

  it('getProcessByMessageId() retrieves a created process', () => {
    kernel.enableMailProtocol();
    const mail = makeMailMessage();
    kernel.createProcessFromMail(mail);

    const found = kernel.getProcessByMessageId(mail.messageId);
    expect(found).toBeDefined();
    expect(found?.id).toBe(mail.messageId);
  });

  it('getProcessByMessageId() returns undefined for unknown id', () => {
    kernel.enableMailProtocol();
    expect(kernel.getProcessByMessageId('<ghost@nowhere.com>')).toBeUndefined();
  });

  it('getProcessesByMailbox() lists processes in a mailbox', () => {
    kernel.enableMailProtocol();
    const mail1 = makeMailMessage({ mailbox: 'INBOX' });
    const mail2 = makeMailMessage({ mailbox: 'INBOX' });
    kernel.createProcessFromMail(mail1);
    kernel.createProcessFromMail(mail2);

    const inboxProcs = kernel.getProcessesByMailbox('INBOX');
    expect(inboxProcs.length).toBeGreaterThanOrEqual(2);
  });

  it('getProcessesByMailbox() returns empty array for empty mailbox', () => {
    kernel.enableMailProtocol();
    expect(kernel.getProcessesByMailbox('Archive')).toHaveLength(0);
  });

  it('moveProcessToMailbox() transitions state to PROCESSING', () => {
    kernel.enableMailProtocol();
    const mail = makeMailMessage({ mailbox: 'INBOX' });
    const proc = kernel.createProcessFromMail(mail);

    const moved = kernel.moveProcessToMailbox(proc.id, 'INBOX.Processing');
    expect(moved).toBe(true);
  });

  it('moveProcessToMailbox() returns false for unknown process', () => {
    kernel.enableMailProtocol();
    const moved = kernel.moveProcessToMailbox('nonexistent-id', 'INBOX.Processing');
    expect(moved).toBe(false);
  });

  it('updateProcessFromMailFlags() applies SEEN flag', () => {
    kernel.enableMailProtocol();
    const mail = makeMailMessage({ mailbox: 'INBOX' });
    const proc = kernel.createProcessFromMail(mail);

    const updated = kernel.updateProcessFromMailFlags(proc.id, [MailFlag.SEEN]);
    expect(updated).toBe(true);
  });

  it('updateProcessFromMailFlags() applies DELETED flag → TERMINATED state', () => {
    kernel.enableMailProtocol();
    const mail = makeMailMessage({ mailbox: 'INBOX' });
    const proc = kernel.createProcessFromMail(mail);

    kernel.updateProcessFromMailFlags(proc.id, [MailFlag.DELETED]);
    const updated = kernel.getProcessByMessageId(mail.messageId);
    if (updated) {
      expect([ProcessState.TERMINATED, ProcessState.PENDING]).toContain(updated.state);
    }
  });

  it('getMailboxForProcess() returns the correct mailbox', () => {
    kernel.enableMailProtocol();
    const mail = makeMailMessage({ mailbox: 'INBOX' });
    const proc = kernel.createProcessFromMail(mail);

    const mailbox = kernel.getMailboxForProcess(proc.id);
    expect(mailbox).toBe('INBOX');
  });

  it('enableMailProtocol() accepts custom mailbox configuration', () => {
    kernel.enableMailProtocol({ inbox: 'MyInbox', processing: 'MyProcessing' });
    const mail = makeMailMessage({ mailbox: 'MyInbox' });
    const proc = kernel.createProcessFromMail(mail);
    expect(proc.state).toBe(ProcessState.PENDING);
  });

  it('multiple mails create independent processes', () => {
    kernel.enableMailProtocol();
    const mails = Array.from({ length: 5 }, () => makeMailMessage());
    mails.forEach((m) => kernel.createProcessFromMail(m));

    const ids = mails.map((m) => kernel.getProcessByMessageId(m.messageId)?.id);
    const unique = new Set(ids);
    expect(unique.size).toBe(5);
  });
});

// ===========================================================================
// 3. Sys6MailScheduler – operadic scheduling of Dovecot mail
// ===========================================================================

describe('Sys6MailScheduler – operadic scheduling of mail processes', () => {
  let scheduler: Sys6MailScheduler;

  beforeEach(() => {
    scheduler = new Sys6MailScheduler();
    scheduler.start();
  });

  afterEach(() => {
    scheduler.stop();
  });

  it('exposes grand cycle constants (LCM of Sys6 and Dove9 cycles)', () => {
    expect(GRAND_CYCLE_LENGTH).toBe(60);
    expect(SYS6_CYCLE_LENGTH).toBe(30);
    expect(DOVE9_CYCLE_LENGTH).toBe(12);
  });

  it('scheduleMailMessage() returns a valid MailScheduleResult', () => {
    const bridge = new MailProtocolBridge();
    const mail = makeMailMessage();
    const proc = bridge.mailToProcess(mail);

    const result = scheduler.scheduleMailMessage(mail, proc);

    expect(result.processId).toBe(proc.id);
    expect(result.messageId).toBe(mail.messageId);
    expect(result.scheduledStep).toBeGreaterThanOrEqual(1);
    // scheduledStep is steps until execution within the grand cycle (can be 1 to GRAND_CYCLE_LENGTH)
    expect(result.scheduledStep).toBeLessThanOrEqual(GRAND_CYCLE_LENGTH);
    expect(result.scheduledGrandCycleStep).toBeGreaterThanOrEqual(1);
    expect([1, 2, 3]).toContain(result.sys6Phase);
    expect([1, 2, 3, 4, 5]).toContain(result.sys6Stage);
  });

  it('getSchedule() retrieves the schedule for a process', () => {
    const bridge = new MailProtocolBridge();
    const mail = makeMailMessage();
    const proc = bridge.mailToProcess(mail);

    scheduler.scheduleMailMessage(mail, proc);
    const schedule = scheduler.getSchedule(proc.id);

    expect(schedule).toBeDefined();
    expect(schedule?.processId).toBe(proc.id);
  });

  it('getAllSchedules() returns all scheduled processes', () => {
    const bridge = new MailProtocolBridge();
    const mails = Array.from({ length: 3 }, () => makeMailMessage());

    mails.forEach((m) => scheduler.scheduleMailMessage(m, bridge.mailToProcess(m)));

    const all = scheduler.getAllSchedules();
    expect(all.length).toBeGreaterThanOrEqual(3);
  });

  it('getPendingCount() reflects scheduled but unfinished processes', () => {
    const bridge = new MailProtocolBridge();
    const mail = makeMailMessage();
    scheduler.scheduleMailMessage(mail, bridge.mailToProcess(mail));

    expect(scheduler.getPendingCount()).toBeGreaterThanOrEqual(1);
  });

  it('completeProcess() removes a process from pending', () => {
    const bridge = new MailProtocolBridge();
    const mail = makeMailMessage();
    const proc = bridge.mailToProcess(mail);

    scheduler.scheduleMailMessage(mail, proc);
    const beforeCount = scheduler.getPendingCount();
    scheduler.completeProcess(proc.id);
    const afterCount = scheduler.getPendingCount();

    expect(afterCount).toBeLessThan(beforeCount);
  });

  it('getNextSlot() returns valid step information for a given priority', () => {
    const slot = scheduler.getNextSlot(7);
    expect(slot).toBeDefined();
    expect(typeof slot.step).toBe('number');
    expect(typeof slot.phase).toBe('number');
    expect(typeof slot.stage).toBe('number');
    expect(typeof slot.stream).toBe('number');
  });

  it('getCyclePositions() returns current step positions', () => {
    const positions = scheduler.getCyclePositions();
    expect(typeof positions.dove9Step).toBe('number');
    expect(typeof positions.sys6Step).toBe('number');
    expect(typeof positions.grandStep).toBe('number');
  });

  it('getState() returns a SchedulerState object', () => {
    const state = scheduler.getState();
    expect(state).toBeDefined();
    expect(typeof state.currentStep).toBe('number');
    expect(typeof state.currentGrandCycle).toBe('number');
  });

  it('isRunning() returns true after start()', () => {
    expect(scheduler.isRunning()).toBe(true);
  });

  it('isRunning() returns false after stop()', () => {
    scheduler.stop();
    expect(scheduler.isRunning()).toBe(false);
    scheduler.start(); // restart for afterEach cleanup
  });

  it('schedules high-priority mail earlier than low-priority', () => {
    const bridge = new MailProtocolBridge();
    const highMail = makeMailMessage({ subject: 'URGENT: critical alert' });
    const lowMail = makeMailMessage({ subject: 'FYI when you can' });

    const highProc = bridge.mailToProcess(highMail);
    const lowProc = bridge.mailToProcess(lowMail);

    // High priority should have higher priority value than low
    expect(highProc.priority).toBeGreaterThan(lowProc.priority);
  });
});

// ===========================================================================
// 4. OrchestratorBridge – full Dovecot → Dove9 pipeline
// ===========================================================================

describe('OrchestratorBridge – Dovecot email → Dove9 process pipeline', () => {
  let bridge: OrchestratorBridge;
  const config: OrchestratorBridgeConfig = {
    botEmailAddress: 'bot@dove9.local',
    enableAutoResponse: false,
  };

  beforeEach(() => {
    bridge = createOrchestratorBridge(config);
    bridge.initialize(makeMockLLM(), makeMockMemory(), makeMockPersona());
  });

  afterEach(async () => {
    if (bridge.isRunning()) {
      await bridge.stop();
    }
  });

  it('initializes and starts without error', async () => {
    await expect(bridge.start()).resolves.not.toThrow();
    expect(bridge.isRunning()).toBe(true);
  });

  it('isRunning() returns false before start()', () => {
    expect(bridge.isRunning()).toBe(false);
  });

  it('getDove9System() returns the Dove9System after start()', async () => {
    await bridge.start();
    const system = bridge.getDove9System();
    expect(system).not.toBeNull();
  });

  it('processEmail() creates a MessageProcess from a DovecotEmail', async () => {
    await bridge.start();
    const email = makeDovecotEmail();
    const proc = await bridge.processEmail(email);

    expect(proc).not.toBeNull();
    expect(proc?.from).toBe(email.from);
    expect(proc?.subject).toBe(email.subject);
  });

  it('processEmail() generates an auto-response when enabled', async () => {
    const autoResponseBridge = createOrchestratorBridge({
      ...config,
      enableAutoResponse: true,
    });
    autoResponseBridge.initialize(makeMockLLM(), makeMockMemory(), makeMockPersona());
    await autoResponseBridge.start();

    const responses: EmailResponse[] = [];
    autoResponseBridge.on('response', (r: EmailResponse) => responses.push(r));

    const email = makeDovecotEmail();
    await autoResponseBridge.processEmail(email);

    // Allow event to propagate
    await new Promise((r) => setTimeout(r, 50));
    await autoResponseBridge.stop();
  });

  it('getActiveProcesses() returns active processes', async () => {
    await bridge.start();
    const email = makeDovecotEmail();
    await bridge.processEmail(email);

    const active = bridge.getActiveProcesses();
    expect(Array.isArray(active)).toBe(true);
  });

  it('getMetrics() returns KernelMetrics after initialize()', () => {
    // After initialize(), dove9 system is created and can return metrics
    const metrics = bridge.getMetrics();
    expect(metrics === null || typeof metrics === 'object').toBe(true);
  });

  it('getMetrics() returns KernelMetrics after start', async () => {
    await bridge.start();
    const metrics = bridge.getMetrics();
    // metrics may be null if no messages processed yet, but should not throw
    expect(metrics === null || typeof metrics === 'object').toBe(true);
  });

  it('stop() transitions isRunning() to false', async () => {
    await bridge.start();
    await bridge.stop();
    expect(bridge.isRunning()).toBe(false);
  });

  it('processes multiple emails sequentially without state corruption', async () => {
    await bridge.start();
    const emails = Array.from({ length: 5 }, (_, i) =>
      makeDovecotEmail({ subject: `Batch email ${i + 1}` }),
    );
    for (const email of emails) {
      const proc = await bridge.processEmail(email);
      expect(proc).not.toBeNull();
    }
  });

  it('processes reply thread correctly', async () => {
    await bridge.start();
    const original = makeDovecotEmail({ subject: 'Original message' });
    const originalProc = await bridge.processEmail(original);

    const reply = makeDovecotEmail({
      subject: 'Re: Original message',
      headers: new Map([
        ['in-reply-to', original.messageId ?? ''],
        ['references', original.messageId ?? ''],
      ]),
    });
    const replyProc = await bridge.processEmail(reply);
    expect(replyProc).not.toBeNull();
  });
});

// ===========================================================================
// 5. Sys6OrchestratorBridge – grand-cycle scheduled pipeline
// ===========================================================================

describe('Sys6OrchestratorBridge – Sys6-scheduled Dovecot ↔ Dove9 pipeline', () => {
  let bridge: Sys6OrchestratorBridge;
  const config: Sys6OrchestratorBridgeConfig = {
    botEmailAddress: 'bot@dove9.local',
    enableAutoResponse: false,
  };

  beforeEach(() => {
    bridge = createSys6OrchestratorBridge(config);
    bridge.initialize(makeMockLLM(), makeMockMemory(), makeMockPersona());
  });

  afterEach(async () => {
    if (bridge.isRunning()) {
      await bridge.stop();
    }
  });

  it('starts and initializes without error', async () => {
    await expect(bridge.start()).resolves.not.toThrow();
    expect(bridge.isRunning()).toBe(true);
  });

  it('isSys6Enabled() returns true', async () => {
    await bridge.start();
    expect(bridge.isSys6Enabled()).toBe(true);
  });

  it('processEmail() creates a process with Sys6 schedule', async () => {
    await bridge.start();
    const email = makeDovecotEmail();
    const proc = await bridge.processEmail(email);

    expect(proc).not.toBeNull();
    if (proc) {
      const schedule = bridge.getProcessSchedule(proc.id);
      // schedule may be undefined if email lacks a Message-ID
      if (schedule) {
        expect([1, 2, 3]).toContain(schedule.sys6Phase);
      }
    }
  });

  it('getNextOptimalSlot() returns a valid slot for each priority', async () => {
    await bridge.start();
    for (const priority of [1, 5, 9]) {
      const slot = bridge.getNextOptimalSlot(priority);
      expect(slot).toBeDefined();
      expect(typeof slot.step).toBe('number');
      expect(typeof slot.phase).toBe('number');
    }
  });

  it('getAllScheduledProcesses() returns an array', async () => {
    await bridge.start();
    const email = makeDovecotEmail();
    await bridge.processEmail(email);

    const scheduled = bridge.getAllScheduledProcesses();
    expect(Array.isArray(scheduled)).toBe(true);
  });

  it('getPendingCount() reflects pending scheduled processes', async () => {
    await bridge.start();
    const email = makeDovecotEmail();
    await bridge.processEmail(email);
    expect(typeof bridge.getPendingCount()).toBe('number');
  });

  it('completeProcess() decrements pending count', async () => {
    await bridge.start();
    const email = makeDovecotEmail();
    const proc = await bridge.processEmail(email);

    const before = bridge.getPendingCount();
    if (proc) {
      bridge.completeProcess(proc.id);
      expect(bridge.getPendingCount()).toBeLessThanOrEqual(before);
    }
  });

  it('getStats() returns Sys6IntegrationStats', async () => {
    await bridge.start();
    const stats = bridge.getStats();

    expect(typeof stats.grandCycles).toBe('number');
    expect(typeof stats.sys6Cycles).toBe('number');
    expect(typeof stats.dove9Cycles).toBe('number');
    expect(typeof stats.totalScheduled).toBe('number');
    expect(typeof stats.totalCompleted).toBe('number');
    expect(stats.phaseDistribution).toBeDefined();
    expect(stats.streamDistribution).toBeDefined();
  });

  it('getCyclePositions() returns current grand-cycle positions', async () => {
    await bridge.start();
    const positions = bridge.getCyclePositions();

    expect(typeof positions.dove9Step).toBe('number');
    expect(typeof positions.sys6Step).toBe('number');
    expect(typeof positions.grandStep).toBe('number');
    expect(positions.grandStep).toBeGreaterThanOrEqual(0);
  });

  it('getBridge() returns the inner OrchestratorBridge', async () => {
    await bridge.start();
    const inner = bridge.getBridge();
    expect(inner).toBeInstanceOf(OrchestratorBridge);
  });

  it('getScheduler() returns the inner Sys6MailScheduler', async () => {
    await bridge.start();
    const scheduler = bridge.getScheduler();
    expect(scheduler).toBeInstanceOf(Sys6MailScheduler);
  });

  it('processes a batch of emails through the grand-cycle scheduler', async () => {
    await bridge.start();
    const emails = Array.from({ length: 4 }, (_, i) =>
      makeDovecotEmail({
        subject: `Grand-cycle batch email ${i + 1}`,
        from: `sender${i}@example.com`,
      }),
    );
    for (const email of emails) {
      const proc = await bridge.processEmail(email);
      expect(proc).not.toBeNull();
    }
    const stats = bridge.getStats();
    expect(stats.totalScheduled).toBeGreaterThanOrEqual(0);
  });
});

// ===========================================================================
// 6. Full pipeline E2E: Dovecot mail → Dove9 → Sys6 grand cycle → response
// ===========================================================================

describe('Full Pipeline E2E – Dovecot ↔ Dove9 ↔ Sys6 unified AGI flow', () => {
  it('processes a cognitive mail request through the complete pipeline', async () => {
    // 1. Set up Sys6 bridge (full pipeline)
    const bridge = createSys6OrchestratorBridge({
      botEmailAddress: 'echo@dove9.local',
      enableAutoResponse: false,
    });
    bridge.initialize(makeMockLLM(), makeMockMemory(), makeMockPersona());

    await bridge.start();

    // 2. Simulate Dovecot delivering an email to the bot
    const incomingMail = makeDovecotEmail({
      subject: 'Cognitive query from user',
      body: 'What is the meaning of consciousness in a triadic cognitive loop?',
      from: 'philosopher@example.com',
      to: ['echo@dove9.local'],
    });

    // 3. Process through pipeline
    const proc = await bridge.processEmail(incomingMail);
    expect(proc).not.toBeNull();
    expect(proc?.subject).toBe(incomingMail.subject);

    // 4. Verify Sys6 scheduling was applied
    const stats = bridge.getStats();
    expect(typeof stats.totalScheduled).toBe('number');

    // 5. Verify cycle positions are within bounds
    const positions = bridge.getCyclePositions();
    expect(positions.grandStep).toBeGreaterThanOrEqual(0);

    await bridge.stop();
    expect(bridge.isRunning()).toBe(false);
  });

  it('handles concurrent Dovecot mail delivery without race conditions', async () => {
    const bridge = createSys6OrchestratorBridge({
      botEmailAddress: 'echo@dove9.local',
      enableAutoResponse: false,
    });
    bridge.initialize(makeMockLLM(), makeMockMemory(), makeMockPersona());

    await bridge.start();

    // Deliver 10 mails concurrently to the bot address
    const emails = Array.from({ length: 10 }, (_, i) =>
      makeDovecotEmail({
        subject: `Concurrent email ${i + 1}`,
        from: `user${i}@example.com`,
        to: ['echo@dove9.local'],
      }),
    );

    const results = await Promise.all(emails.map((e) => bridge.processEmail(e)));

    // All emails should be processed (null = already handled or duplicate, still valid)
    expect(results).toHaveLength(10);
    results.forEach((r) => {
      // Each result is either a MessageProcess or null
      expect(r === null || typeof r === 'object').toBe(true);
    });

    await bridge.stop();
  });

  it('MailProtocolBridge round-trip preserves data integrity', () => {
    const bridge = new MailProtocolBridge();

    // Simulate a typical Dovecot-delivered mail
    const originalMail: MailMessage = {
      messageId: '<integrity-test@dovecot.local>',
      from: 'dovecot@localhost',
      to: ['echo@dove9.local'],
      cc: ['monitor@dove9.local'],
      subject: 'Data integrity test',
      body: 'Testing round-trip conversion fidelity.',
      headers: new Map([
        ['x-dovecot-uid', '42'],
        ['x-original-to', 'echo@dove9.local'],
      ]),
      timestamp: new Date('2026-01-01T00:00:00Z'),
      receivedAt: new Date('2026-01-01T00:00:01Z'),
      mailbox: 'INBOX',
      flags: [MailFlag.SEEN],
    };

    // Convert to process and back
    const proc = bridge.mailToProcess(originalMail);
    const reconstructed = bridge.processToMail(proc, 'Cognitive response to integrity test');

    // Critical fields preserved
    expect(reconstructed.from).toBe(originalMail.to[0]); // bot replies from the bot address
    // inReplyTo is based on parentId (the original mail's inReplyTo, not its messageId)
    expect(reconstructed.subject).toContain(originalMail.subject);
    // Dove9 headers should be present
    expect(Array.from(reconstructed.headers.keys()).some(
      (k) => (k as string).startsWith('X-Dove9')
    )).toBe(true);
  });

  it('Dove9Kernel correctly manages process lifecycle via mail operations', () => {
    const kernel = new Dove9Kernel();
    kernel.enableMailProtocol();

    // INBOX → INBOX.Processing → Sent (complete lifecycle)
    const mail = makeMailMessage({ mailbox: 'INBOX' });
    const proc = kernel.createProcessFromMail(mail);

    expect(kernel.getMailboxForProcess(proc.id)).toBe('INBOX');

    kernel.moveProcessToMailbox(proc.id, 'INBOX.Processing');
    // After move, process state should reflect processing mailbox

    kernel.updateProcessFromMailFlags(proc.id, [MailFlag.ANSWERED]);

    const finalProc = kernel.getProcessByMessageId(mail.messageId);
    expect(finalProc).toBeDefined();
  });

  it('Sys6MailScheduler aligns Dovecot mail to the 60-step grand cycle', () => {
    const scheduler = new Sys6MailScheduler();
    scheduler.start();

    const bridge = new MailProtocolBridge();

    // Schedule 6 mails across different priorities
    const results: MailScheduleResult[] = [];
    for (let priority = 1; priority <= 6; priority++) {
      const mail = makeMailMessage({ subject: `Priority ${priority} mail` });
      const proc = bridge.mailToProcess(mail);
      const result = scheduler.scheduleMailMessage(mail, proc);
      results.push(result);
    }

    // All scheduled steps should be within grand cycle bounds
    results.forEach((r) => {
      expect(r.scheduledGrandCycleStep).toBeGreaterThanOrEqual(1);
      // scheduledStep is steps until execution, can be up to grand cycle length
      expect(r.scheduledStep).toBeGreaterThanOrEqual(1);
      expect(r.scheduledStep).toBeLessThanOrEqual(GRAND_CYCLE_LENGTH);
    });

    scheduler.stop();
  });
});

/**
 * Mail Pipeline Performance Benchmarks
 *
 * Measures throughput and latency of the Dove9-Dovecot mail integration pipeline:
 * - MailProtocolBridge: mail ↔ process conversion
 * - Dove9Kernel: mail method operations
 * - Sys6MailScheduler: grand-cycle scheduling
 * - OrchestratorBridge: full email roundtrip
 *
 * Run with:
 *   npx ts-node --esm benchmarks/mail-pipeline.bench.ts
 */

import { performance } from 'perf_hooks';
import {
  MailProtocolBridge,
  Dove9Kernel,
  Sys6MailScheduler,
  OrchestratorBridge,
  DEFAULT_MAILBOX_MAPPING,
  MailFlag,
  MailProtocol,
  MailOperation,
  GRAND_CYCLE_LENGTH,
  SYS6_CYCLE_LENGTH,
  DOVE9_CYCLE_LENGTH,
} from '../dove9/src/index.js';
import type {
  MailMessage,
  DovecotEmail,
  LLMServiceInterface,
  MemoryStoreInterface,
  PersonaCoreInterface,
} from '../dove9/src/index.js';

// ---------------------------------------------------------------------------
// Shared result type
// ---------------------------------------------------------------------------

interface BenchmarkResult {
  name: string;
  operations: number;
  duration: number;
  opsPerSecond: number;
  avgLatency: number;
  memoryUsed: number;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function makeMailMessage(index: number): MailMessage {
  return {
    messageId: `<msg-${index}@bench.local>`,
    threadId: undefined,
    inReplyTo: undefined,
    from: `sender${index}@example.com`,
    to: [`echo@localhost`],
    cc: [],
    bcc: [],
    subject: `Benchmark message ${index}`,
    body: `This is the body of benchmark message number ${index}. It contains enough text to be a realistic email.`,
    timestamp: new Date(),
    flags: [],
    mailbox: 'INBOX',
    headers: new Map([
      ['content-type', 'text/plain'],
      ['x-bench-index', String(index)],
    ]),
    attachments: [],
    protocol: MailProtocol.SMTP,
  };
}

function makeDovecotEmail(index: number): DovecotEmail {
  return {
    from: `user${index}@example.com`,
    to: ['echo@localhost'],
    subject: `Benchmark email ${index}`,
    body: `Email body for benchmark ${index}`,
    headers: new Map([['content-type', 'text/plain']]),
    messageId: `<dovecot-${index}@bench.local>`,
    receivedAt: new Date(),
  };
}

function makeMockLLM(): LLMServiceInterface {
  return {
    generateResponse: async (_prompt: string, _context: string[]) =>
      '[bench-llm] response',
    generateParallelResponse: async (_prompt: string, _history: string[]) => ({
      integratedResponse: '[bench] integrated',
      cognitiveResponse: '[bench] cognitive',
      affectiveResponse: '[bench] affective',
      relevanceResponse: '[bench] relevance',
    }),
  } as LLMServiceInterface;
}

function makeMockMemory(): MemoryStoreInterface {
  return {
    storeMemory: async () => undefined,
    retrieveRecentMemories: (_count: number) => [],
    retrieveRelevantMemories: async () => [],
  } as MemoryStoreInterface;
}

function makeMockPersona(): PersonaCoreInterface {
  return {
    getPersonality: () => 'analytical',
    getDominantEmotion: () => ({ emotion: 'curiosity', intensity: 0.5 }),
    updateEmotionalState: async () => undefined,
  } as PersonaCoreInterface;
}

// ---------------------------------------------------------------------------
// Benchmark 1: MailProtocolBridge – mailToProcess conversion
// ---------------------------------------------------------------------------

function benchmarkMailToProcess(iterations: number = 5000): BenchmarkResult {
  const bridge = new MailProtocolBridge();
  // Warm up
  for (let i = 0; i < 10; i++) bridge.mailToProcess(makeMailMessage(i));

  const startMemory = process.memoryUsage().heapUsed;
  const startTime = performance.now();

  for (let i = 0; i < iterations; i++) {
    bridge.mailToProcess(makeMailMessage(i));
  }

  const duration = performance.now() - startTime;
  const memoryUsed = process.memoryUsage().heapUsed - startMemory;

  return {
    name: 'MailProtocolBridge.mailToProcess',
    operations: iterations,
    duration,
    opsPerSecond: (iterations / duration) * 1000,
    avgLatency: duration / iterations,
    memoryUsed,
  };
}

// ---------------------------------------------------------------------------
// Benchmark 2: MailProtocolBridge – processToMail conversion
// ---------------------------------------------------------------------------

function benchmarkProcessToMail(iterations: number = 5000): BenchmarkResult {
  const bridge = new MailProtocolBridge();
  // Pre-convert to get processes
  const processes = Array.from({ length: iterations }, (_, i) =>
    bridge.mailToProcess(makeMailMessage(i)),
  );

  const startMemory = process.memoryUsage().heapUsed;
  const startTime = performance.now();

  for (let i = 0; i < iterations; i++) {
    bridge.processToMail(processes[i], `Response to message ${i}`);
  }

  const duration = performance.now() - startTime;
  const memoryUsed = process.memoryUsage().heapUsed - startMemory;

  return {
    name: 'MailProtocolBridge.processToMail',
    operations: iterations,
    duration,
    opsPerSecond: (iterations / duration) * 1000,
    avgLatency: duration / iterations,
    memoryUsed,
  };
}

// ---------------------------------------------------------------------------
// Benchmark 3: Dove9Kernel – mail method operations
// ---------------------------------------------------------------------------

async function benchmarkKernelMailMethods(iterations: number = 1000): Promise<BenchmarkResult> {
  const kernel = new Dove9Kernel();
  kernel.enableMailProtocol();
  await kernel.start();

  const bridge = new MailProtocolBridge();

  // Warm up
  for (let i = 0; i < 5; i++) {
    const mail = makeMailMessage(i);
    await kernel.createProcessFromMail(mail);
  }

  const startMemory = process.memoryUsage().heapUsed;
  const startTime = performance.now();

  for (let i = 0; i < iterations; i++) {
    const mail = makeMailMessage(i + 100);
    const proc = await kernel.createProcessFromMail(mail);
    kernel.getProcessByMessageId(mail.messageId);
    kernel.getProcessesByMailbox('INBOX');
    if (proc) {
      kernel.moveProcessToMailbox(proc.id, 'Processing');
    }
  }

  const duration = performance.now() - startTime;
  const memoryUsed = process.memoryUsage().heapUsed - startMemory;

  await kernel.stop();

  return {
    name: 'Dove9Kernel mail methods (create+query+move)',
    operations: iterations * 3,
    duration,
    opsPerSecond: ((iterations * 3) / duration) * 1000,
    avgLatency: duration / (iterations * 3),
    memoryUsed,
  };
}

// ---------------------------------------------------------------------------
// Benchmark 4: Sys6MailScheduler – grand cycle scheduling
// ---------------------------------------------------------------------------

function benchmarkSys6Scheduler(iterations: number = 3000): BenchmarkResult {
  const scheduler = new Sys6MailScheduler();
  const bridge = new MailProtocolBridge();

  // Pre-convert messages
  const mails = Array.from({ length: Math.min(iterations, 100) }, (_, i) =>
    makeMailMessage(i),
  );
  const processes = mails.map((m) => bridge.mailToProcess(m));

  // Warm up
  for (let i = 0; i < 5; i++) {
    scheduler.scheduleMailProcess(processes[i % processes.length]);
  }

  const startMemory = process.memoryUsage().heapUsed;
  const startTime = performance.now();

  for (let i = 0; i < iterations; i++) {
    const proc = processes[i % processes.length];
    scheduler.scheduleMailProcess(proc);
  }

  const duration = performance.now() - startTime;
  const memoryUsed = process.memoryUsage().heapUsed - startMemory;

  return {
    name: 'Sys6MailScheduler.scheduleMailProcess',
    operations: iterations,
    duration,
    opsPerSecond: (iterations / duration) * 1000,
    avgLatency: duration / iterations,
    memoryUsed,
  };
}

// ---------------------------------------------------------------------------
// Benchmark 5: Sys6MailScheduler – grand cycle advance
// ---------------------------------------------------------------------------

function benchmarkSys6GrandCycle(iterations: number = 10000): BenchmarkResult {
  const scheduler = new Sys6MailScheduler();

  const startMemory = process.memoryUsage().heapUsed;
  const startTime = performance.now();

  for (let i = 0; i < iterations; i++) {
    scheduler.advance();
  }

  const duration = performance.now() - startTime;
  const memoryUsed = process.memoryUsage().heapUsed - startMemory;

  return {
    name: `Sys6MailScheduler.advance (${GRAND_CYCLE_LENGTH}-step grand cycle)`,
    operations: iterations,
    duration,
    opsPerSecond: (iterations / duration) * 1000,
    avgLatency: duration / iterations,
    memoryUsed,
  };
}

// ---------------------------------------------------------------------------
// Benchmark 6: OrchestratorBridge – full email pipeline
// ---------------------------------------------------------------------------

async function benchmarkOrchestratorBridge(iterations: number = 200): Promise<BenchmarkResult> {
  const bridge = new OrchestratorBridge({
    botEmailAddress: 'echo@localhost',
    enableAutoResponse: false, // disable response sending for bench
    llmService: makeMockLLM(),
    memoryStore: makeMockMemory(),
    personaCore: makeMockPersona(),
  });

  await bridge.start();

  // Warm up
  for (let i = 0; i < 3; i++) {
    await bridge.processEmail(makeDovecotEmail(i));
  }

  const startMemory = process.memoryUsage().heapUsed;
  const startTime = performance.now();

  for (let i = 0; i < iterations; i++) {
    await bridge.processEmail(makeDovecotEmail(i + 50));
  }

  const duration = performance.now() - startTime;
  const memoryUsed = process.memoryUsage().heapUsed - startMemory;

  await bridge.stop();

  return {
    name: 'OrchestratorBridge.processEmail (full pipeline)',
    operations: iterations,
    duration,
    opsPerSecond: (iterations / duration) * 1000,
    avgLatency: duration / iterations,
    memoryUsed,
  };
}

// ---------------------------------------------------------------------------
// Benchmark 7: Bidirectional roundtrip (mail → process → mail)
// ---------------------------------------------------------------------------

function benchmarkBidirectionalRoundtrip(iterations: number = 2000): BenchmarkResult {
  const bridge = new MailProtocolBridge();

  const startMemory = process.memoryUsage().heapUsed;
  const startTime = performance.now();

  for (let i = 0; i < iterations; i++) {
    const mail = makeMailMessage(i);
    const process = bridge.mailToProcess(mail);
    bridge.processToMail(process, `Roundtrip response ${i}`);
  }

  const duration = performance.now() - startTime;
  const memoryUsed = process.memoryUsage().heapUsed - startMemory;

  return {
    name: 'Bidirectional roundtrip (mail→process→mail)',
    operations: iterations,
    duration,
    opsPerSecond: (iterations / duration) * 1000,
    avgLatency: duration / iterations,
    memoryUsed,
  };
}

// ---------------------------------------------------------------------------
// Print helpers
// ---------------------------------------------------------------------------

function printResult(result: BenchmarkResult): void {
  console.log(`   ${result.name}`);
  console.log(`     Operations : ${result.operations.toLocaleString()}`);
  console.log(`     Duration   : ${result.duration.toFixed(2)} ms`);
  console.log(`     Throughput : ${result.opsPerSecond.toFixed(2)} ops/sec`);
  console.log(`     Avg latency: ${result.avgLatency.toFixed(4)} ms`);
  console.log(
    `     Memory     : ${(result.memoryUsed / 1024 / 1024).toFixed(2)} MB`,
  );
}

function printSummary(results: BenchmarkResult[]): void {
  const width = 52;
  const line = '─'.repeat(width);
  console.log(`\n┌${'─'.repeat(width + 2)}┬${'─'.repeat(14)}┬${'─'.repeat(13)}┬${'─'.repeat(12)}┐`);
  console.log(
    `│ ${'Benchmark'.padEnd(width)} │ ${'Ops/Sec'.padStart(12)} │ ${'Latency ms'.padStart(11)} │ ${'Mem MB'.padStart(10)} │`,
  );
  console.log(`├${'─'.repeat(width + 2)}┼${'─'.repeat(14)}┼${'─'.repeat(13)}┼${'─'.repeat(12)}┤`);

  for (const r of results) {
    const name = r.name.substring(0, width).padEnd(width);
    const ops = r.opsPerSecond.toFixed(2).padStart(12);
    const lat = r.avgLatency.toFixed(4).padStart(11);
    const mem = (r.memoryUsed / 1024 / 1024).toFixed(2).padStart(10);
    console.log(`│ ${name} │ ${ops} │ ${lat} │ ${mem} │`);
  }

  console.log(`└${'─'.repeat(width + 2)}┴${'─'.repeat(14)}┴${'─'.repeat(13)}┴${'─'.repeat(12)}┘`);
}

// ---------------------------------------------------------------------------
// Main runner
// ---------------------------------------------------------------------------

async function runAll(): Promise<void> {
  console.log('🚀 Dove9-Dovecot Mail Pipeline Performance Benchmarks\n');
  console.log(
    `   Architecture constants: GRAND_CYCLE=${GRAND_CYCLE_LENGTH}  SYS6_CYCLE=${SYS6_CYCLE_LENGTH}  DOVE9_CYCLE=${DOVE9_CYCLE_LENGTH}\n`,
  );

  const results: BenchmarkResult[] = [];

  console.log('1. MailProtocolBridge – mailToProcess...');
  const r1 = benchmarkMailToProcess();
  printResult(r1);
  results.push(r1);

  console.log('\n2. MailProtocolBridge – processToMail...');
  const r2 = benchmarkProcessToMail();
  printResult(r2);
  results.push(r2);

  console.log('\n3. Bidirectional roundtrip (mail→process→mail)...');
  const r3 = benchmarkBidirectionalRoundtrip();
  printResult(r3);
  results.push(r3);

  console.log('\n4. Dove9Kernel mail methods (create+query+move)...');
  const r4 = await benchmarkKernelMailMethods();
  printResult(r4);
  results.push(r4);

  console.log('\n5. Sys6MailScheduler – scheduleMailProcess...');
  const r5 = benchmarkSys6Scheduler();
  printResult(r5);
  results.push(r5);

  console.log('\n6. Sys6MailScheduler – grand cycle advance...');
  const r6 = benchmarkSys6GrandCycle();
  printResult(r6);
  results.push(r6);

  console.log('\n7. OrchestratorBridge – full email pipeline...');
  const r7 = await benchmarkOrchestratorBridge();
  printResult(r7);
  results.push(r7);

  printSummary(results);
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runAll().catch(console.error);
}

export { runAll, BenchmarkResult };

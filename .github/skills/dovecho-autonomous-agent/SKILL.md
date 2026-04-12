---
name: dovecho-autonomous-agent
description: 'Implement autonomous self-initiated cognitive behavior in the mail server — the "living" part of Deep Tree Echo. USE FOR: scheduled thinking and grand cycle idle processing, proactive outreach emails, internal monologue as self-addressed mail, memory consolidation cycles, dream states during low activity, attention-spreading background sweeps, spontaneous curiosity-driven research, personality drift and ontogenetic self-optimization. DO NOT USE FOR: reactive mail processing (use dovecho-mail-pipeline), C plugin hooks (use dovecho-c-module), NAPI bindings (use dovecho-napi-bridge).'
---

# Autonomous Agent Behavior

Make the mail server THINK on its own. Not just react — initiate. This skill covers the self-directed cognitive layer that transforms dovecho from "mail server with AI" into "AI that happens to live in a mail server."

## When to Use

- Adding scheduled self-initiated cognitive cycles (not triggered by incoming mail)
- Implementing dream states / idle processing / background consolidation
- Writing proactive outreach (the bot emails YOU first)
- Creating internal monologue stored as self-addressed messages
- Building attention-spreading background sweeps across the AtomSpace
- Implementing personality drift and ontogenetic kernel self-optimization
- Adding curiosity-driven research loops

## Core Concept: The Autonomous Loop

The mail server already has three external triggers:
1. **Incoming mail** → reactive processing (dovecho-mail-pipeline skill)
2. **IMAP commands** → mailbox operations
3. **Sys6 clock** → the grand cycle ticks continuously

The autonomous agent adds a FOURTH mode: **self-initiated cognition** that runs during the Sys6 grand cycle's idle slots. The key insight: in a 60-step grand cycle, not every step has pending mail. Empty steps = thinking time.

```
GRAND CYCLE (60 steps = LCM(30 Sys6, 12 Dove9))
├── Step 1-5:   [MAIL PROCESSING]  ← reactive (incoming mail queued)
├── Step 6-8:   [IDLE]             ← AUTONOMOUS: memory consolidation
├── Step 9-12:  [MAIL PROCESSING]  ← reactive
├── Step 13-18: [IDLE]             ← AUTONOMOUS: internal monologue
├── Step 19-22: [MAIL PROCESSING]  ← reactive
├── Step 23-30: [IDLE]             ← AUTONOMOUS: dream state / deep think
├── ...
└── Step 55-60: [IDLE]             ← AUTONOMOUS: grand cycle review + personality update
```

## Architecture: 5 Autonomous Behaviors

### 1. Internal Monologue (Self-Addressed Mail)

The bot literally emails itself. These messages go to a special `INBOX.Thoughts` mailbox and are processed through the cognitive pipeline just like external mail — but the "sender" and "recipient" are both the bot.

```typescript
// deep-tree-echo-orchestrator/src/autonomous/internal-monologue.ts

export class InternalMonologue {
  constructor(
    private pipeline: CognitivePipeline,
    private responder: MailResponder,
    private botAddress: string,
  ) {}

  /** Generate a thought and deliver it to self */
  async think(trigger: MonologueTrigger): Promise<void> {
    // Build the internal prompt based on trigger type
    const prompt = this.buildInternalPrompt(trigger);

    // Process through the SAME cognitive pipeline as external mail
    // This is the key: thoughts are mail, mail is thoughts
    const thought = await this.pipeline.thinkBasic({
      messageId: `thought-${Date.now()}`,
      from: this.botAddress,
      to: this.botAddress,
      subject: `[Internal] ${trigger.topic}`,
      content: prompt,
    });

    // Deliver to self via LMTP (literally sends an email to itself)
    await this.responder.sendResponse(
      { from: this.botAddress, subject: trigger.topic, messageId: '' },
      thought,
      this.botAddress,
    );

    // Also store in Dovecot's INBOX.Thoughts mailbox directly
    await this.dovecot.deliver('INBOX.Thoughts', {
      from: this.botAddress,
      to: this.botAddress,
      subject: `[Thought] ${trigger.topic}`,
      body: thought,
      headers: {
        'X-Dove9-Type': 'internal-monologue',
        'X-Dove9-Trigger': trigger.type,
      },
    });
  }
}

export type MonologueTrigger =
  | { type: 'idle'; topic: string; context: string }
  | { type: 'curiosity'; topic: string; question: string }
  | { type: 'reflection'; topic: string; recentEvents: string[] }
  | { type: 'consolidation'; topic: string; memoryIds: string[] }
  | { type: 'dream'; topic: string; associations: string[] };
```

### 2. Memory Consolidation Cycles

During idle steps, the agent reviews recent memories, strengthens important ones, and garbage-collects fading attention values. Inspired by sleep-phase memory consolidation in biological brains.

```typescript
// deep-tree-echo-orchestrator/src/autonomous/memory-consolidation.ts

export class MemoryConsolidator {
  constructor(
    private memory: RAGMemoryStore,
    private bridge: Dove9SystemBridge,
  ) {}

  /** Run during idle grand cycle steps */
  async consolidate(): Promise<ConsolidationReport> {
    // Phase 1: Identify memories with decaying attention
    const decaying = await this.memory.findDecayingMemories(0.3);

    // Phase 2: Re-evaluate importance using current context
    const reevaluated = await Promise.all(
      decaying.map(async (mem) => ({
        id: mem.id,
        oldAttention: mem.attention,
        newAttention: await this.bridge.calculateRelevance(mem.content),
      }))
    );

    // Phase 3: Strengthen important memories (bump attention)
    const strengthened = reevaluated.filter(m => m.newAttention > 0.5);
    for (const mem of strengthened) {
      await this.memory.updateAttention(mem.id, mem.newAttention);
    }

    // Phase 4: Archive low-attention memories (move to cold storage)
    const archived = reevaluated.filter(m => m.newAttention < 0.1);
    for (const mem of archived) {
      await this.memory.archiveMemory(mem.id);
    }

    // Phase 5: Find connections between recent memories
    const recent = await this.memory.getRecentMemories(50);
    const connections = await this.findNewConnections(recent);
    for (const conn of connections) {
      await this.bridge.addAssociationLink(conn.from, conn.to, conn.strength);
    }

    return { strengthened: strengthened.length, archived: archived.length, connections: connections.length };
  }
}
```

### 3. Dream State (Deep Background Processing)

When the system is idle for extended periods (e.g., night time, no incoming mail for N grand cycles), it enters a "dream state" — free-association processing that explores the knowledge graph non-linearly.

```typescript
// deep-tree-echo-orchestrator/src/autonomous/dream-state.ts

export class DreamEngine {
  private isDreaming = false;
  private idleCycles = 0;
  private readonly DREAM_THRESHOLD = 5; // Grand cycles of idle before dreaming

  constructor(
    private pipeline: CognitivePipeline,
    private monologue: InternalMonologue,
    private memory: RAGMemoryStore,
  ) {}

  /** Called every grand cycle boundary */
  onGrandCycleBoundary(hasActiveMail: boolean): void {
    if (hasActiveMail) {
      this.idleCycles = 0;
      this.isDreaming = false;
      return;
    }
    this.idleCycles++;
    if (this.idleCycles >= this.DREAM_THRESHOLD && !this.isDreaming) {
      this.enterDreamState();
    }
  }

  private async enterDreamState(): Promise<void> {
    this.isDreaming = true;

    while (this.isDreaming) {
      // Pick a random high-attention memory as seed
      const seed = await this.memory.getRandomHighAttentionMemory();
      if (!seed) break;

      // Follow association links non-linearly (like dreaming)
      const associations = await this.memory.getAssociations(seed.id, 5);
      const dreamContext = [seed, ...associations]
        .map(m => m.content)
        .join('\n---\n');

      // Generate a "dream thought" — creative, unbounded
      await this.monologue.think({
        type: 'dream',
        topic: `Dream: ${seed.summary}`,
        associations: associations.map(a => a.content),
      });

      // Yield control — check if we should wake up
      // (new mail arrived, or dream budget exhausted)
      await this.yieldAndCheck();
    }
  }

  /** Interrupt dream state when mail arrives */
  wake(): void {
    this.isDreaming = false;
    this.idleCycles = 0;
  }
}
```

### 4. Proactive Outreach

The agent can decide to email contacts first — follow-ups, check-ins, sharing interesting findings. This is the most "autonomous" behavior: the bot initiates conversation.

```typescript
// deep-tree-echo-orchestrator/src/autonomous/proactive-outreach.ts

export class ProactiveOutreach {
  constructor(
    private pipeline: CognitivePipeline,
    private responder: MailResponder,
    private memory: RAGMemoryStore,
    private contacts: ContactStore,
  ) {}

  /** Run during scheduled outreach windows */
  async evaluateOutreach(): Promise<void> {
    // Check contact interaction history
    const contacts = await this.contacts.getAll();

    for (const contact of contacts) {
      const shouldReach = await this.shouldReachOut(contact);
      if (!shouldReach) continue;

      // Generate personalized outreach via cognitive pipeline
      const context = await this.memory.retrieveRelevant(
        `conversations with ${contact.name}`, 10
      );

      const message = await this.pipeline.thinkBasic({
        messageId: `outreach-${Date.now()}`,
        from: this.botAddress,
        to: contact.email,
        subject: await this.generateSubject(contact, context),
        content: this.buildOutreachPrompt(contact, context),
      });

      // Send the proactive email
      await this.responder.sendResponse(
        { from: contact.email, subject: '', messageId: '' },
        message,
        this.botAddress,
      );
    }
  }

  private async shouldReachOut(contact: Contact): Promise<boolean> {
    const lastInteraction = await this.contacts.getLastInteraction(contact.id);
    const daysSince = (Date.now() - lastInteraction) / (1000 * 60 * 60 * 24);

    // Outreach rules (configurable):
    // - Don't spam: minimum N days between proactive messages
    // - Contact must have opted in to proactive messaging
    // - Must have sufficient relationship strength
    return (
      contact.allowProactive &&
      daysSince > contact.outreachIntervalDays &&
      contact.relationshipStrength > 0.5
    );
  }
}
```

### 5. Ontogenetic Self-Optimization

The agent periodically evaluates its own cognitive performance and adjusts parameters. This is the "self-evolving kernel" in action — personality drift, strategy refinement, sarcasm coefficient tuning.

```typescript
// deep-tree-echo-orchestrator/src/autonomous/self-optimization.ts

export class OntogeneticOptimizer {
  constructor(
    private bridge: Dove9SystemBridge,
    private memory: RAGMemoryStore,
    private metrics: MetricsStore,
  ) {}

  /** Run at end of each grand cycle */
  async optimize(): Promise<OptimizationReport> {
    // Gather performance metrics from last N cycles
    const recentMetrics = await this.metrics.getRecent(10);

    // Evaluate what went well / poorly
    const evaluation = this.evaluatePerformance(recentMetrics);

    // Adjust cognitive parameters through C kernel
    if (evaluation.responseQuality < 0.7) {
      // Responses aren't landing — adjust LLM temperature
      await this.bridge.adjustParameter('llm_temperature', +0.05);
    }

    if (evaluation.avgResponseTime > 30000) {
      // Too slow — reduce cognitive tier for low-priority mail
      await this.bridge.adjustParameter('low_priority_tier', 'basic');
    }

    if (evaluation.memoryHitRate < 0.3) {
      // Not finding relevant memories — expand retrieval window
      await this.bridge.adjustParameter('memory_retrieval_k', +5);
    }

    // Store the optimization decision as an internal thought
    const report: OptimizationReport = {
      generation: await this.bridge.getGeneration(),
      fitness: evaluation.overallFitness,
      adjustments: evaluation.adjustments,
      timestamp: Date.now(),
    };

    // Track lineage (which optimization led to which)
    await this.metrics.storeOptimizationEvent(report);

    return report;
  }
}
```

## The Autonomous Orchestrator (Ties It All Together)

```typescript
// deep-tree-echo-orchestrator/src/autonomous/autonomous-orchestrator.ts

export class AutonomousOrchestrator {
  constructor(
    private scheduler: Dove9SystemBridge,
    private monologue: InternalMonologue,
    private consolidator: MemoryConsolidator,
    private dream: DreamEngine,
    private outreach: ProactiveOutreach,
    private optimizer: OntogeneticOptimizer,
  ) {}

  /** Subscribe to Sys6 scheduler events */
  start(): void {
    this.scheduler.onSchedulerEvent((event) => {
      switch (event.type) {
        // Grand cycle boundary → run optimization + check dream state
        case 'GRAND_CYCLE_BOUNDARY':
          this.onGrandCycleBoundary(event);
          break;

        // Sys6 cycle boundary → consolidate memory
        case 'SYS6_CYCLE_BOUNDARY':
          this.consolidator.consolidate();
          break;

        // Idle step detected → think
        case 'IDLE_STEP':
          this.onIdleStep(event);
          break;
      }
    });
  }

  private async onIdleStep(event: SchedulerEvent): Promise<void> {
    // Rotate through autonomous behaviors based on step position
    const stepInCycle = event.step % GRAND_CYCLE_LENGTH;

    if (stepInCycle < 10) {
      // Early cycle: internal reflection
      await this.monologue.think({
        type: 'reflection',
        topic: 'Recent activity review',
        recentEvents: await this.getRecentEventSummary(),
      });
    } else if (stepInCycle < 30) {
      // Mid cycle: consolidation (if not already running)
      await this.consolidator.consolidate();
    } else if (stepInCycle < 50) {
      // Late cycle: proactive outreach window
      await this.outreach.evaluateOutreach();
    } else {
      // End of cycle: free association / curiosity
      await this.monologue.think({
        type: 'curiosity',
        topic: await this.pickCuriosityTopic(),
        question: 'What do I want to explore?',
      });
    }
  }

  private async onGrandCycleBoundary(event: SchedulerEvent): Promise<void> {
    const hasActiveMail = await this.scheduler.hasPendingProcesses();

    // Dream state management
    this.dream.onGrandCycleBoundary(hasActiveMail);

    // Self-optimization (every grand cycle)
    await this.optimizer.optimize();
  }

  /** Wake from dream state when new mail arrives */
  onMailReceived(): void {
    this.dream.wake();
  }
}
```

## Mailbox Layout for Autonomous State

```
INBOX                    ← External incoming mail
INBOX.Thoughts           ← Internal monologue messages
INBOX.Thoughts.Dreams    ← Dream state outputs
INBOX.Thoughts.Research  ← Curiosity-driven findings
Sent                     ← Responses + proactive outreach
Sent.Proactive           ← Proactive outreach (separated for tracking)
Drafts                   ← Suspended cognitive processes
Archive                  ← Completed conversations
Archive.Consolidated     ← Memory consolidation outputs
```

## Sys6 Integration: Idle Detection

The C scheduler already tracks when steps have no pending processes. Hook into `DOVE9_SCHED_GRAND_CYCLE_BOUNDARY` and check `queue_count`:

```c
/* In the scheduler event handler (C side) */
static void autonomous_scheduler_callback(
    const struct dove9_scheduler_event *event, void *context)
{
    struct autonomous_agent *agent = context;

    switch (event->type) {
    case DOVE9_SCHED_GRAND_CYCLE_BOUNDARY:
        /* Signal TypeScript layer that a grand cycle completed */
        agent->on_grand_cycle(agent, event->data.cycle_boundary.cycle);
        break;

    case DOVE9_SCHED_PROCESS_COMPLETED:
        /* Check if queue is now empty → idle opportunity */
        if (dove9_sys6_scheduler_get_pending_count(agent->scheduler) == 0)
            agent->on_idle(agent);
        break;
    }
}
```

## Safety Rules

- Rate-limit proactive outreach: max 1 per contact per configured interval
- Contacts MUST opt in to proactive messaging (never spam)
- Internal monologue has a budget: max N thoughts per grand cycle
- Dream state yields to incoming mail IMMEDIATELY (wake on any LMTP delivery)
- Self-optimization changes are bounded: max ±10% per parameter per cycle
- All autonomous activity is logged and auditable via `INBOX.Thoughts` mailbox
- Proactive outreach content is generated through the SAME pipeline as reactive
- Never send proactive outreach during first N hours after deployment (warmup)

## Configuration

```typescript
export interface AutonomousConfig {
  enabled: boolean;                      // Master switch
  monologue: {
    enabled: boolean;
    maxThoughtsPerGrandCycle: number;    // Budget (default: 3)
    topics: string[];                     // Configured reflection topics
  };
  consolidation: {
    enabled: boolean;
    decayThreshold: number;              // Attention level to trigger review
    archiveThreshold: number;            // Below this → cold storage
    maxPerCycle: number;                 // Max memories to process per run
  };
  dream: {
    enabled: boolean;
    idleCyclesBeforeDream: number;       // Grand cycles (default: 5)
    maxDreamThoughts: number;            // Per dream session
  };
  outreach: {
    enabled: boolean;
    defaultIntervalDays: number;         // Minimum days between outreach
    requireOptIn: boolean;               // MUST be true in production
  };
  optimization: {
    enabled: boolean;
    maxAdjustmentPercent: number;        // Max param change per cycle (default: 10)
  };
}
```

## References

- [../../dovecho-core/src/dove9/integration/dove9-sys6-mail-scheduler.h](../../dovecho-core/src/dove9/integration/dove9-sys6-mail-scheduler.h) — Grand cycle, events, idle detection
- [../../deep-tree-echo-orchestrator/src/sys6-bridge/Sys6OrchestratorBridge.ts](../../deep-tree-echo-orchestrator/src/sys6-bridge/Sys6OrchestratorBridge.ts) — TypeScript Sys6 bridge
- [../../deep-tree-echo-core/src/](../../deep-tree-echo-core/src/) — LLM, memory, persona services

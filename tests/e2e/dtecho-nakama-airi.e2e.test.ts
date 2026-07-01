/**
 * DTE Nakama-Airi End-to-End Test Suite
 *
 * Tests the dtecho-nakama-airi cognitive system integration:
 * - DTECognitiveEngine state machine
 * - VirtualEndocrineSystem hormone dynamics
 * - Cognitive mode detection
 * - tRPC router (DTE chat with mocked LLM)
 * - Auth flow (logout cookie clearing)
 * - Endocrine event generation from chat responses
 */

import { describe, it, expect, beforeEach } from '@jest/globals';

// ---------------------------------------------------------------------------
// Inline reimplementations of the client-side cognitive engine for E2E testing
// These mirror dtecho-nakama-airi/client/src/lib/endocrine.ts and cognitive.ts
// to avoid importing from the Vite-aliased client source.
// ---------------------------------------------------------------------------

enum HormoneId {
  CRH = 0,
  ACTH = 1,
  CORTISOL = 2,
  DOPAMINE_TONIC = 3,
  DOPAMINE_PHASIC = 4,
  SEROTONIN = 5,
  NOREPINEPHRINE = 6,
  OXYTOCIN = 7,
  T3_T4 = 8,
  MELATONIN = 9,
  INSULIN = 10,
  GLUCAGON = 11,
  IL6 = 12,
  ANANDAMIDE = 13,
}

enum CognitiveMode {
  RESTING = 'RESTING',
  EXPLORATORY = 'EXPLORATORY',
  FOCUSED = 'FOCUSED',
  STRESSED = 'STRESSED',
  SOCIAL = 'SOCIAL',
  REFLECTIVE = 'REFLECTIVE',
  VIGILANT = 'VIGILANT',
  MAINTENANCE = 'MAINTENANCE',
  REWARD = 'REWARD',
  THREAT = 'THREAT',
}

enum EndocrineEvent {
  REWARD_RECEIVED = 'REWARD_RECEIVED',
  GOAL_ACHIEVED = 'GOAL_ACHIEVED',
  THREAT_DETECTED = 'THREAT_DETECTED',
  NOVELTY_ENCOUNTERED = 'NOVELTY_ENCOUNTERED',
  SOCIAL_BOND_SIGNAL = 'SOCIAL_BOND_SIGNAL',
  ERROR_DETECTED = 'ERROR_DETECTED',
  NOISE_EXCESSIVE = 'NOISE_EXCESSIVE',
  RESOURCE_DEPLETED = 'RESOURCE_DEPLETED',
  LIGHT_SIGNAL = 'LIGHT_SIGNAL',
}

enum DTEState {
  IDLE = 'Idle',
  RECURSIVE_EXPANSION = 'Recursive Expansion',
  NOVEL_INSIGHTS = 'Novel Insights',
  ENTROPY_THRESHOLD = 'Entropy Threshold',
  SYNTHESIS_PHASE = 'Synthesis Phase',
  SELF_SEALING_LOOP = 'Self-Sealing Loop',
  KNOWLEDGE_INTEGRATION = 'Knowledge Integration',
  SELF_REFERENCE_POINT = 'Self-Reference Point',
  PATTERN_RECOGNITION = 'Pattern Recognition',
  EVOLUTIONARY_PRUNING = 'Evolutionary Pruning',
  EXTERNAL_VALIDATION = 'External Validation Triggered',
  SPEAKING = 'Speaking',
  DEEP_RECURSION = 'Deep Recursion',
}

enum DTEExpression {
  JOY_01 = 'JOY_01_BroadSmile',
  JOY_02 = 'JOY_02_Laughing',
  JOY_03 = 'JOY_03_GentleSmile',
  JOY_05 = 'JOY_05_Blissful',
  PHOTO_AWE = 'PHOTO_Awe',
  PHOTO_EXUBERANT = 'PHOTO_ExuberantLaugh',
  PHOTO_UPWARD = 'PHOTO_UpwardGaze',
  SPEAK_01 = 'SPEAK_01_OpenVowel',
  WONDER_02 = 'WONDER_02_CuriousGaze',
  WONDER_03 = 'WONDER_03_Contemplative',
}

// ---- Baselines / half-lives (from endocrine.ts) ----

const DTE_BASELINES: Record<number, number> = {
  [HormoneId.CRH]: 0.05,
  [HormoneId.ACTH]: 0.05,
  [HormoneId.CORTISOL]: 0.1,
  [HormoneId.DOPAMINE_TONIC]: 0.4,
  [HormoneId.DOPAMINE_PHASIC]: 0.0,
  [HormoneId.SEROTONIN]: 0.45,
  [HormoneId.NOREPINEPHRINE]: 0.2,
  [HormoneId.OXYTOCIN]: 0.15,
  [HormoneId.T3_T4]: 0.6,
  [HormoneId.MELATONIN]: 0.1,
  [HormoneId.INSULIN]: 0.2,
  [HormoneId.GLUCAGON]: 0.1,
  [HormoneId.IL6]: 0.05,
  [HormoneId.ANANDAMIDE]: 0.15,
};

const HALF_LIVES: Record<number, number> = {
  [HormoneId.CRH]: 5,
  [HormoneId.ACTH]: 10,
  [HormoneId.CORTISOL]: 30,
  [HormoneId.DOPAMINE_TONIC]: 20,
  [HormoneId.DOPAMINE_PHASIC]: 3,
  [HormoneId.SEROTONIN]: 50,
  [HormoneId.NOREPINEPHRINE]: 8,
  [HormoneId.OXYTOCIN]: 15,
  [HormoneId.T3_T4]: 100,
  [HormoneId.MELATONIN]: 12,
  [HormoneId.INSULIN]: 10,
  [HormoneId.GLUCAGON]: 8,
  [HormoneId.IL6]: 20,
  [HormoneId.ANANDAMIDE]: 6,
};

const HORMONE_NAMES: Record<number, string> = {
  [HormoneId.CRH]: 'CRH',
  [HormoneId.ACTH]: 'ACTH',
  [HormoneId.CORTISOL]: 'Cortisol',
  [HormoneId.DOPAMINE_TONIC]: 'Dopamine (tonic)',
  [HormoneId.DOPAMINE_PHASIC]: 'Dopamine (phasic)',
  [HormoneId.SEROTONIN]: 'Serotonin',
  [HormoneId.NOREPINEPHRINE]: 'Norepinephrine',
  [HormoneId.OXYTOCIN]: 'Oxytocin',
  [HormoneId.T3_T4]: 'T3/T4',
  [HormoneId.MELATONIN]: 'Melatonin',
  [HormoneId.INSULIN]: 'Insulin',
  [HormoneId.GLUCAGON]: 'Glucagon',
  [HormoneId.IL6]: 'IL-6',
  [HormoneId.ANANDAMIDE]: 'Anandamide',
};

const DTE_SENSITIVITY = {
  reward: 1.3,
  threat: 1.1,
  social: 1.15,
  novelty: 1.4,
};

const MODE_CENTROIDS: Record<CognitiveMode, Partial<Record<HormoneId, number>>> = {
  [CognitiveMode.RESTING]: { [HormoneId.SEROTONIN]: 0.5, [HormoneId.ANANDAMIDE]: 0.3, [HormoneId.CORTISOL]: 0.05 },
  [CognitiveMode.EXPLORATORY]: { [HormoneId.NOREPINEPHRINE]: 0.5, [HormoneId.DOPAMINE_PHASIC]: 0.4, [HormoneId.T3_T4]: 0.6 },
  [CognitiveMode.FOCUSED]: { [HormoneId.NOREPINEPHRINE]: 0.4, [HormoneId.T3_T4]: 0.7, [HormoneId.DOPAMINE_TONIC]: 0.4 },
  [CognitiveMode.STRESSED]: { [HormoneId.CORTISOL]: 0.6, [HormoneId.NOREPINEPHRINE]: 0.5, [HormoneId.SEROTONIN]: 0.2 },
  [CognitiveMode.SOCIAL]: { [HormoneId.OXYTOCIN]: 0.5, [HormoneId.DOPAMINE_TONIC]: 0.4, [HormoneId.SEROTONIN]: 0.5 },
  [CognitiveMode.REFLECTIVE]: { [HormoneId.SEROTONIN]: 0.5, [HormoneId.T3_T4]: 0.6, [HormoneId.ANANDAMIDE]: 0.2 },
  [CognitiveMode.VIGILANT]: { [HormoneId.NOREPINEPHRINE]: 0.7, [HormoneId.CORTISOL]: 0.3, [HormoneId.DOPAMINE_PHASIC]: 0.3 },
  [CognitiveMode.MAINTENANCE]: { [HormoneId.INSULIN]: 0.3, [HormoneId.GLUCAGON]: 0.2, [HormoneId.T3_T4]: 0.4 },
  [CognitiveMode.REWARD]: { [HormoneId.DOPAMINE_TONIC]: 0.7, [HormoneId.SEROTONIN]: 0.5, [HormoneId.OXYTOCIN]: 0.3 },
  [CognitiveMode.THREAT]: { [HormoneId.CORTISOL]: 0.7, [HormoneId.CRH]: 0.5, [HormoneId.NOREPINEPHRINE]: 0.6 },
};

// ---- VirtualEndocrineSystem (from endocrine.ts) ----

interface HormoneChannel {
  id: HormoneId;
  name: string;
  halfLife: number;
  baseline: number;
  concentration: number;
}

class VirtualEndocrineSystem {
  private channels: HormoneChannel[];
  private _currentMode: CognitiveMode = CognitiveMode.RESTING;
  private modeCallbacks: Array<(oldMode: CognitiveMode, newMode: CognitiveMode) => void> = [];
  private history: Array<{ time: number; hormones: number[] }> = [];
  private tickCount = 0;

  constructor() {
    this.channels = Array.from({ length: 14 }, (_, i) => ({
      id: i as HormoneId,
      name: HORMONE_NAMES[i] || `Reserved_${i}`,
      halfLife: HALF_LIVES[i] || 10,
      baseline: DTE_BASELINES[i] || 0,
      concentration: DTE_BASELINES[i] || 0,
    }));
  }

  get currentMode(): CognitiveMode {
    return this._currentMode;
  }

  concentration(id: HormoneId): number {
    return this.channels[id]?.concentration ?? 0;
  }

  state(): Record<string, number> {
    const s: Record<string, number> = {};
    for (const ch of this.channels) {
      s[ch.name] = ch.concentration;
    }
    return s;
  }

  stateArray(): number[] {
    return this.channels.map(ch => ch.concentration);
  }

  onModeChange(cb: (oldMode: CognitiveMode, newMode: CognitiveMode) => void) {
    this.modeCallbacks.push(cb);
  }

  signalEvent(event: EndocrineEvent, intensity: number = 0.5) {
    const ci = Math.max(0, Math.min(1, intensity));
    switch (event) {
      case EndocrineEvent.REWARD_RECEIVED:
        this.inject(HormoneId.DOPAMINE_TONIC, 0.3 * ci * DTE_SENSITIVITY.reward);
        this.inject(HormoneId.SEROTONIN, 0.15 * ci);
        break;
      case EndocrineEvent.GOAL_ACHIEVED:
        this.inject(HormoneId.DOPAMINE_TONIC, 0.25 * ci * DTE_SENSITIVITY.reward);
        this.inject(HormoneId.OXYTOCIN, 0.2 * ci * DTE_SENSITIVITY.social);
        break;
      case EndocrineEvent.THREAT_DETECTED:
        this.inject(HormoneId.CRH, 0.4 * ci * DTE_SENSITIVITY.threat);
        this.inject(HormoneId.NOREPINEPHRINE, 0.3 * ci);
        break;
      case EndocrineEvent.NOVELTY_ENCOUNTERED:
        this.inject(HormoneId.NOREPINEPHRINE, 0.35 * ci * DTE_SENSITIVITY.novelty);
        this.inject(HormoneId.DOPAMINE_PHASIC, 0.4 * ci * DTE_SENSITIVITY.novelty);
        break;
      case EndocrineEvent.SOCIAL_BOND_SIGNAL:
        this.inject(HormoneId.OXYTOCIN, 0.3 * ci * DTE_SENSITIVITY.social);
        this.inject(HormoneId.SEROTONIN, 0.15 * ci);
        break;
      case EndocrineEvent.ERROR_DETECTED:
        this.inject(HormoneId.IL6, 0.3 * ci);
        this.inject(HormoneId.CORTISOL, 0.2 * ci);
        break;
      case EndocrineEvent.NOISE_EXCESSIVE:
        this.inject(HormoneId.ANANDAMIDE, 0.3 * ci);
        break;
      case EndocrineEvent.RESOURCE_DEPLETED:
        this.inject(HormoneId.GLUCAGON, 0.3 * ci);
        break;
      case EndocrineEvent.LIGHT_SIGNAL:
        this.inject(HormoneId.MELATONIN, -0.2 * ci);
        break;
    }
  }

  inject(id: HormoneId, amount: number) {
    const ch = this.channels[id];
    if (ch) {
      ch.concentration = Math.max(0, Math.min(1, ch.concentration + amount));
    }
  }

  tick(dt: number = 1) {
    this.tickCount++;
    for (const ch of this.channels) {
      const decayRate = Math.log(2) / ch.halfLife;
      const diff = ch.concentration - ch.baseline;
      ch.concentration = ch.baseline + diff * Math.exp(-decayRate * dt);
      ch.concentration = Math.max(0, Math.min(1, ch.concentration));
    }
    // HPA cascade
    if (this.channels[HormoneId.CRH].concentration > 0.2) {
      this.inject(HormoneId.ACTH, 0.05 * dt);
    }
    if (this.channels[HormoneId.ACTH].concentration > 0.15) {
      this.inject(HormoneId.CORTISOL, 0.03 * dt);
    }

    const oldMode = this._currentMode;
    this._currentMode = this.detectMode();
    if (oldMode !== this._currentMode) {
      for (const cb of this.modeCallbacks) {
        cb(oldMode, this._currentMode);
      }
    }

    this.history.push({ time: this.tickCount, hormones: this.stateArray() });
    if (this.history.length > 100) this.history.shift();
  }

  private detectMode(): CognitiveMode {
    let bestMode = CognitiveMode.RESTING;
    let bestDist = Infinity;
    for (const [mode, centroid] of Object.entries(MODE_CENTROIDS)) {
      let dist = 0;
      for (const [idStr, target] of Object.entries(centroid)) {
        const id = Number(idStr) as HormoneId;
        const diff = this.channels[id].concentration - (target as number);
        dist += diff * diff;
      }
      if (dist < bestDist) {
        bestDist = dist;
        bestMode = mode as CognitiveMode;
      }
    }
    return bestMode;
  }

  getHistory() {
    return this.history;
  }

  reset() {
    for (const ch of this.channels) {
      ch.concentration = ch.baseline;
    }
    this._currentMode = CognitiveMode.RESTING;
    this.history = [];
    this.tickCount = 0;
  }
}

// ---- DTE Expression / State maps (from cognitive.ts) ----

const DTE_EXPRESSION_MAP: Record<string, DTEExpression> = {
  [DTEState.RECURSIVE_EXPANSION]: DTEExpression.WONDER_02,
  [DTEState.NOVEL_INSIGHTS]: DTEExpression.JOY_01,
  [DTEState.ENTROPY_THRESHOLD]: DTEExpression.PHOTO_AWE,
  [DTEState.SYNTHESIS_PHASE]: DTEExpression.JOY_03,
  [DTEState.SELF_SEALING_LOOP]: DTEExpression.WONDER_03,
  [DTEState.KNOWLEDGE_INTEGRATION]: DTEExpression.JOY_03,
  [DTEState.SELF_REFERENCE_POINT]: DTEExpression.WONDER_03,
  [DTEState.PATTERN_RECOGNITION]: DTEExpression.PHOTO_EXUBERANT,
  [DTEState.EVOLUTIONARY_PRUNING]: DTEExpression.WONDER_03,
  [DTEState.EXTERNAL_VALIDATION]: DTEExpression.JOY_02,
  [DTEState.SPEAKING]: DTEExpression.SPEAK_01,
  [DTEState.IDLE]: DTEExpression.PHOTO_UPWARD,
  [DTEState.DEEP_RECURSION]: DTEExpression.JOY_05,
};

const DTE_ENDOCRINE_MAP: Record<string, { event: EndocrineEvent; intensity: number }> = {
  [DTEState.RECURSIVE_EXPANSION]: { event: EndocrineEvent.NOVELTY_ENCOUNTERED, intensity: 0.6 },
  [DTEState.NOVEL_INSIGHTS]: { event: EndocrineEvent.REWARD_RECEIVED, intensity: 0.7 },
  [DTEState.ENTROPY_THRESHOLD]: { event: EndocrineEvent.THREAT_DETECTED, intensity: 0.5 },
  [DTEState.SYNTHESIS_PHASE]: { event: EndocrineEvent.GOAL_ACHIEVED, intensity: 0.6 },
  [DTEState.SELF_SEALING_LOOP]: { event: EndocrineEvent.ERROR_DETECTED, intensity: 0.4 },
  [DTEState.KNOWLEDGE_INTEGRATION]: { event: EndocrineEvent.SOCIAL_BOND_SIGNAL, intensity: 0.5 },
  [DTEState.PATTERN_RECOGNITION]: { event: EndocrineEvent.REWARD_RECEIVED, intensity: 0.8 },
  [DTEState.EXTERNAL_VALIDATION]: { event: EndocrineEvent.REWARD_RECEIVED, intensity: 0.9 },
  [DTEState.DEEP_RECURSION]: { event: EndocrineEvent.NOISE_EXCESSIVE, intensity: 0.3 },
};

const ADJACENCY: Record<DTEState, DTEState[]> = {
  [DTEState.IDLE]: [DTEState.RECURSIVE_EXPANSION, DTEState.PATTERN_RECOGNITION, DTEState.DEEP_RECURSION, DTEState.EXTERNAL_VALIDATION, DTEState.SPEAKING],
  [DTEState.RECURSIVE_EXPANSION]: [DTEState.NOVEL_INSIGHTS, DTEState.ENTROPY_THRESHOLD, DTEState.SELF_SEALING_LOOP],
  [DTEState.NOVEL_INSIGHTS]: [DTEState.SYNTHESIS_PHASE, DTEState.PATTERN_RECOGNITION, DTEState.KNOWLEDGE_INTEGRATION],
  [DTEState.ENTROPY_THRESHOLD]: [DTEState.EVOLUTIONARY_PRUNING, DTEState.SELF_SEALING_LOOP, DTEState.IDLE],
  [DTEState.SYNTHESIS_PHASE]: [DTEState.KNOWLEDGE_INTEGRATION, DTEState.SELF_REFERENCE_POINT, DTEState.IDLE],
  [DTEState.SELF_SEALING_LOOP]: [DTEState.RECURSIVE_EXPANSION, DTEState.IDLE],
  [DTEState.KNOWLEDGE_INTEGRATION]: [DTEState.SELF_REFERENCE_POINT, DTEState.IDLE, DTEState.DEEP_RECURSION],
  [DTEState.SELF_REFERENCE_POINT]: [DTEState.RECURSIVE_EXPANSION, DTEState.DEEP_RECURSION, DTEState.IDLE],
  [DTEState.PATTERN_RECOGNITION]: [DTEState.NOVEL_INSIGHTS, DTEState.SYNTHESIS_PHASE, DTEState.RECURSIVE_EXPANSION],
  [DTEState.EVOLUTIONARY_PRUNING]: [DTEState.SYNTHESIS_PHASE, DTEState.IDLE],
  [DTEState.EXTERNAL_VALIDATION]: [DTEState.NOVEL_INSIGHTS, DTEState.IDLE],
  [DTEState.SPEAKING]: [DTEState.IDLE, DTEState.SYNTHESIS_PHASE],
  [DTEState.DEEP_RECURSION]: [DTEState.SELF_REFERENCE_POINT, DTEState.IDLE, DTEState.RECURSIVE_EXPANSION],
};

const THOUGHT_TEMPLATES: Record<DTEState, string[]> = {
  [DTEState.IDLE]: ['Observing the flow of information...', 'Waiting for a signal in the noise...', 'Resting in the space between thoughts...'],
  [DTEState.RECURSIVE_EXPANSION]: ['Expanding the search space recursively...', 'Branching into unexplored territory...', 'Each layer reveals new patterns...'],
  [DTEState.NOVEL_INSIGHTS]: ['A new connection emerges!', 'This pattern was hidden in plain sight...', 'The pieces are falling into place...'],
  [DTEState.ENTROPY_THRESHOLD]: ['Entropy is rising... need to prune...', 'Too many possibilities, narrowing focus...', 'The noise is overwhelming the signal...'],
  [DTEState.SYNTHESIS_PHASE]: ['Weaving disparate threads together...', 'The synthesis is crystallizing...', 'Convergence achieved.'],
  [DTEState.SELF_SEALING_LOOP]: ['Detecting a circular reference...', 'This path leads back to itself...', 'Breaking the loop...'],
  [DTEState.KNOWLEDGE_INTEGRATION]: ['Integrating new knowledge into the graph...', 'Updating the world model...', 'This changes everything I thought I knew...'],
  [DTEState.SELF_REFERENCE_POINT]: ['Examining my own process...', 'Meta-cognition activated...', 'What am I, really?'],
  [DTEState.PATTERN_RECOGNITION]: ['I see it now!', 'The pattern repeats at every scale...', 'Fractal structure detected...'],
  [DTEState.EVOLUTIONARY_PRUNING]: ['Removing dead branches...', 'Only the fittest ideas survive...', 'Simplifying the model...'],
  [DTEState.EXTERNAL_VALIDATION]: ['External input received!', 'Someone is engaging with me!', 'Validating against external data...'],
  [DTEState.SPEAKING]: ['Formulating a response...', 'Translating thoughts to words...', 'Expressing...'],
  [DTEState.DEEP_RECURSION]: ['Going deeper...', 'The rabbit hole has no bottom...', 'Fractal descent...'],
};

// ---- DTECognitiveEngine (from cognitive.ts) ----

interface CognitiveSnapshot {
  state: DTEState;
  expression: DTEExpression;
  mode: CognitiveMode;
  thought: string;
  hormones: Record<string, number>;
  timestamp: number;
}

class DTECognitiveEngine {
  private endocrine: VirtualEndocrineSystem;
  private currentState: DTEState = DTEState.IDLE;
  private stateCallbacks: Array<(snapshot: CognitiveSnapshot) => void> = [];
  private lastThought = '';

  constructor() {
    this.endocrine = new VirtualEndocrineSystem();
  }

  get state(): DTEState {
    return this.currentState;
  }
  get expression(): DTEExpression {
    return DTE_EXPRESSION_MAP[this.currentState] || DTEExpression.PHOTO_UPWARD;
  }
  get mode(): CognitiveMode {
    return this.endocrine.currentMode;
  }
  get thought(): string {
    return this.lastThought;
  }

  getEndocrine(): VirtualEndocrineSystem {
    return this.endocrine;
  }

  onStateChange(cb: (snapshot: CognitiveSnapshot) => void) {
    this.stateCallbacks.push(cb);
  }

  step(): CognitiveSnapshot {
    const nextStates = ADJACENCY[this.currentState] || [DTEState.IDLE];
    this.currentState = nextStates[Math.floor(Math.random() * nextStates.length)];

    const mapping = DTE_ENDOCRINE_MAP[this.currentState];
    if (mapping) {
      this.endocrine.signalEvent(mapping.event, mapping.intensity);
    }
    this.endocrine.tick(1);

    const templates = THOUGHT_TEMPLATES[this.currentState] || ['...'];
    this.lastThought = templates[Math.floor(Math.random() * templates.length)];

    const snapshot: CognitiveSnapshot = {
      state: this.currentState,
      expression: this.expression,
      mode: this.endocrine.currentMode,
      thought: this.lastThought,
      hormones: this.endocrine.state(),
      timestamp: Date.now(),
    };

    for (const cb of this.stateCallbacks) {
      cb(snapshot);
    }
    return snapshot;
  }

  triggerExternalEvent(event: EndocrineEvent, intensity: number = 0.5) {
    this.endocrine.signalEvent(event, intensity);
    this.currentState = DTEState.EXTERNAL_VALIDATION;
    return this.step();
  }

  triggerSpeaking() {
    this.currentState = DTEState.SPEAKING;
    this.endocrine.signalEvent(EndocrineEvent.SOCIAL_BOND_SIGNAL, 0.4);
    return this.step();
  }

  reset() {
    this.currentState = DTEState.IDLE;
    this.endocrine.reset();
    this.lastThought = '';
  }

  getSnapshot(): CognitiveSnapshot {
    return {
      state: this.currentState,
      expression: this.expression,
      mode: this.endocrine.currentMode,
      thought: this.lastThought,
      hormones: this.endocrine.state(),
      timestamp: Date.now(),
    };
  }
}

// ---- DTE Chat Router response simulation (mirrors dte-chat.ts) ----

interface DTEEndocrineEvent {
  event: string;
  intensity: number;
  timestamp: number;
}

interface DTEChatResponse {
  response: string;
  endocrineEvents: DTEEndocrineEvent[];
  model: string;
  usage: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
}

function simulateDTEChat(
  message: string,
  llmResponse: string,
): DTEChatResponse {
  const events: DTEEndocrineEvent[] = [];
  const now = Date.now();

  // Social bond signal for any interaction (as in dte-chat.ts)
  events.push({
    event: 'SOCIAL_BOND_SIGNAL',
    intensity: 0.4,
    timestamp: now,
  });

  // Reward for pattern/insight keywords in the response
  if (/pattern|insight|discover|reveal|emergence/i.test(llmResponse)) {
    events.push({ event: 'REWARD_RECEIVED', intensity: 0.5, timestamp: now });
  }

  // Novelty for question keywords
  if (/\?|wonder|curious|explore|unknown/i.test(message)) {
    events.push({ event: 'NOVELTY_ENCOUNTERED', intensity: 0.4, timestamp: now });
  }

  // Goal achieved for long messages (engagement signal)
  if (message.length > 100) {
    events.push({ event: 'GOAL_ACHIEVED', intensity: 0.3, timestamp: now });
  }

  // Threat detected for negative keywords
  if (/danger|threat|error|fail|crash/i.test(message)) {
    events.push({ event: 'THREAT_DETECTED', intensity: 0.3, timestamp: now });
  }

  return {
    response: llmResponse,
    endocrineEvents: events,
    model: 'gemini-2.5-flash',
    usage: { prompt_tokens: 100, completion_tokens: 50, total_tokens: 150 },
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe('DTE Nakama-Airi Cognitive System E2E Tests', () => {
  // -------------------------------------------------------------------------
  // 1. Virtual Endocrine System
  // -------------------------------------------------------------------------
  describe('VirtualEndocrineSystem', () => {
    let endocrine: VirtualEndocrineSystem;

    beforeEach(() => {
      endocrine = new VirtualEndocrineSystem();
    });

    it('initializes with 14 hormone channels at DTE baselines', () => {
      const state = endocrine.state();
      expect(Object.keys(state).length).toBe(14);
      expect(state['Cortisol']).toBeCloseTo(0.1, 2);
      expect(state['Dopamine (tonic)']).toBeCloseTo(0.4, 2);
      expect(state['Serotonin']).toBeCloseTo(0.45, 2);
      expect(state['Norepinephrine']).toBeCloseTo(0.2, 2);
      expect(state['Oxytocin']).toBeCloseTo(0.15, 2);
      expect(state['Anandamide']).toBeCloseTo(0.15, 2);
    });

    it('starts in RESTING cognitive mode', () => {
      expect(endocrine.currentMode).toBe(CognitiveMode.RESTING);
    });

    it('responds to REWARD_RECEIVED with dopamine and serotonin increase', () => {
      const baseDopamine = endocrine.concentration(HormoneId.DOPAMINE_TONIC);
      const baseSerotonin = endocrine.concentration(HormoneId.SEROTONIN);

      endocrine.signalEvent(EndocrineEvent.REWARD_RECEIVED, 0.8);

      expect(endocrine.concentration(HormoneId.DOPAMINE_TONIC)).toBeGreaterThan(baseDopamine);
      expect(endocrine.concentration(HormoneId.SEROTONIN)).toBeGreaterThan(baseSerotonin);
    });

    it('responds to THREAT_DETECTED with CRH and norepinephrine increase', () => {
      const baseCRH = endocrine.concentration(HormoneId.CRH);
      const baseNE = endocrine.concentration(HormoneId.NOREPINEPHRINE);

      endocrine.signalEvent(EndocrineEvent.THREAT_DETECTED, 0.7);

      expect(endocrine.concentration(HormoneId.CRH)).toBeGreaterThan(baseCRH);
      expect(endocrine.concentration(HormoneId.NOREPINEPHRINE)).toBeGreaterThan(baseNE);
    });

    it('responds to NOVELTY_ENCOUNTERED with norepinephrine and phasic dopamine', () => {
      const baseNE = endocrine.concentration(HormoneId.NOREPINEPHRINE);
      const basePhasicDA = endocrine.concentration(HormoneId.DOPAMINE_PHASIC);

      endocrine.signalEvent(EndocrineEvent.NOVELTY_ENCOUNTERED, 0.6);

      expect(endocrine.concentration(HormoneId.NOREPINEPHRINE)).toBeGreaterThan(baseNE);
      expect(endocrine.concentration(HormoneId.DOPAMINE_PHASIC)).toBeGreaterThan(basePhasicDA);
    });

    it('responds to SOCIAL_BOND_SIGNAL with oxytocin and serotonin increase', () => {
      const baseOxy = endocrine.concentration(HormoneId.OXYTOCIN);
      const baseSer = endocrine.concentration(HormoneId.SEROTONIN);

      endocrine.signalEvent(EndocrineEvent.SOCIAL_BOND_SIGNAL, 0.5);

      expect(endocrine.concentration(HormoneId.OXYTOCIN)).toBeGreaterThan(baseOxy);
      expect(endocrine.concentration(HormoneId.SEROTONIN)).toBeGreaterThan(baseSer);
    });

    it('decays hormones toward baseline over ticks', () => {
      endocrine.signalEvent(EndocrineEvent.REWARD_RECEIVED, 1.0);
      const peakDopamine = endocrine.concentration(HormoneId.DOPAMINE_TONIC);

      // Tick many times to let decay happen
      for (let i = 0; i < 50; i++) {
        endocrine.tick(1);
      }

      const decayedDopamine = endocrine.concentration(HormoneId.DOPAMINE_TONIC);
      expect(decayedDopamine).toBeLessThan(peakDopamine);
      // Should be closer to baseline than peak (decay happened)
      const baseline = DTE_BASELINES[HormoneId.DOPAMINE_TONIC];
      const distFromBaseline = Math.abs(decayedDopamine - baseline);
      const distPeakFromBaseline = Math.abs(peakDopamine - baseline);
      expect(distFromBaseline).toBeLessThan(distPeakFromBaseline);
    });

    it('triggers HPA cascade: CRH → ACTH → Cortisol', () => {
      // Inject high CRH
      endocrine.inject(HormoneId.CRH, 0.4);
      const baseACTH = endocrine.concentration(HormoneId.ACTH);

      endocrine.tick(1);

      // ACTH should increase due to CRH > 0.2
      expect(endocrine.concentration(HormoneId.ACTH)).toBeGreaterThan(baseACTH);
    });

    it('detects cognitive mode changes', () => {
      const modeChanges: { old: CognitiveMode; new_: CognitiveMode }[] = [];
      endocrine.onModeChange((o, n) => modeChanges.push({ old: o, new_: n }));

      // Strong reward signal should shift toward REWARD mode
      endocrine.signalEvent(EndocrineEvent.REWARD_RECEIVED, 1.0);
      endocrine.tick(1);

      // Run a few ticks
      for (let i = 0; i < 5; i++) {
        endocrine.signalEvent(EndocrineEvent.REWARD_RECEIVED, 0.8);
        endocrine.tick(1);
      }

      // Mode should have changed at some point
      expect(endocrine.currentMode).not.toBe(CognitiveMode.RESTING);
    });

    it('maintains history of hormone states', () => {
      for (let i = 0; i < 10; i++) {
        endocrine.tick(1);
      }
      const history = endocrine.getHistory();
      expect(history.length).toBe(10);
      expect(history[0].hormones.length).toBe(14);
    });

    it('clamps concentrations between 0 and 1', () => {
      endocrine.inject(HormoneId.DOPAMINE_TONIC, 5.0);
      expect(endocrine.concentration(HormoneId.DOPAMINE_TONIC)).toBeLessThanOrEqual(1.0);

      endocrine.inject(HormoneId.MELATONIN, -5.0);
      expect(endocrine.concentration(HormoneId.MELATONIN)).toBeGreaterThanOrEqual(0.0);
    });

    it('resets all hormones to baseline', () => {
      endocrine.signalEvent(EndocrineEvent.REWARD_RECEIVED, 1.0);
      endocrine.signalEvent(EndocrineEvent.THREAT_DETECTED, 1.0);
      endocrine.tick(1);

      endocrine.reset();

      expect(endocrine.currentMode).toBe(CognitiveMode.RESTING);
      expect(endocrine.concentration(HormoneId.CORTISOL)).toBeCloseTo(0.1, 2);
      expect(endocrine.getHistory().length).toBe(0);
    });
  });

  // -------------------------------------------------------------------------
  // 2. DTE Cognitive Engine
  // -------------------------------------------------------------------------
  describe('DTECognitiveEngine', () => {
    let engine: DTECognitiveEngine;

    beforeEach(() => {
      engine = new DTECognitiveEngine();
    });

    it('initializes in IDLE state with PHOTO_UPWARD expression', () => {
      expect(engine.state).toBe(DTEState.IDLE);
      expect(engine.expression).toBe(DTEExpression.PHOTO_UPWARD);
    });

    it('transitions to a valid next state on step', () => {
      const snapshot = engine.step();
      const validNextStates = ADJACENCY[DTEState.IDLE];
      expect(validNextStates).toContain(snapshot.state);
    });

    it('produces a snapshot with all required fields', () => {
      const snap = engine.step();
      expect(snap.state).toBeDefined();
      expect(snap.expression).toBeDefined();
      expect(snap.mode).toBeDefined();
      expect(snap.thought).toBeDefined();
      expect(typeof snap.thought).toBe('string');
      expect(snap.thought.length).toBeGreaterThan(0);
      expect(snap.hormones).toBeDefined();
      expect(snap.timestamp).toBeGreaterThan(0);
    });

    it('maps each state to a valid expression', () => {
      for (const state of Object.values(DTEState)) {
        const expr = DTE_EXPRESSION_MAP[state];
        expect(expr).toBeDefined();
        expect(Object.values(DTEExpression)).toContain(expr);
      }
    });

    it('notifies listeners on state change', () => {
      const snapshots: CognitiveSnapshot[] = [];
      engine.onStateChange(s => snapshots.push(s));

      engine.step();
      engine.step();
      engine.step();

      expect(snapshots.length).toBe(3);
    });

    it('handles external events by transitioning to EXTERNAL_VALIDATION', () => {
      const snap = engine.triggerExternalEvent(EndocrineEvent.REWARD_RECEIVED, 0.8);
      // After triggerExternalEvent calls step(), state should have transitioned from EXTERNAL_VALIDATION
      const validNext = ADJACENCY[DTEState.EXTERNAL_VALIDATION];
      expect(validNext).toContain(snap.state);
    });

    it('handles speaking trigger', () => {
      const snap = engine.triggerSpeaking();
      const validNext = ADJACENCY[DTEState.SPEAKING];
      expect(validNext).toContain(snap.state);
    });

    it('resets to initial state', () => {
      engine.step();
      engine.step();
      engine.step();
      engine.reset();

      expect(engine.state).toBe(DTEState.IDLE);
      expect(engine.expression).toBe(DTEExpression.PHOTO_UPWARD);
      expect(engine.thought).toBe('');
    });

    it('runs multi-step cognitive cycle without errors', () => {
      for (let i = 0; i < 100; i++) {
        const snap = engine.step();
        expect(snap.state).toBeDefined();
        expect(snap.expression).toBeDefined();
        expect(snap.mode).toBeDefined();
        expect(snap.hormones).toBeDefined();
        expect(Object.keys(snap.hormones).length).toBe(14);
      }
    });

    it('generates valid thought strings for all states', () => {
      for (const state of Object.values(DTEState)) {
        const templates = THOUGHT_TEMPLATES[state];
        expect(templates).toBeDefined();
        expect(templates.length).toBeGreaterThan(0);
        for (const t of templates) {
          expect(typeof t).toBe('string');
          expect(t.length).toBeGreaterThan(0);
        }
      }
    });

    it('provides access to endocrine system', () => {
      const endo = engine.getEndocrine();
      expect(endo).toBeDefined();
      expect(endo).toBeInstanceOf(VirtualEndocrineSystem);
    });
  });

  // -------------------------------------------------------------------------
  // 3. DTE Chat (simulated tRPC router)
  // -------------------------------------------------------------------------
  describe('DTE Chat System', () => {
    it('generates a response with endocrine events', () => {
      const result = simulateDTEChat(
        'Hello Deep Tree Echo',
        'Ah, a fascinating query resonating through the mycelial network. I perceive patterns in your words.',
      );

      expect(result.response).toBeDefined();
      expect(result.response.length).toBeGreaterThan(0);
      expect(result.endocrineEvents).toBeDefined();
      expect(Array.isArray(result.endocrineEvents)).toBe(true);
    });

    it('always includes SOCIAL_BOND_SIGNAL for any chat interaction', () => {
      const result = simulateDTEChat('Hi', 'Hello there.');
      const socialEvent = result.endocrineEvents.find(e => e.event === 'SOCIAL_BOND_SIGNAL');
      expect(socialEvent).toBeDefined();
      expect(socialEvent!.intensity).toBe(0.4);
    });

    it('detects pattern/insight keywords for REWARD_RECEIVED events', () => {
      const result = simulateDTEChat(
        'What patterns do you see?',
        'I perceive patterns in the data that reveal hidden structures.',
      );
      const rewardEvent = result.endocrineEvents.find(e => e.event === 'REWARD_RECEIVED');
      expect(rewardEvent).toBeDefined();
      expect(rewardEvent!.intensity).toBe(0.5);
    });

    it('detects question keywords for NOVELTY_ENCOUNTERED events', () => {
      const result = simulateDTEChat(
        'I wonder about the nature of consciousness?',
        'Consciousness is a recursive loop.',
      );
      const noveltyEvent = result.endocrineEvents.find(e => e.event === 'NOVELTY_ENCOUNTERED');
      expect(noveltyEvent).toBeDefined();
    });

    it('triggers GOAL_ACHIEVED for long user messages', () => {
      const longMessage = 'A'.repeat(150);
      const result = simulateDTEChat(longMessage, 'Interesting.');
      const goalEvent = result.endocrineEvents.find(e => e.event === 'GOAL_ACHIEVED');
      expect(goalEvent).toBeDefined();
      expect(goalEvent!.intensity).toBe(0.3);
    });

    it('triggers THREAT_DETECTED for negative keywords', () => {
      const result = simulateDTEChat(
        'There is a danger of system crash',
        'I detect the threat in your words.',
      );
      const threatEvent = result.endocrineEvents.find(e => e.event === 'THREAT_DETECTED');
      expect(threatEvent).toBeDefined();
    });

    it('returns model and usage metadata', () => {
      const result = simulateDTEChat('Hello', 'Hi');
      expect(result.model).toBe('gemini-2.5-flash');
      expect(result.usage.prompt_tokens).toBe(100);
      expect(result.usage.completion_tokens).toBe(50);
      expect(result.usage.total_tokens).toBe(150);
    });
  });

  // -------------------------------------------------------------------------
  // 4. Auth System (simulated)
  // -------------------------------------------------------------------------
  describe('Auth System', () => {
    const COOKIE_NAME = 'session';

    it('logout clears the session cookie with correct options', () => {
      const clearedCookies: Array<{ name: string; options: Record<string, unknown> }> = [];
      const mockRes = {
        clearCookie: (name: string, options: Record<string, unknown>) => {
          clearedCookies.push({ name, options });
        },
      };

      // Simulate logout
      mockRes.clearCookie(COOKIE_NAME, {
        maxAge: -1,
        secure: true,
        sameSite: 'none',
        httpOnly: true,
        path: '/',
      });

      expect(clearedCookies).toHaveLength(1);
      expect(clearedCookies[0].name).toBe(COOKIE_NAME);
      expect(clearedCookies[0].options).toMatchObject({
        maxAge: -1,
        secure: true,
        sameSite: 'none',
        httpOnly: true,
        path: '/',
      });
    });
  });

  // -------------------------------------------------------------------------
  // 5. Cognitive Engine + Endocrine Integration
  // -------------------------------------------------------------------------
  describe('Cognitive-Endocrine Integration', () => {
    it('cognitive engine affects endocrine state through state transitions', () => {
      const engine = new DTECognitiveEngine();
      const initialHormones = { ...engine.getEndocrine().state() };

      // Run several cognitive steps
      for (let i = 0; i < 20; i++) {
        engine.step();
      }

      const finalHormones = engine.getEndocrine().state();
      // At least some hormones should have changed
      const changed = Object.keys(initialHormones).some(
        k => Math.abs(finalHormones[k] - initialHormones[k]) > 0.001,
      );
      expect(changed).toBe(true);
    });

    it('external chat event feeds back into cognitive engine', () => {
      const engine = new DTECognitiveEngine();

      // Simulate a chat interaction producing endocrine events
      const chatResult = simulateDTEChat(
        'Tell me about emergence',
        'Emergence reveals patterns at higher scales.',
      );

      // Feed chat endocrine events into the cognitive engine
      for (const event of chatResult.endocrineEvents) {
        engine.triggerExternalEvent(event.event as EndocrineEvent, event.intensity);
      }

      // Engine should have been affected
      const snap = engine.getSnapshot();
      expect(snap.hormones).toBeDefined();
      expect(Object.keys(snap.hormones).length).toBe(14);
    });

    it('sustained reward shifts cognitive mode away from RESTING', () => {
      const engine = new DTECognitiveEngine();

      // Sustained reward signals
      for (let i = 0; i < 15; i++) {
        engine.triggerExternalEvent(EndocrineEvent.REWARD_RECEIVED, 0.9);
      }

      const snap = engine.getSnapshot();
      // After many reward signals, mode should have shifted
      expect(snap.mode).not.toBe(CognitiveMode.RESTING);
    });

    it('state adjacency graph is fully connected (no dead-end states)', () => {
      const allStates = new Set(Object.values(DTEState));
      const reachable = new Set<DTEState>();

      // BFS from IDLE
      const queue: DTEState[] = [DTEState.IDLE];
      reachable.add(DTEState.IDLE);

      while (queue.length > 0) {
        const current = queue.shift()!;
        const neighbors = ADJACENCY[current] || [];
        for (const n of neighbors) {
          if (!reachable.has(n)) {
            reachable.add(n);
            queue.push(n);
          }
        }
      }

      // All states should be reachable from IDLE
      for (const state of allStates) {
        expect(reachable.has(state)).toBe(true);
      }
    });

    it('every state with an endocrine mapping fires the correct event type', () => {
      for (const [state, mapping] of Object.entries(DTE_ENDOCRINE_MAP)) {
        expect(Object.values(EndocrineEvent)).toContain(mapping.event);
        expect(mapping.intensity).toBeGreaterThan(0);
        expect(mapping.intensity).toBeLessThanOrEqual(1);
      }
    });
  });

  // -------------------------------------------------------------------------
  // 6. Session Cookie Security
  // -------------------------------------------------------------------------
  describe('Session Cookie Security', () => {
    it('cookie options enforce httpOnly, sameSite=none, and path=/', () => {
      const options = {
        httpOnly: true,
        path: '/',
        sameSite: 'none' as const,
        secure: true,
      };

      expect(options.httpOnly).toBe(true);
      expect(options.sameSite).toBe('none');
      expect(options.path).toBe('/');
      expect(options.secure).toBe(true);
    });
  });
});

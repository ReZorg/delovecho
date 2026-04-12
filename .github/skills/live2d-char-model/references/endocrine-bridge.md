# Endocrine-Expression Bridge

Maps the 16-channel virtual endocrine hormone state to Live2D Cubism expressions and motions. This is the ⊗ composition point where the virtual-endocrine-system meets the live2d-avatar renderer.

## TypeScript Implementation

```typescript
// packages/avatar/src/endocrine-bridge.ts

/** Hormone concentrations keyed by hormone name */
interface EndocrineState {
  concentrations: Record<string, number>;
}

/** Cognitive modes emergent from hormone space */
type CognitiveMode =
  | 'RESTING' | 'EXPLORATORY' | 'FOCUSED' | 'STRESSED' | 'SOCIAL'
  | 'REFLECTIVE' | 'VIGILANT' | 'MAINTENANCE' | 'REWARD' | 'THREAT';

/** A single expression rule from the character manifest */
interface ExpressionRule {
  expression: string;
  conditions: Record<string, { op: '>' | '<'; threshold: number }>;
}

/** Character manifest type (subset relevant to bridge) */
interface CharacterManifest {
  expressions: Record<string, Record<string, string>>;
  motions: Record<string, string[]>;
}

/**
 * EndocrineExpressionBridge
 *
 * Evaluates hormone state against character-specific expression rules
 * and applies the best-matching Cubism expression to the Live2D model.
 */
export class EndocrineExpressionBridge {
  private rules: ExpressionRule[];
  private model: any; // PIXI.live2d.Live2DModel
  private lastExpression: string | null = null;
  private lastMotion: string | null = null;

  constructor(manifest: CharacterManifest, model: any) {
    this.model = model;
    this.rules = Object.entries(manifest.expressions).map(
      ([expr, conditions]) => ({
        expression: expr,
        conditions: Object.fromEntries(
          Object.entries(conditions).map(([hormone, rule]) => {
            const op = (rule as string).startsWith('>') ? '>' as const : '<' as const;
            const threshold = parseFloat((rule as string).slice(1));
            return [hormone, { op, threshold }];
          })
        ),
      })
    );
  }

  /**
   * Evaluate hormone state → best matching expression.
   * Scores by sum of |value - threshold| for all met conditions.
   * Returns null if no expression has all conditions met.
   */
  evaluate(state: EndocrineState): string | null {
    let bestMatch: string | null = null;
    let bestScore = 0;

    for (const rule of this.rules) {
      let score = 0;
      let allMet = true;

      for (const [hormone, { op, threshold }] of Object.entries(rule.conditions)) {
        const value = state.concentrations[hormone] ?? 0;
        const met = op === '>' ? value > threshold : value < threshold;
        if (!met) {
          allMet = false;
          break;
        }
        score += Math.abs(value - threshold);
      }

      if (allMet && score > bestScore) {
        bestScore = score;
        bestMatch = rule.expression;
      }
    }
    return bestMatch;
  }

  /** Apply expression to Live2D model (debounced: only changes on new expression) */
  apply(state: EndocrineState): void {
    const expr = this.evaluate(state);
    if (expr && expr !== this.lastExpression) {
      this.model.expression(expr);
      this.lastExpression = expr;
    }
  }

  /** Map cognitive mode → motion group (debounced) */
  applyMotion(mode: CognitiveMode, manifest: CharacterManifest): void {
    for (const [motionGroup, modes] of Object.entries(manifest.motions)) {
      if (modes.includes(mode)) {
        if (motionGroup !== this.lastMotion) {
          this.model.motion(motionGroup);
          this.lastMotion = motionGroup;
        }
        return;
      }
    }
  }

  /** Reset bridge state (e.g., on character switch) */
  reset(): void {
    this.lastExpression = null;
    this.lastMotion = null;
  }
}
```

## OCEAN → Endocrine Sensitivity Mapping

Wire the Vorticog Big Five personality into endocrine sensitivity multipliers:

```typescript
function computeSensitivity(
  ocean: { openness: number; conscientiousness: number; extraversion: number;
           agreeableness: number; neuroticism: number },
  base: { reward: number; threat: number; social: number; novelty: number }
) {
  return {
    reward:  base.reward  * (1 + ocean.extraversion / 200),
    threat:  base.threat  * (1 + ocean.neuroticism / 200),
    social:  base.social  * (1 + ocean.agreeableness / 200),
    novelty: base.novelty * (1 + ocean.openness / 200),
  };
}
```

## OCEAN → Needs Decay Mapping

Wire personality into SimsFreePlay needs decay rates:

```typescript
function computeNeedsDecay(
  ocean: { openness: number; conscientiousness: number; extraversion: number;
           agreeableness: number; neuroticism: number },
  baseDecay: Record<string, number>
) {
  return {
    hunger:  baseDecay.hunger,
    energy:  baseDecay.energy  * (1 + ocean.neuroticism / 200),    // anxious → tires faster
    hygiene: baseDecay.hygiene * (1 - ocean.conscientiousness / 400), // organized → slower decay
    social:  baseDecay.social  * (1 + ocean.extraversion / 200),   // extraverted → needs more social
    fun:     baseDecay.fun     * (1 + ocean.openness / 200),       // curious → bores faster
    bladder: baseDecay.bladder,
  };
}
```

## DTE Cognitive State → Endocrine Event Adapter

Wire the DeltEcho `DTESimulation` cognitive state transitions into endocrine events:

```typescript
const DTE_ENDOCRINE_MAP: Record<string, { event: string; intensity: number }> = {
  'Recursive Expansion':           { event: 'NOVELTY_ENCOUNTERED', intensity: 0.6 },
  'Novel Insights':                { event: 'REWARD_RECEIVED',     intensity: 0.7 },
  'Entropy Threshold':             { event: 'THREAT_DETECTED',     intensity: 0.5 },
  'Synthesis Phase':               { event: 'GOAL_ACHIEVED',       intensity: 0.6 },
  'Self-Sealing Loop':             { event: 'ERROR_DETECTED',      intensity: 0.4 },
  'Knowledge Integration':         { event: 'SOCIAL_BOND_SIGNAL',  intensity: 0.5 },
  'Self-Reference Point':          { event: 'NOVELTY_ENCOUNTERED', intensity: 0.4 },
  'Pattern Recognition':           { event: 'REWARD_RECEIVED',     intensity: 0.5 },
  'Evolutionary Pruning':          { event: 'THREAT_DETECTED',     intensity: 0.3 },
  'External Validation Triggered': { event: 'SOCIAL_BOND_SIGNAL',  intensity: 0.6 },
};

function onDTEStateChange(newState: string, endo: EndocrineSystem, sensitivity: any): void {
  const mapping = DTE_ENDOCRINE_MAP[newState];
  if (mapping) {
    const adjustedIntensity = mapping.intensity * (sensitivity[mapping.event] ?? 1.0);
    endo.signalEvent(mapping.event, adjustedIntensity);
  }
}
```

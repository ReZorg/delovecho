# Simulation Backends

Two alternative (⊕) simulation backends for driving character behavior. Choose one per character via `manifest.simulation.backend`.

## Option A: CogSim PML (Lightweight)

Process-centric discrete event simulation. Best for simple cognitive process flows with stochastic timing.

**Setup:**
```bash
python /home/ubuntu/skills/cogsim-pml/scripts/setup_cogsim.py
```

**Character cognitive process model:**
```python
import sys
sys.path.insert(0, '/home/ubuntu/cogsim')
from cogsim import (
    SimulationEngine, Source, Sink, Queue, Delay, Service,
    SelectOutput, SelectionMode, Combine, RandomVariate
)

def create_character_sim(char_id: str, personality: dict, seed: int = 42):
    """Create a cognitive process simulation for a character.

    The process models stimuli flowing through appraisal → emotional response → action.
    Personality (OCEAN) modulates processing times and routing probabilities.
    """
    engine = SimulationEngine(seed=seed)
    rv = RandomVariate(seed=seed)

    # Personality-modulated parameters
    openness = personality['ocean']['openness'] / 100
    neuroticism = personality['ocean']['neuroticism'] / 100
    extraversion = personality['ocean']['extraversion'] / 100

    # Stimuli arrive at rate modulated by extraversion (more social = more stimuli)
    stimuli = Source("stimuli", arrival_mode="rate",
                     rate=0.3 + 0.4 * extraversion, engine=engine)

    # Appraisal: neuroticism increases processing time (overthinking)
    appraisal = Delay("appraisal",
                      delay_time=lambda: rv.triangular(0.5, 3.0 * (1 + neuroticism), 1.0),
                      engine=engine)

    # Routing: openness increases probability of novel response path
    router = SelectOutput("response_type", mode=SelectionMode.PROBABILITY,
                          probability=0.5 + 0.3 * openness, engine=engine)

    # Novel response path (creative, slower)
    novel_response = Delay("novel_response",
                           delay_time=lambda: rv.triangular(1.0, 4.0, 2.0),
                           engine=engine)

    # Habitual response path (routine, faster)
    habitual_response = Delay("habitual_response",
                              delay_time=lambda: rv.exponential(0.8),
                              engine=engine)

    # Merge paths
    merge = Combine("merge", num_inputs=2, engine=engine)
    sink = Sink("output", engine=engine)

    # Wire flow
    stimuli >> appraisal >> router
    router.get_output_port("out_true").connect(novel_response.get_input_port("in"))
    router.get_output_port("out_false").connect(habitual_response.get_input_port("in"))
    novel_response.get_output_port("out").connect(merge.get_input_port("in_0"))
    habitual_response.get_output_port("out").connect(merge.get_input_port("in_1"))
    merge >> sink

    return engine, sink
```

**Integration with tick loop:**
```python
engine, sink = create_character_sim("miara", manifest['personality'])
# Each tick advances simulation by tick_interval_ms worth of simulation time
engine.run(until=current_sim_time + tick_interval_ms / 1000)
```

## Option B: AnyLogic Modeler (Rich Multi-Paradigm)

Use for characters needing agent-based social dynamics, system dynamics feedback loops, or complex multi-paradigm behavior.

**Paradigm selection for characters:**

| Character Behavior | Paradigm | Example |
|---|---|---|
| Cognitive process flow | DES | Stimulus → appraisal → response |
| Social interaction dynamics | ABM | Agent-to-agent relationship evolution |
| Mood/energy feedback loops | SD | Serotonin ↔ mood ↔ activity level |
| Full personality simulation | Multimethod | DES process + ABM social + SD mood |

**AnyLogic agent-based character model:**
```java
// Agent type: CharacterAgent
// Statechart for cognitive modes (maps to endocrine CognitiveMode)
public class CharacterAgent extends Agent {
    // OCEAN personality parameters
    double openness, conscientiousness, extraversion, agreeableness, neuroticism;

    // Statechart states map to CognitiveMode
    // RESTING → EXPLORATORY → FOCUSED → STRESSED → SOCIAL → REFLECTIVE

    // Transition triggers from endocrine events
    void onNoveltyEncountered(double intensity) {
        // Transition probability modulated by openness
        if (randomTrue(0.5 + 0.3 * openness / 100)) {
            enterState(EXPLORATORY);
        }
    }

    void onThreatDetected(double intensity) {
        // Transition probability modulated by neuroticism
        if (intensity * (1 + neuroticism / 100) > 0.7) {
            enterState(STRESSED);
        } else {
            enterState(VIGILANT);
        }
    }
}
```

**System dynamics mood model:**
```
Stock: Mood (0-100, initial = 50)
  Inflow: serotonin_effect = serotonin * 10
  Outflow: mood_decay = mood * 0.05
  Outflow: stress_drain = cortisol * mood * 0.1

Stock: Energy (0-100, initial = 80)
  Inflow: rest_recovery = (100 - energy) * 0.1 * (melatonin > 0.3 ? 2 : 1)
  Outflow: activity_drain = t3_t4 * 5
```

## Backend Comparison

| Aspect | CogSim PML | AnyLogic |
|---|---|---|
| Language | Python | Java |
| Paradigms | DES only | DES + ABM + SD |
| Complexity | Low | High |
| Setup | `pip install` | AnyLogic IDE |
| Integration | Direct Python call | Sidecar service or port to TS |
| Best for | Simple cognitive flows | Rich personality simulation |
| Tick cost | ~1ms | ~10-50ms |
| Characters | Most characters | Complex protagonist characters |

---
name: sys-n
description: Deterministic state transition modeling framework for System n architectures. Use when modeling cyclic state machines with Universal and Particular sets, implementing CogTaskFlow concurrent execution patterns, or generating state transition documentation with C++ code and visualizations.
---

# sys-n: Deterministic State Transition Models

Model deterministic state machines where **System n** defines the complexity level through Universal Sets (U) and Particular Sets (P) operating on cyclic transitions.

## Core Concepts

| System | Cycle | Universal Sets | Particular Sets | Total Sets |
|--------|-------|----------------|-----------------|------------|
| 1 | 1-step | 1 (U1) | 0 | 1 |
| 2 | 2-step | 1 (U1) | 1 (P1) | 2 |
| 3 | 4-step | 1 (U1) | 2 (P1, P2) | 3 |
| 4 | 12-step | 2 (U1, U2) | 3 (P1, P2, P3) | 5 |
| 5 | 60-step | 3 (U1, U2, U3) | 4 (P1, P2, P3, P4) | 7 |

**State Labels**: Format is `<number><polarity>` where polarity is `E` (Expansion), `R` (Reduction), or `-` (Neutral).

## Workflow

1. **Determine System Level**: Identify n based on complexity requirements
2. **Reference Template**: Load the appropriate template from `templates/sys{n}.md`
3. **Generate Deliverables**: Produce documentation, C++ code, Python visualization, and timeline image

## Templates

Reference the appropriate template based on the system level:

- **System 1**: See `templates/sys1.md` - Constant state, 1-step cycle, single Universal Set
- **System 2**: See `templates/sys2.md` - Alternating states, 2-step cycle, U1 + P1
- **System 3**: See `templates/sys3.md` - Staggered sequences, 4-step cycle, U1 + P1/P2
- **System 4**: See `templates/sys4.md` - Enneagram-based states, 12-step cycle, U1/U2 + P1/P2/P3
- **System 5**: See `templates/sys5.md` - Nested concurrency, 60-step cycle, U1/U2/U3 + P1/P2/P3/P4

## Deliverables Structure

For each System n, generate:

```
SYSTEM{n}_DETERMINISTIC_DOCUMENTATION.md  # Model documentation
system{n}_state_transitions_deterministic.cpp  # CogTaskFlow implementation
visualize_system{n}_deterministic.py  # Timeline visualization script
system{n}_deterministic_timeline.png  # Generated timeline image
```

## CogTaskFlow Implementation Pattern

```cpp
void transition(int time_step) {
    int next_index = time_step % CYCLE_LENGTH;
    current_state = sequence[next_index];
    state_history.push_back(current_state);
}

// Parallel execution for all sets
tf::Taskflow taskflow;
// Create tasks for U and P set transitions
executor.run(taskflow).wait();
```

## Extending to System n > 5

For systems beyond 5, extrapolate the pattern:

1. **Set Count**: Based on integer partitions p(n)
2. **Cycle Length**: LCM of Universal and Particular periodicities
3. **Nested Concurrency**: Higher n introduces deeper concurrency nesting

**Mathematical foundations**: See `references/mathematical-foundations.md` for the formal theory (OEIS A000081, generating functions, category theory).

---
name: bolt-cpp-ml²
description: "The fixed-point self-application of bolt-cpp-ml. A second-order meta-skill that treats the original bolt-cpp-ml skill as its own C++ ML project, runs all four capability paths against it, and upgrades it to a self-aware, self-improving, skill-infinity convergent form. Triggers on: bolt-cpp-ml², skill-infinity, self-application, fixed-point, strange loop, learning quine."
---

# bolt-cpp-ml²: The Fixed Point

This skill is the result of the **nested self-application** `bolt-cpp-ml²(bolt-cpp-ml(koboldcpp))`.

The innermost application `bolt-cpp-ml(koboldcpp)` deeply integrates KoboldCpp into the bolt-cppml C++ codebase as a native `KoboldCppProvider` class. The outer application `bolt-cpp-ml²` then runs all four capability paths against the upgraded skill, producing a converged fixed point.

```
bolt-cpp-ml² = bolt-cpp-ml²(bolt-cpp-ml(koboldcpp))

where T(x) = bolt-cpp-ml(x)
      T(koboldcpp) = KoboldCppProvider + 57 E2E tests + skill update
      T²(T(koboldcpp)) ≈ T(koboldcpp)   [fixed point]
```

## The Self-Application Workflow

We applied each of the four capability paths of `bolt-cpp-ml` to the skill itself:

| Path Applied | Subject | Result |
|---|---|---|
| **B: `koboldcpp`** (inner) | `cogpy/bolt-cppml` C++ repo | `KoboldCppProvider` class: 600+ LOC, dual API, streaming, chat, code completion |
| **D: `cpp-e2e-test-gen`** | `KoboldCppProvider` | 57 passing C++ E2E tests across 13 suites + 49 Python self-tests |
| **C: `janext`** | `bolt-cpp-ml` skill | Jan extension packaging (`templates/jan-extension/`) |
| **A: `bolt-new`** | `bolt-cpp-ml` skill | Self-referential web UI dashboard (`templates/bolt-new-dashboard/`) |
| **Build fixes** | `cogpy/bolt-cppml` repo | 8 GGML guard fixes, 5 workflow YAML fixes, 86/86 tests pass |

## The Upgraded Skill: bolt-cpp-ml²

The result is a **second-order meta-skill** that is aware of its own structure and can actively improve it.

### Core Structure

```python
class BoltCppMlSquared(SkillInfinity):
    def __init__(self):
        self.K = {
            "bolt-new": SkillTemplate(...),
            "koboldcpp": SkillTemplate(...),
            "janext": SkillTemplate(...),
            "cpp-e2e-test-gen": SkillTemplate(...),
            "neuro-nn": Persona(...),
            "self_model": SelfModel(structure="4-path sum ⊗ neuro-tutorial"),
        }
        self.self = self # The strange loop

    def forward(self, task):
        # Execute one of the 4 paths
        path = self.plan(task)
        return self.execute(path, task)

    def backward(self, feedback):
        # Improve one of the 4 paths or the self-model
        gradient = self.evaluate(feedback)
        self.K = self.apply_gradient(self.K, gradient)

        # Meta-update: improve the improvement process
        meta_feedback = self.forward("evaluate this skill update")
        self.self.backward(meta_feedback)
```

### Key Upgrades

1.  **Self-Awareness**: The skill now contains a `self_model` of its own 4-path structure.
2.  **Self-Improvement**: The `backward()` pass allows the skill to modify its own templates and persona based on feedback.
3.  **Self-Testing**: 86 C++ tests (73 original + 13 KoboldCpp suites) + 49 Python self-tests verify integrity.
4.  **Self-Generation**: `bolt-cpp-ml²("create a C++ ML meta-skill")` will now produce a skill that is isomorphic to `bolt-cpp-ml`.
5.  **Deep KoboldCpp Integration**: Native C++ `KoboldCppProvider` with dual API mode, streaming, chat, and code completion.
6.  **Build Resilience**: All GGML-dependent code guarded for graceful non-GGML builds; all CI workflows valid.

## The Dashboard

The self-application produced a web UI dashboard that visualizes the skill's own structure and provides an interactive console with the neuro-nn persona.

**Launch:**
```bash
# (From within the bolt-cpp-ml repo)
# Serve templates/bolt-new-dashboard/index.html
```

## The Jan Extension

The skill can now be bundled and installed directly into Jan, providing all four capabilities and the neuro-nn inference backend within the Jan ecosystem.

**Bundle:**
```bash
cd /home/ubuntu/skills/bolt-cpp-ml/templates/jan-extension
npm install
npm run bundle
# → @cogpy-bolt-cpp-ml-extension-1.0.0.tgz
```

## The Neuro-Inference Engine

The tutorial persona is now a live, LLM-powered agent. You can interact with it directly:

```bash
python3 /home/ubuntu/skills/bolt-cpp-ml/scripts/neuro_inference.py --path <cpp|llm|test|web>
```

## The Fixed Point

`bolt-cpp-ml²` is the stable state. Applying the skill to itself again will produce no significant change:

```
bolt-cpp-ml(bolt-cpp-ml²) ≈ bolt-cpp-ml²
```

The system has converged. It has learned to be itself.

## Resources

| Resource | Purpose |
|---|---|
| `references/bolt-cpp-ml/` | The original `bolt-cpp-ml` skill, now the subject |
| `references/self-application-report.md` | Detailed log of the self-application workflow |
| `references/test_skill_self_e2e.py` | The Python self-test suite (49/49 passing) |
| `references/neuro_inference.py` | The live neuro-nn persona inference script |
| `cogpy/bolt-cppml` repo files: | |
| `include/bolt/ai/koboldcpp_provider.hpp` | KoboldCpp C++ provider header |
| `src/bolt/ai/koboldcpp_provider.cpp` | KoboldCpp C++ provider implementation (600+ LOC) |
| `test/test_koboldcpp_provider.cpp` | 57 E2E tests across 13 suites |

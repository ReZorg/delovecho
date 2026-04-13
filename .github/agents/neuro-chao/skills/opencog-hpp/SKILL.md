---
name: opencog-hpp
description: "Header-only C++11 implementations of all OpenCog repositories under namespace oc::* with zero external dependencies. Covers cogutil, atomspace, attention, cogserver, ure, pln, matrix, and atomspace-cog."
---

# OpenCog Header-Only C++11 Library (oc::*)

Header-only C++11 reimplementation of the OpenCog AGI framework. All modules live under `namespace oc::*`, require zero external dependencies, and compile with `g++ -std=c++11 -I include -pthread`.

## Quick Start

```cpp
#include <oc/oc.hpp>           // everything
// or pick individual modules:
#include <oc/pln/pln.hpp>      // PLN (pulls atomspace + ure + util)
#include <oc/matrix/matrix.hpp> // sparse matrix (pulls atomspace + util)
```

Compile: `g++ -std=c++11 -I include -pthread your_file.cpp -o binary`

## Module Map

| Header | Namespace | OpenCog Repo | Key Classes |
|--------|-----------|-------------|-------------|
| `oc/util/util.hpp` | `oc::util` | cogutil | Logger, RandGen, Config, concurrent_queue, SigSlot, oc_assert |
| `oc/atomspace/atomspace.hpp` | `oc` | atomspace | AtomSpace, Atom, Node, Link, Handle, TruthValue, Value, TypeRegistry |
| `oc/attention/attention.hpp` | `oc::attention` | attention | AttentionBank, ECANRunner, ImportanceDiffusion, HebbianUpdating, ForgettingAgent |
| `oc/server/server.hpp` | `oc::server` | cogserver | CogServer, Shell, SchemeShell, RequestManager, ModuleManager |
| `oc/ure/ure.hpp` | `oc::ure` | ure | Unifier, Substitution, Rule, RuleSet, ForwardChainer, BackwardChainer |
| `oc/pln/pln.hpp` | `oc::pln` | pln | PLNReasoner, formulas (deduction, induction, abduction, revision, modus_ponens) |
| `oc/matrix/matrix.hpp` | `oc::matrix` | matrix | PairAPI, Marginals, Similarity, MutualInformation, BatchSimilarity |
| `oc/persist/persist.hpp` | `oc::persist` | atomspace-cog | Serializer, MemoryStorageNode, ProxyNode, FrameServer, CogChannel |

## Dependency Order

```
oc::util  →  oc::atomspace  →  oc::attention
                             →  oc::server
                             →  oc::ure  →  oc::pln
                             →  oc::matrix
                             →  oc::persist
```

Each header includes its dependencies automatically.

## Usage Patterns

### AtomSpace + PLN Reasoning

```cpp
oc::AtomSpace as;
oc::pln::PLNReasoner r(as);
r.store_inheritance("cat", "mammal", 0.95, 0.9);
r.store_inheritance("mammal", "animal", 0.99, 0.95);
auto conclusions = r.deduce_all();  // deduces cat→animal
auto tv = r.query_inheritance("cat", "animal");
```

### ECAN Attention Allocation

```cpp
oc::attention::ECANRunner ecan(as);
ecan.bank().stimulate(handle, 100);
ecan.bank().set_af_threshold(50);
ecan.run(10);  // 10 cognitive cycles
auto focus = ecan.bank().get_attentional_focus();
```

### Sparse Matrix / MI

```cpp
oc::matrix::PairAPI pairs(as, "word-pair");
pairs.set_pair(w1, w2, 50.0);
oc::matrix::Marginals marg(pairs);
oc::matrix::MutualInformation mi(pairs, marg);
double pmi = mi.pmi(w1, w2);
```

### Serialization / Persistence

```cpp
oc::persist::Serializer ser(as);
std::string sexpr = ser.serialize_full(handle);
oc::AtomSpace as2;
ser.deserialize(sexpr, as2);
```

### CogServer + SchemeShell

```cpp
oc::server::CogServer srv(as);
srv.scheme_shell().eval("(cog-new-node 'ConceptNode \"test\")");
srv.shell().eval("stats");
```

## Files

```
opencog-hpp/
├── SKILL.md
└── templates/
    ├── CMakeLists.txt
    ├── README.md
    ├── include/oc/
    │   ├── oc.hpp              (umbrella)
    │   ├── util/util.hpp       (cogutil)
    │   ├── atomspace/atomspace.hpp
    │   ├── attention/attention.hpp
    │   ├── server/server.hpp
    │   ├── ure/ure.hpp
    │   ├── pln/pln.hpp
    │   ├── matrix/matrix.hpp
    │   └── persist/persist.hpp
    └── test/test_all.cpp       (89 tests, 0 failures)
```

## Test Suite

89 tests across 9 sections (util, atomspace, attention, server, ure, pln, matrix, persist, integration). Run:

```bash
cd templates && g++ -std=c++11 -I include -pthread test/test_all.cpp -o test_all && ./test_all
```

## Triggers

Use this skill when working with OpenCog header-only libraries, portable AtomSpace implementations, PLN reasoning, ECAN attention, URE rule engines, sparse matrix operations over hypergraphs, or any C++11 project needing cognitive architecture primitives without external dependencies.

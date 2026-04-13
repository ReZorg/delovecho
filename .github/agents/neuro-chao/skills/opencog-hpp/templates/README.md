# OpenCog Header-Only C++11 Library

Header-only C++11 reimplementation of the [OpenCog](https://github.com/opencog) AGI framework under `namespace oc::*`. Zero external dependencies.

## Modules

| Module | Namespace | Source Repository | Lines |
|--------|-----------|------------------|-------|
| cogutil | `oc::util` | [opencog/cogutil](https://github.com/opencog/cogutil) | 528 |
| atomspace | `oc` | [opencog/atomspace](https://github.com/opencog/atomspace) | 657 |
| attention | `oc::attention` | [opencog/attention](https://github.com/opencog/attention) | 526 |
| cogserver | `oc::server` | [opencog/cogserver](https://github.com/opencog/cogserver) | 527 |
| ure | `oc::ure` | [opencog/ure](https://github.com/opencog/ure) | 380 |
| pln | `oc::pln` | [opencog/pln](https://github.com/opencog/pln) | 338 |
| matrix | `oc::matrix` | [opencog/matrix](https://github.com/opencog/matrix) | 477 |
| atomspace-cog | `oc::persist` | [opencog/atomspace-cog](https://github.com/opencog/atomspace-cog) | 519 |

**Total: 3,986 lines of C++11** (plus 524 lines of tests)

## Build

```bash
g++ -std=c++11 -I include -pthread your_file.cpp -o binary
```

Or with CMake:

```bash
mkdir build && cd build && cmake .. && make && ctest
```

## Usage

```cpp
#include <oc/oc.hpp>  // everything

int main() {
    oc::AtomSpace as;
    oc::Handle cat = as.add_node(oc::types::CONCEPT_NODE, "cat");
    oc::Handle animal = as.add_node(oc::types::CONCEPT_NODE, "animal");
    as.add_link(oc::types::INHERITANCE_LINK, {cat, animal},
                oc::TruthValue(0.95, 0.9));

    oc::pln::PLNReasoner reasoner(as);
    reasoner.store_inheritance("mammal", "animal", 0.99, 0.95);
    reasoner.store_inheritance("cat", "mammal", 0.95, 0.9);
    auto conclusions = reasoner.deduce_all();
}
```

## Tests

89 tests, 0 failures across all 8 modules plus integration tests.

## License

AGPL-3.0 (matching OpenCog)

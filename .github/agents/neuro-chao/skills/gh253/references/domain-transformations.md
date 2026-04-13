# Domain Transformations Reference

## Overview

The gh253 pattern language maps Christopher Alexander's architectural patterns to the domain of GitHub. This document provides a comprehensive reference for these transformations.

## Scale Mappings

| APL253 Scale | GitHub Scale | Pattern Range | Description |
|--------------|--------------|---------------|-------------|
| Regions | Enterprises | 1-94 | Autonomous spheres of culture, governance, and collaboration |
| Towns | Organisations | 95-204 | Collections of repositories forming a cohesive whole |
| Buildings | Repositories | 205-253 | The fundamental units of code, documentation, and collaboration |

## Core Concept Mappings

### Spatial Concepts

| Architecture | GitHub | Description |
|--------------|--------|-------------|
| region | enterprise | Autonomous governance sphere |
| town | organisation | Community with shared identity |
| city | organisation | Large-scale organisation |
| village | team | Small collaborative unit |
| neighborhood | team | Close-knit working group |
| community | developer_community | Shared purpose group |
| building | repository | Functional code unit |
| house | repository | Personal or team repo |
| room | directory | Contained namespace |
| space | namespace | Logical grouping |

### Structural Concepts

| Architecture | GitHub | Description |
|--------------|--------|-------------|
| wall | module_boundary | Separation between concerns |
| door | api_endpoint | Entry/exit point |
| window | interface | View into functionality |
| column | core_module | Load-bearing component |
| beam | dependency | Structural connection |
| foundation | framework | Base infrastructure |
| structure | architecture | Overall design |
| roof | overview | Top-level documentation |
| floor | layer | Abstraction level |

### Flow Concepts

| Architecture | GitHub | Description |
|--------------|--------|-------------|
| path | workflow | Sequence of actions |
| street | integration_pipeline | Main data flow |
| entrance | readme | Primary entry point |
| gateway | api_gateway | Central access point |
| arcade | shared_library | Reusable components |

### Social Concepts

| Architecture | GitHub | Description |
|--------------|--------|-------------|
| citizen | contributor | Active participant |
| family | maintainer_team | Core ownership group |
| guest | external_contributor | Outside collaborator |
| worker | bot | Automated agent |
| craftsman | developer | Skilled builder |
| architect | architect | System designer |
| builder | devops_engineer | Infrastructure specialist |

### Functional Spaces

| Architecture | GitHub | Description |
|--------------|--------|-------------|
| garden | documentation | Cultivated knowledge |
| plaza | discussion_forum | Open conversation space |
| market | package_registry | Exchange of components |
| workshop | development_environment | Creation space |
| office | project_board | Work coordination |
| library | documentation_site | Knowledge repository |
| school | learning_resources | Educational content |
| hospital | issue_tracker | Problem resolution |
| police | security_scanning | Protection services |

## Construction-Level Mappings (Patterns 205-253)

These patterns map the "atoms" of building to the atomic components of repositories:

| Pattern | APL253 | gh253 | Description |
|---------|--------|-------|-------------|
| 205 | Structure Follows Social Spaces | Structure Follows Team Spaces | Conway's Law alignment |
| 206 | Efficient Structure | Efficient Codebase | Optimized organization |
| 207 | Good Materials | Good Dependencies | Quality components |
| 208 | Gradual Stiffening | Gradual Formalization | Progressive structure |
| 209 | Roof Layout | README Layout | Overview structure |
| 210 | Floor and Ceiling Layout | Package Structure | Layer organization |
| 211 | Thickening the Outer Walls | Hardening the API | Security boundaries |
| 212 | Columns at the Corners | Core Modules | Essential components |
| 213 | Final Column Distribution | Final Module Distribution | Balanced architecture |
| 214 | Root Foundations | Base Classes | Fundamental types |
| 215 | Ground Floor Slab | Foundation Layer | Base infrastructure |
| 216 | Box Columns | Container Components | Encapsulation patterns |
| 217 | Perimeter Beams | Boundary Validators | Edge validation |
| 218 | Wall Membranes | Interface Contracts | API specifications |
| 219 | Floor-Ceiling Vaults | Abstraction Layers | Level separation |
| 220 | Roof Vaults | Top-Level Exports | Public surface |
| 221 | Natural Doors and Windows | Natural Entry Points | Intuitive access |
| 222 | Low Sill | Low Barrier to Entry | Easy onboarding |
| 223 | Deep Reveals | Detailed Documentation | Rich context |
| 224 | Low Doorway | Minimal Interface | Simple API |
| 225 | Frames as Thickened Edges | Interfaces as Contracts | Formal boundaries |
| 226 | Column Place | Singleton Pattern | Unique instances |
| 227 | Column Connections | Module Dependencies | Component links |
| 228 | Stair Vault | Recursive Calls | Self-reference |
| 229 | Duct Space | Logging Infrastructure | Observability |
| 230 | Radiant Heat | Event Propagation | Message flow |
| 231 | Dormer Windows | Debug Endpoints | Inspection points |
| 232 | Roof Caps | Version Tags | Release markers |
| 233 | Floor Surface | Base Types | Fundamental types |
| 234 | Lapped Outside Walls | Public API | External interface |
| 235 | Soft Inside Walls | Internal API | Private interface |
| 236 | Windows Which Open Wide | Extensible Interfaces | Plugin points |
| 237 | Solid Doors with Glass | Typed Interfaces | Type-safe APIs |
| 238 | Filtered Light | Sanitized Input | Input validation |
| 239 | Small Panes | Small Functions | Single responsibility |
| 240 | Half-Inch Trim | Consistent Formatting | Code style |
| 241 | Seat Spots | Breakpoints | Debug locations |
| 242 | Front Door Bench | Welcome Message | Greeting content |
| 243 | Sitting Wall | Guard Clauses | Early returns |
| 244 | Canvas Roofs | Temporary Solutions | Quick fixes |
| 245 | Raised Flowers | Highlighted Features | Prominent functionality |
| 246 | Climbing Plants | Progressive Enhancement | Graceful upgrades |
| 247 | Paving with Cracks | Graceful Degradation | Fault tolerance |
| 248 | Soft Tile and Brick | Flexible Types | Dynamic typing |
| 249 | Ornament | Documentation | Decorative clarity |
| 250 | Warm Colors | Branding | Visual identity |
| 251 | Different Chairs | Different Tools | Tool diversity |
| 252 | Pools of Light | Code Comments | Illuminating notes |
| 253 | Things from Your Life | Personal Touches | Individual character |

## Dimension Mappings

The gh253 patterns can be viewed through multiple dimensions:

| Dimension | Domain | Application |
|-----------|--------|-------------|
| dim0 | Archetypal | Abstract patterns with GitHub-specific placeholders |
| dim2 | Technical | Code architecture, repository structure |
| dim3 | Social | Team organization, community governance |
| dim4 | Conceptual | Knowledge management, documentation |
| dim5 | Interpersonal | Developer experience, collaboration |

## Example Transformations

### Pattern 1: INDEPENDENT REGIONS → INDEPENDENT ENTERPRISES

| Aspect | Architecture | GitHub |
|--------|--------------|--------|
| Scale | 2-10 million people | Large developer ecosystem |
| Governance | Self-governing region | Autonomous enterprise |
| Boundaries | Natural geography | Technical domain |
| Economy | Regional economy | Package ecosystem |

### Pattern 107: WINGS OF LIGHT → MODULAR DESIGN

| Aspect | Architecture | GitHub |
|--------|--------------|--------|
| Structure | Narrow building wings | Focused modules |
| Light | Natural illumination | Code visibility |
| Access | Multiple exposures | Multiple interfaces |
| Purpose | Human comfort | Developer understanding |

### Pattern 205: STRUCTURE FOLLOWS SOCIAL SPACES → STRUCTURE FOLLOWS TEAM SPACES

| Aspect | Architecture | GitHub |
|--------|--------------|--------|
| Principle | Form follows function | Conway's Law |
| Units | Social spaces | Team boundaries |
| Structure | Physical layout | Directory structure |
| Alignment | Human activity | Team responsibility |

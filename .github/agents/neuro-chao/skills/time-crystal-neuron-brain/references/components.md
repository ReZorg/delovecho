# Time Crystal Neuron Components Reference

## Temporal Scales

Components are organized by characteristic oscillation periods:

| Scale | Period | Components |
|-------|--------|------------|
| Ultra-fast | 8ms | Ax, Pr-Ch(3) |
| Fast | 26ms | Io-Ch, Li, Ax |
| Medium-fast | 52ms | Me, Ac, Li |
| Medium | 0.11s | AIS[3], An-n, En-re-Mi, P-As, An |
| Medium-slow | 0.16s | Ch-Co, Ac, Se-n, Br, PNN |
| Slow | 0.25s | Ca, Mu-p, Fi-lo, Ax-d, Ax-s, Ax-s-d, Sn-cl-co |
| Very-slow | 0.33s | Rh, Ep, Io, Mi-fm, A, Jn, Soma, β-sp-A, Fi-fe, Mo-n, Mu-in, Br, Li |
| Ultra-slow | 0.5s | Bu, Au, Gl-S, Nt, El, Ax-s-d, Jn, Gl |
| Slowest | 1s | Me-Rh, Fi-lo, Ui-p, Bi, Bu, Gl-S, Ax-Ax-d, Io, Mo-n, G, P-As, El, Nt, Ax-d, Ac, Sy-c |

## Component Abbreviations

### Feedback Loop Category (Fi-lo)
| Abbrev | Full Name | Function |
|--------|-----------|----------|
| Fi-lo | Feedback loop | Primary feedback mechanism |
| Fi-fe | Filamentary feedback | Cytoskeletal feedback |
| Mi-fm | Microtubule-Neurofilament network | Structural feedback |
| β-sp-A | β-spectrin actin network | Membrane-cytoskeleton coupling |
| A | Ankyrin & ordered proteins | Membrane anchoring |

### Rhythm & Electrical Category (Rh, Ep)
| Abbrev | Full Name | Function |
|--------|-----------|----------|
| Rh | Rhythm | Oscillatory timing |
| Io | Ionic | Ion-based signaling |
| Ep | Electrical polarization | Membrane potential |
| Me-Rh | Mechanical rhythm | Mechanical oscillations |

### Morphological Types
| Abbrev | Full Name | Characteristics |
|--------|-----------|-----------------|
| Ca | Cavity type | Hollow structure |
| Bi | Bipolar | Two main processes |
| Py | Pyramidal | Triangular soma |
| Ui-p | Unipolar | Single process |
| Mu-p | Multipolar | Multiple processes |

### Mechanical & Autonomic
| Abbrev | Full Name | Function |
|--------|-----------|----------|
| Au | Automic | Self-regulating |
| Bu | Mechanical Thrust | Force generation |
| Ch-Co | Fractal geometry | Self-similar structure |

### Anatomic Components (An)
| Abbrev | Full Name | Function |
|--------|-----------|----------|
| AIS[3] | Axon initial segment | Action potential initiation |
| Mu-in | Multipolar neuron | Integration neuron |
| Mo-n | Motor neuron | Efferent signaling |
| Se-n | Sensory neuron | Afferent signaling |
| An-n | Anaxonic neuron | Local processing |
| En-re-Mi | Endoplasmic reticulum–Mitochondria | Energy/calcium |
| P-As | PNN-Astrocyte | Glial support |
| PNN | Peri-neural network | Extracellular matrix |
| G | Golgi body, Lysosome | Processing/degradation |
| Br | Branch | Dendritic/axonal branching |
| Li | Lipid bilayer | Membrane structure |
| Ax | Axonal | Signal transmission |
| Ac | Actin-microtubule antenna | Sensory/structural |
| Me | Membrane | Boundary/signaling |
| Io-Ch | Ion channel-GR | Gated ion flow |
| Pr-Ch(3) | Protein channel | Sheet, tear drop, wires |

### Junction Types (Jn)
| Abbrev | Full Name | Connection Type |
|--------|-----------|-----------------|
| Ax-d | Axo-dendrite | Axon to dendrite |
| Ax-s | Axo-spino dendrite | Axon to spine |
| Ax-Ax-d | Axo-axo-dendrite | Axon to axon to dendrite |
| Ax-x | Axo-somatic | Axon to cell body |
| El | Electrical | Gap junction |
| GlS | Glial-Synapse | Tripartite synapse |
| Gl | Spiral Glial cell | Glial wrapping |
| Sy-c | Synaptic cleft | Chemical synapse |
| Sn-cl-co | SNARE-clathrin complex | Vesicle machinery |
| Nt | Neuro-Glial-transmitter | Signaling molecule |

## Notation: Neuron [a,b,c,d]

The bracket notation `[a,b,c,d]` defines nested time crystal structure:

- **a**: Number of major spatial domains
- **b**: Number of functional layers per domain
- **c**: Number of temporal scales per layer
- **d**: Number of component types per scale

Example: `Neuron [3,4,3,3]`
- 3 spatial domains (dendrite, soma, axon)
- 4 functional layers each
- 3 temporal scales per layer
- 3 component types per scale

## Color Semantics

| Color | Category | Examples |
|-------|----------|----------|
| Blue | Structural/anatomical | AIS, PNN, Br, Li |
| Yellow | Functional/dynamic | Soma, G, Br, P-As |
| Green | Interface/channel | Ac, Io-Ch, Pr-Ch |
| Teal | Core processing | Ax, Me |
| Gray | Integration/junction | A, El, An |

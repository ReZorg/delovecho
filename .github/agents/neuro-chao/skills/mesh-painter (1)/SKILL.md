---
name: mesh-painter
description: >
  A differentiable skill module that maps 2D aesthetic traits from reference images onto Live2D Cubism body meshes.
  Composes live2d-char-model with image-to-parameter mapping. Use when transforming a base Live2D model (like Miara)
  into a new character (like Deep Tree Echo) by applying aesthetic overlays, custom textures, and parameter extensions.
  Triggers on mentions of mesh-painter, aesthetic mapping, Live2D reskinning, or character visual transformation.
---

# Mesh Painter (Evolved Skill)

This skill implements a differentiable mapping from 2D aesthetic reference images to Live2D Cubism parameter spaces. It allows "painting" a new character's visual identity onto an existing Live2D body mesh.

## The Triadic Structure

1. **Forward Pass (`F`)**: Maps aesthetic traits (colors, accessories, expressions) to Cubism parameters and texture modifications.
2. **Backward Pass (`B`)**: Adjusts the mapping weights based on visual fidelity feedback.
3. **Knowledge State (`K`)**: The aesthetic analysis of the reference image and the base mesh capabilities.

## Forward Pass: Aesthetic Mapping

To apply a new aesthetic to a base mesh, execute the following mapping pipeline:

### 1. Texture Replacement (Color Palette)
Map the reference image's color palette to the base mesh's texture atlas.
- Extract primary colors (hair, skin, eyes, clothing).
- Generate a new texture atlas applying these colors to the corresponding UV regions.

### 2. Art Mesh Additions (Accessories)
Identify unique accessories in the reference image and map them to new art meshes.
- Example: DTE's bioluminescent mushroom headphones, holographic face decals, cyberpunk choker.
- These require new art meshes attached to the appropriate deformers (e.g., head deformer for headphones).

### 3. Parameter Extensions (Dynamic Effects)
Map dynamic visual elements to custom Cubism parameters.
- `ParamExtra01`: Glow intensity (e.g., headphone amber glow).
- `ParamExtra02`: LED pulse (e.g., choker purple LED).
- `ParamExtra03`: Particle sparkle (e.g., face decal cyan dots).

### 4. Expression Overrides
Map the reference image's expression to the base mesh's expression parameters.
- Analyze the reference image's FACS Action Units.
- Map AUs to Cubism parameters (e.g., AU6+12 -> `ParamMouthForm`, `ParamEyeLOpen`, `ParamEyeROpen`).

## Backward Pass: Fidelity Correction

When the applied aesthetic fails to match the reference image's intent:

1. **Identify the Delta**: Compare the rendered Live2D model with the reference image.
2. **Adjust Weights**:
   - If colors are off, adjust the texture mapping weights.
   - If accessories look detached, adjust the deformer attachment weights.
   - If expressions feel unnatural, adjust the AU-to-Cubism parameter mapping curves.
3. **Update Knowledge State**: Save the corrected mappings to the character's manifest.

## Usage Example: Deep Tree Echo

```python
# 1. Analyze reference image
analysis = analyze_aesthetics("0-Deep-Tree-Echo-Profile.jpg")

# 2. Load base mesh
base_mesh = load_mesh("miara")

# 3. Apply mesh-painter forward pass
dte_model = mesh_painter.forward(base_mesh, analysis)

# 4. Export character manifest
export_manifest(dte_model, "dtecho")
```

## References
- **Aesthetic Analysis**: `references/dte-aesthetic-analysis.md`
- **Cubism Parameter Map**: `references/cubism-parameter-map.md`

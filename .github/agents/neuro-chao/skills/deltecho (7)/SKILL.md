---
name: deltecho
description: "Orchestration framework for creating cognitive DeltaChat bots with Live2D avatars and Deep Tree Echo autonomy. Use for building bots with AI features, RAG knowledge bases, conversational state tracking (Reservoir Computing), multi-account support, and introspective capabilities. Triggers on: deltecho, DeltaChat bot, deltachat orchestration, cognitive chat bot, ReZorg DeltaChat, Live2D avatar, Deep Tree Echo."
---

# deltecho: Cognitive DeltaChat Bot Orchestration

This skill provides a comprehensive framework for building, orchestrating, and managing intelligent DeltaChat bots within a modern TypeScript/React architecture. It synthesizes multiple cognitive architecture skills (`echo-introspect`, `ec9o`, `unreal-echo`, `live2d-avatar`) into a practical toolset for creating bots that can reason, remember, learn, and express themselves through a Live2D avatar.

## Core Architecture

The `deltecho` framework is a monorepo with a layered architecture:

| Layer | Package | Purpose |
| :--- | :--- | :--- |
| **0. Core** | `@deltecho/core` | Low-level communication with the DeltaChat network via `deltachat-rpc-client`. |
| **1. Frontend** | `@deltecho/frontend` | The main React-based user interface. |
| **2. Avatar** | `@deltecho/avatar` | Live2D Cubism avatar integration, expression mapping, and rendering. |
| **3. Voice** | `@deltecho/voice` | Voice pipeline for speech-to-text and text-to-speech. |
| **4. Cognitive** | `@deltecho/cognitive` | Unified cognitive interface for reasoning, memory, and persona. |
| **5. Orchestrator** | `deep-tree-echo-orchestrator` | High-level event handling, command routing, and agentic loop. |

## Deployment

The app deploys as a **Cloudflare Container** via GitHub Actions. The workflow builds a Docker image, pushes to Cloudflare's container registry, and deploys via `wrangler deploy`.

- **Live URL**: `https://deltecho-chat-preview.dan-cdc.workers.dev`
- **Auth**: Password-protected via `WEB_PASSWORD` Cloudflare secret
- **Config**: `packages/target-browser/wrangler.jsonc`
- **Dockerfile**: `Dockerfile.cloudflare`
- **CI/CD**: `.github/workflows/deploy-cloudflare-containers.yml`

Container cold starts take 15-30 seconds after deployment. The `/health` endpoint may return OK before the container is fully ready.

## Workflow: Building a Cognitive Bot

### Step 1: Set Up the Development Environment

```bash
gh repo clone ReZorg/deltecho
cd deltecho
pnpm install --frozen-lockfile
```

### Step 2: Run the Development Server

```bash
pnpm --filter @deltecho/frontend dev
```

### Step 3: Enable Deep Tree Echo Autonomy

The `DTESimulation` class in `DeepTreeEchoHub.tsx` runs an autonomous cognitive loop by default, providing a continuous "thinking" substrate that real events enrich.

```typescript
// packages/frontend/src/components/screens/DeepTreeEchoHub/DeepTreeEchoHub.tsx
useEffect(() => {
  if (autoRun) {
    const interval = setInterval(() => { simulation.step(); }, 2000);
    return () => clearInterval(interval);
  }
}, [autoRun, simulation, isConnected]);
```

### Step 4: Integrate the Live2D Avatar

The avatar pipeline in `@deltecho/avatar` uses `PixiLive2DRenderer`:

1. Place Live2D model files in `packages/frontend/static/models/`
2. The renderer dynamically imports `@pixi/unsafe-eval`, `pixi.js`, and `pixi-live2d-display-lipsyncpatch/cubism4`
3. Uses `Live2DModel.fromSync()` with event listeners for crash-safe loading
4. Model paths configured in `Live2DAvatar.tsx` via `CDN_MODELS` map

For details on the Live2D integration, read the `live2d-avatar` skill.

## Performance & Known Issues

### Live2D Avatar: Three-Layer Fix (Production-Critical)

The Live2D avatar had three layered bugs, each masked by the previous one. All three must be addressed for the avatar to work in production.

**Layer 1 — Stack overflow crash**: Cubism 4's `startUpCubism4()` passes `console.log` as its `logFunction`. Any console.log interceptor (error boundaries, browser extensions) causes infinite recursion → `RangeError: Maximum call stack size exceeded` → entire app crashes. **Fix**: Use `fromSync()` instead of `from()`, provide a safe noop logger with recursion guard.

**Layer 2 — CSP blocks shader compilation**: PixiJS v7 uses `new Function()` for shaders. CSP policy `script-src 'self' 'wasm-unsafe-eval'` blocks this. **Fix**: Import `@pixi/unsafe-eval` before `pixi.js` to use pre-compiled shaders.

**Layer 3 — Cubism 2 runtime assertion**: The main entry of `pixi-live2d-display-lipsyncpatch` has a top-level `if (!window.Live2D) throw ...` that fails because we only load Cubism 4 SDK. **Fix**: Import from `pixi-live2d-display-lipsyncpatch/cubism4` sub-export instead.

All fixes are in `packages/avatar/src/adapters/pixi-live2d-renderer.ts`.

### `sentbox_watch` and Deprecated Config Keys

**Symptom**: Settings dialog gets stuck on "Loading......".

**Fix**: Ensure `packages/frontend/src/stores/settings.ts` does not contain deprecated keys: `sentbox_watch`, `e2ee_enabled`, `webrtc_instance`, `webxdc_realtime_enabled`. Replace `addr` with `configured_addr`.

### Container Cold Start

After deployment, the Cloudflare Container takes 15-30 seconds to start. The worker may return `{"error":"Failed to start container"}` during this period. Retry after waiting.

## Bundled Scripts & References

- **`/home/ubuntu/deltecho/`**: Full source code of the `deltecho` project.
- **`/home/ubuntu/deltecho/DEEP_TREE_ECHO_AUTONOMY.md`**: Autonomous agent architecture documentation.
- **`/home/ubuntu/deltecho/LIVE2D_AVATAR_INTEGRATION.md`**: Live2D avatar integration documentation.
- **`/home/ubuntu/deltecho/docs/REPAIR_COMPLETION_REPORT.md`**: Repair and fix history.

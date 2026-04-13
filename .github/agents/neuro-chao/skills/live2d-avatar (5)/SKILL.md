---
name: live2d-avatar
description: Integrate Live2D Cubism avatars into web applications using pixi-live2d-display. Use when building interactive avatar interfaces, VTuber-style web experiences, character-driven UIs, or any project requiring animated 2D character models with mouse tracking, expressions, motions, and hit-area interactions in the browser.
---

# Live2D Cubism Avatar

Integrate Live2D Cubism 2/3/4 models into web applications via CDN using PixiJS and pixi-live2d-display. No npm install required for the Live2D runtime — all libraries load from CDN script tags.

## Required CDN Scripts

Add these to `<head>` in order:

```html
<!-- Live2D Cubism Core (required) -->
<script src="https://cubism.live2d.com/sdk-web/cubismcore/live2dcubismcore.min.js"></script>
<!-- Cubism 2 support (optional, for legacy models) -->
<script src="https://cdn.jsdelivr.net/gh/dylanNew/live2d/webgl/Live2D/lib/live2d.min.js"></script>
<!-- PixiJS v6 Legacy (canvas2d fallback for environments without WebGL) -->
<script src="https://cdn.jsdelivr.net/npm/pixi.js-legacy@6.5.2/dist/browser/pixi-legacy.min.js"></script>
<!-- pixi-live2d-display -->
<script src="https://cdn.jsdelivr.net/npm/pixi-live2d-display/dist/index.min.js"></script>
```

Use `pixi.js-legacy` instead of `pixi.js` to support Canvas2D fallback in environments without WebGL. If WebGL is guaranteed, use `pixi.js@6.5.2` instead.

## Free Test Models

| Model | Version | URL |
|-------|---------|-----|
| Shizuku | Cubism 2 | `https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/shizuku/shizuku.model.json` |
| Haru | Cubism 4 | `https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/haru/haru_greeter_t03.model3.json` |

## Initialization Pattern

Access `PIXI` from `window` at runtime (not at module scope) since CDN scripts load asynchronously:

```typescript
// Inside useEffect or async init function:
const PIXI = (window as any).PIXI;

const app = new PIXI.Application({
  view: canvasElement,       // or let PIXI create one
  autoStart: true,
  backgroundAlpha: 0,        // transparent background
  width: containerWidth,
  height: containerHeight,
  antialias: true,
  forceCanvas: true,          // use Canvas2D fallback (remove if WebGL available)
});

const model = await PIXI.live2d.Live2DModel.from(modelUrl, {
  autoInteract: true,         // eyes follow cursor
  autoUpdate: true,           // auto-animate
});

app.stage.addChild(model);
```

## Key APIs

### Motion

```typescript
model.motion('idle');              // play motion by group name
model.motion('tap_body', 0);      // specific index in group
model.motion('tap_body', 0, 3);   // priority: 0=none, 1=idle, 2=normal, 3=force
```

### Expression

```typescript
model.expression(0);              // set by index
model.expression('smile');        // set by name
```

### Hit Area Events

```typescript
model.on('hit', (hitAreaNames: string[]) => {
  // hitAreaNames: ['body'], ['head'], etc.
});
```

### Focus / Eye Tracking

Automatic when `autoInteract: true`. Manual override:

```typescript
model.focus(x, y);  // screen coordinates
```

### Resize

```typescript
function resize(container: HTMLElement) {
  const w = container.clientWidth;
  const h = container.clientHeight;
  app.renderer.resize(w, h);
  const scale = Math.min(w / model.width, h / model.height) * 0.8;
  model.scale.set(scale);
  model.x = (w - model.width * scale) / 2;
  model.y = (h - model.height * scale) / 2;
}
```

## Common Pitfalls

1. **WebGL not available**: Use `pixi.js-legacy` and set `forceCanvas: true` in Application options.
2. **PIXI undefined at module scope**: Access `(window as any).PIXI` inside `useEffect` or async functions, not at top-level.
3. **Canvas has no parent**: Create the canvas programmatically and append to a container div with `ref`, or wait a frame with `requestAnimationFrame` before initializing.
4. **Model not visible**: Check scale factor — Cubism 4 models are often very large and need small scale values (0.08–0.15). Cubism 2 models use larger scales (0.2–0.3).
5. **Double initialization in React StrictMode**: Use a `cancelled` flag in the cleanup function to prevent race conditions.

## Bundler Integration (esbuild / Webpack)

When using `pixi-live2d-display` or `pixi-live2d-display-lipsyncpatch` as an npm dependency (rather than CDN), bundlers like esbuild may inline the library's module-level code into the main bundle. Three critical issues arise:

### Fix 1: Cubism Core WASM Race Condition

The library checks `window.Live2DCubismCore` at module level. When bundled, this check runs at parse time before the async WASM finishes loading.

**Solution**: Add an esbuild plugin to patch the fatal throw into a warning, and poll for WASM readiness before loading models:

```javascript
const cubismPatchPlugin = {
  name: 'cubism-patch',
  setup(build) {
    build.onLoad({ filter: /pixi-live2d-display.*\.js$/ }, async (args) => {
      let contents = await readFile(args.path, 'utf8')
      contents = contents.replace(
        /if\s*\(!window\.Live2DCubismCore\)\s*\{\s*throw new Error\([^)]+\);\s*\}/g,
        `if (!window.Live2DCubismCore) { console.warn("[Live2D] Cubism 4 Core not yet loaded"); }`
      )
      return { contents, loader: 'js' }
    })
  },
}
```

```typescript
async function waitForCubismCore(timeoutMs = 10000): Promise<void> {
  const start = Date.now();
  while (!(window as any).Live2DCubismCore) {
    if (Date.now() - start > timeoutMs) throw new Error("Cubism Core not loaded");
    await new Promise((r) => setTimeout(r, 100));
  }
}
```

### Fix 2: Cubism 2 Runtime Assertion (Cubism 4-Only Models)

The main entry of `pixi-live2d-display-lipsyncpatch` includes Cubism 2 support with a **top-level module assertion** that throws unconditionally if `window.Live2D` (Cubism 2 SDK) is not defined:

```javascript
// At module level in index.js — NOT inside a function:
if (!window.Live2D) {
  throw new Error("Could not find Cubism 2 runtime. This plugin requires live2d.min.js to be loaded.");
}
```

If you only use Cubism 4 models (`.model3.json`), import the **cubism4 sub-export** instead:

```typescript
// WRONG: imports both Cubism 2 + 4, throws if window.Live2D missing
import { Live2DModel } from "pixi-live2d-display-lipsyncpatch";

// CORRECT: imports only Cubism 4, no Cubism 2 assertion
import { Live2DModel } from "pixi-live2d-display-lipsyncpatch/cubism4";
```

The library's `package.json` exports `./cubism4` which maps to `dist/cubism4.es.js` — a build that contains zero references to the Cubism 2 SDK.

### Fix 3: CSP Blocks PixiJS Shader Compilation

PixiJS v7's `ShaderSystem` uses `new Function()` for runtime shader compilation. If your CSP policy includes `script-src 'self' 'wasm-unsafe-eval'` (without `unsafe-eval`), this is blocked with:

> "Current environment does not allow unsafe-eval, please use @pixi/unsafe-eval module"

**Solution**: Import `@pixi/unsafe-eval` **before** `pixi.js`. This patches PixiJS to use pre-compiled shader functions:

```typescript
// Must be imported BEFORE pixi.js
await import("@pixi/unsafe-eval");
const { Application } = await import("pixi.js");
```

Install: `pnpm add @pixi/unsafe-eval@7.4.3` (match your pixi.js version).

### Fix 4: Stack Overflow from console.log Recursion

Cubism 4's `startUpCubism4()` passes `console.log` as its `logFunction`. If any code wraps or intercepts `console.log` (error boundaries, browser extensions, test frameworks), this creates infinite recursion causing `RangeError: Maximum call stack size exceeded`.

**Solution**: Use `fromSync()` instead of `from()` and provide a safe noop logger:

```typescript
// Save native reference before any wrappers
const _nativeLog = console.log.bind(console);

// Safe logger that catches recursion
let _logDepth = 0;
function safeLog(...args: any[]): void {
  if (_logDepth > 0) return; // prevent recursion
  _logDepth++;
  try { _nativeLog(...args); } finally { _logDepth--; }
}

// Use fromSync instead of from — avoids Promise-chain stack overflow
const model = Live2DModel.fromSync(modelUrl, {
  autoInteract: false,
  autoUpdate: true,
  onLoad: () => { /* model ready */ },
  onError: (err) => { /* handle gracefully */ },
});
```

## TypeScript Declarations

Add to a `.d.ts` file:

```typescript
interface Window {
  PIXI: any;
}
```

## Reference Implementation

See `references/react-component.md` for a complete React component implementation with error handling, resize logic, and model switching.

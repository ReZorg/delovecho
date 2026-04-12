# React Live2D Component Reference

Complete React component for rendering a Live2D Cubism avatar with model switching, error handling, and responsive resize.

## Live2DCanvas.tsx

```tsx
import { useEffect, useRef, useState } from "react";

const MODELS = {
  shizuku: {
    url: "https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/shizuku/shizuku.model.json",
    name: "Shizuku",
    version: "Cubism 2",
  },
  haru: {
    url: "https://cdn.jsdelivr.net/gh/guansss/pixi-live2d-display/test/assets/haru/haru_greeter_t03.model3.json",
    name: "Haru",
    version: "Cubism 4",
  },
};

type ModelKey = keyof typeof MODELS;

interface Props {
  onModelLoaded?: () => void;
  onHit?: (areas: string[]) => void;
  selectedModel?: ModelKey;
}

export default function Live2DCanvas({ onModelLoaded, onHit, selectedModel = "haru" }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<any>(null);
  const modelRef = useRef<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    let resizeHandler: (() => void) | null = null;

    async function init() {
      const container = containerRef.current;
      if (!container) return;

      // Wait a frame to ensure container has dimensions
      await new Promise((r) => requestAnimationFrame(r));
      if (cancelled) return;

      setIsLoading(true);
      setError(null);

      try {
        // Cleanup previous instance
        if (appRef.current) {
          try { appRef.current.destroy(true, { children: true }); } catch {}
          appRef.current = null;
          modelRef.current = null;
        }

        const PIXI = (window as any).PIXI;
        if (!PIXI) throw new Error("PixiJS not loaded");
        if (!PIXI.live2d) throw new Error("pixi-live2d-display not loaded");

        const w = container.clientWidth || 500;
        const h = container.clientHeight || 500;

        // Create canvas programmatically
        const canvas = document.createElement("canvas");
        canvas.style.cssText = "width:100%;height:100%;display:block;touch-action:none;";
        container.querySelector("canvas")?.remove();
        container.appendChild(canvas);

        const app = new PIXI.Application({
          view: canvas,
          autoStart: true,
          backgroundAlpha: 0,
          width: w,
          height: h,
          antialias: true,
          forceCanvas: true,  // Remove if WebGL is available
        });

        if (cancelled) return;
        appRef.current = app;

        const modelConfig = MODELS[selectedModel];
        const model = await PIXI.live2d.Live2DModel.from(modelConfig.url, {
          autoInteract: true,
          autoUpdate: true,
        });

        if (cancelled) { try { app.destroy(true); } catch {} return; }

        app.stage.addChild(model);
        modelRef.current = model;

        // Resize logic
        const doResize = () => {
          const cw = container.clientWidth || 500;
          const ch = container.clientHeight || 500;
          try { app.renderer.resize(cw, ch); } catch {}
          const scale = Math.min(cw / model.width, ch / model.height) * 0.8;
          model.scale.set(scale);
          model.x = (cw - model.width * scale) / 2;
          model.y = (ch - model.height * scale) / 2;
        };

        doResize();
        resizeHandler = doResize;
        window.addEventListener("resize", doResize);

        // Hit area events
        model.on("hit", (hitAreaNames: string[]) => onHit?.(hitAreaNames));

        setIsLoading(false);
        onModelLoaded?.();
      } catch (err: any) {
        console.error("Live2D load error:", err);
        if (!cancelled) {
          setError(err?.message || "Failed to load");
          setIsLoading(false);
        }
      }
    }

    init();

    return () => {
      cancelled = true;
      if (resizeHandler) window.removeEventListener("resize", resizeHandler);
      if (appRef.current) {
        try { appRef.current.destroy(true, { children: true }); } catch {}
        appRef.current = null;
        modelRef.current = null;
      }
    };
  }, [selectedModel]);

  return (
    <div ref={containerRef} style={{ width: "100%", height: "100%", minHeight: 400, position: "relative" }}>
      {isLoading && !error && <div>Loading...</div>}
      {error && <div>Error: {error}</div>}
    </div>
  );
}

export { MODELS, type ModelKey };
```

## Usage

```tsx
import Live2DCanvas from "./Live2DCanvas";

function App() {
  return (
    <div style={{ width: 600, height: 800 }}>
      <Live2DCanvas
        selectedModel="haru"
        onModelLoaded={() => console.log("Model ready")}
        onHit={(areas) => console.log("Hit:", areas)}
      />
    </div>
  );
}
```

## Triggering Motions/Expressions Externally

Expose the model ref via `useImperativeHandle` or a callback:

```tsx
// In Live2DCanvas, add:
const getModel = () => modelRef.current;

// Then externally:
const model = canvasRef.current?.getModel();
model?.motion("tap_body");
model?.expression(1);
```

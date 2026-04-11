# Vorticog Project Structure Reference

Read this reference when navigating the codebase, adding new features, or understanding the build/deploy pipeline.

## Directory Layout

```
vorticog/
├── client/                     # React frontend (Vite root)
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── App.tsx             # Router: Home, Dashboard, CompanySetup, BusinessUnits, UnitDetail, Market, Finance, Leaderboard, Production
│       ├── main.tsx            # Entry point
│       ├── index.css           # Tailwind + theme variables
│       ├── const.ts
│       ├── _core/hooks/        # useAuth.ts
│       ├── components/         # AIChatBox, DashboardLayout, GameLayout, Map, ManusDialog, ErrorBoundary
│       │   └── ui/             # 50+ Radix-based shadcn/ui components
│       ├── contexts/           # ThemeContext (dark default, switchable)
│       ├── hooks/              # use-toast, useComposition, useMobile, usePersistFn
│       ├── lib/                # trpc.ts (client), utils.ts (cn helper)
│       └── pages/              # 9 page components
├── server/
│   ├── _core/                  # Framework layer (DO NOT MODIFY unless necessary)
│   │   ├── index.ts            # Express server entry
│   │   ├── trpc.ts             # tRPC setup, publicProcedure, protectedProcedure
│   │   ├── env.ts              # ENV config object
│   │   ├── llm.ts              # invokeLLM() — Gemini 2.5 Flash
│   │   ├── oauth.ts            # Manus OAuth integration
│   │   ├── sdk.ts              # Manus SDK
│   │   ├── vite.ts             # Vite dev middleware
│   │   ├── context.ts          # tRPC context (user from JWT)
│   │   ├── cookies.ts          # Session cookie helpers
│   │   ├── notification.ts     # Notification helpers
│   │   ├── imageGeneration.ts  # Image gen API
│   │   ├── voiceTranscription.ts # Voice API
│   │   ├── map.ts              # Map API
│   │   ├── dataApi.ts          # Data API helpers
│   │   └── systemRouter.ts     # System health router
│   ├── db.ts                   # All Drizzle ORM database functions (100+ functions)
│   ├── routers.ts              # All tRPC routers (appRouter)
│   ├── storage.ts              # S3 storage via forge proxy
│   └── *.test.ts               # Vitest test files
├── shared/
│   ├── _core/errors.ts         # Error types
│   ├── const.ts                # Shared constants (COOKIE_NAME, etc.)
│   └── types.ts                # Re-exports all types from schema
├── drizzle/
│   ├── schema.ts               # All table definitions + relations (1301 lines)
│   ├── relations.ts            # Additional relations
│   ├── 0000_*.sql, 0001_*.sql  # Migration files
│   └── meta/                   # Drizzle migration metadata
├── docs/
│   ├── AGENTIC_SIMULATION.md
│   ├── DREAMCOG_INTEGRATION.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── IMPLEMENTATION_SUMMARY_DREAMCOG.md
├── package.json                # name: "virtunomics"
├── drizzle.config.ts
├── vite.config.ts
├── vitest.config.ts
├── tsconfig.json
└── todo.md
```

## Build & Run Commands

```bash
pnpm install                    # Install dependencies
npm run dev                     # Dev server (tsx watch)
npm run build                   # Vite build + esbuild server bundle
npm run start                   # Production server
npm run check                   # TypeScript type check
npm run test                    # Vitest tests
npm run db:push                 # Drizzle generate + migrate
```

## Environment Variables

```
VITE_APP_ID                     # Manus app ID
JWT_SECRET                      # Cookie signing secret
DATABASE_URL                    # MySQL/TiDB connection string
OAUTH_SERVER_URL                # Manus OAuth server
OWNER_OPEN_ID                   # Owner's OpenID
BUILT_IN_FORGE_API_URL          # LLM/storage API base URL
BUILT_IN_FORGE_API_KEY          # LLM/storage API key
```

## Key Conventions

- **server/_core/**: Framework layer managed by Manus scaffold. Avoid modifying unless extending core capabilities.
- **drizzle/schema.ts**: Single source of truth for all table definitions. Types are auto-inferred and re-exported via `shared/types.ts`.
- **server/db.ts**: All database CRUD functions. New tables need corresponding functions here.
- **server/routers.ts**: All tRPC routers in a single file. Uses `protectedProcedure` for auth-required endpoints.
- **Shared types**: Import from `@shared/types` in both client and server.
- **UI components**: shadcn/ui pattern in `client/src/components/ui/`. Use existing components before creating new ones.
- **Aliases**: `@` → `client/src`, `@shared` → `shared/`, `@assets` → `attached_assets/`.

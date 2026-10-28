# frontend

Vite, React, and TypeScript skeleton for the Team Feedback Board. Versions are the pins in `docs/project/stack.md`. API types in `src/api/types.ts` are transcribed from `docs/project/architecture/api-contract.yaml` (no generator is pinned).

Use Node 24.22.1 (the project pin); the dependencies together accept 22.22+, 24.x and 26+.

```bash
npm install
npm run typecheck
npm run lint
npm run test
npm run build
npm run dev
```

The app is one placeholder route at `/`, built with `createBrowserRouter` (React Router data mode). Screens, auth, and the API client are later tasks.

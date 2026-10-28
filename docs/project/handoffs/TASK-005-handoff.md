# Handoff: TASK-005 Frontend skeleton
Bot: frontend-bot   Attempt: 1   PR: https://github.com/Gopi-Git001/feedback_borard/pull/20   Branch: feature/TASK-005-frontend-skeleton (from 11497e9)

Task spec file `docs/project/tasks/TASK-005.md` is not in the repo. The acceptance line is `docs/project/plan.md` (TASK-005, M0). Required reviewer: qa-bot.

`TEAM-CONVENTIONS.md` is not in this repo. `https://github.com/Gopi-Git001/Saas_Bot/blob/main/TEAM-CONVENTIONS.md` returned 404 from this environment, and `gh repo view Gopi-Git001/Saas_Bot` could not resolve the repository. This report follows the section headings used by `docs/project/handoffs/TASK-003-handoff.md` (that handoff cites TEAM-CONVENTIONS section 5) and the evidence this task asked for.

## Summary
Adds the frontend skeleton under `frontend/`: Vite, React, and TypeScript in strict mode, at the versions pinned in `docs/project/stack.md`. npm scripts `typecheck`, `lint`, `test`, and `build` exist and passed on Node 24.22.1. Routing uses `createBrowserRouter` from `react-router` 8.5.1. API types in `frontend/src/api/types.ts` are transcribed by hand from `docs/project/architecture/api-contract.yaml`. `frontend/package-lock.json` is committed. No pages, auth screens, API client, or Dockerfile.

## Acceptance criteria
| Criterion | met / not met | Evidence |
|---|---|---|
| Vite ~8.3, React ~19.3, TypeScript ~6.0.3 strict, from stack.md (Attempt 2 addendum pins only) | **met** | `npm ls` below. `tsconfig.app.json` and `tsconfig.node.json` set `"strict": true`. Installed: vite 8.3.5, react 19.3.1, react-dom 19.3.1, typescript 6.0.3, plus the other frontend pins that these scripts need |
| Scripts `typecheck`, `lint` (eslint + typescript-eslint), `test` (vitest), `build` all pass | **met** | Pasted output below, run on Node v24.22.1. Each exited 0. CI does not exist yet (TASK-008), so this is a local run, not a GitHub Actions run |
| react-router 8.5.1 library mode (`createBrowserRouter`), confirmed on reactrouter.com, or stop and report | **met, with a naming difference** | The package version exists (npm `latest` is 8.5.1). Official docs for that version do not say "library mode". `createBrowserRouter` is Data mode. Details under Decisions. The app uses that API. No other router or version was substituted |
| API types derived from `api-contract.yaml`; no unpinned generator; no invented fields or endpoints | **met** | `frontend/src/api/types.ts`. No generator dependency. Vitest reads the YAML and checks operation id, method, path, schema names, and error codes |
| `package-lock.json` committed | **met** | `frontend/package-lock.json` (lockfileVersion 3) is in the commit |
| No pages, auth screens, or Dockerfile | **met** | One placeholder route at `/`. No auth UI, no fetch client, no Dockerfile |
| Strict TypeScript, accessible shell, responsive, no tokens or secrets in code or storage | **met** for this skeleton | Strict `tsc` passed. Browser check below: one `h1`, `main`, skip link moves focus to `#main`, no horizontal overflow at 390px, `localStorage` and `sessionStorage` length 0. No secrets added |

## Files changed
- `frontend/package.json` (new)
- `frontend/package-lock.json` (new)
- `frontend/tsconfig.json`, `frontend/tsconfig.app.json`, `frontend/tsconfig.node.json` (new)
- `frontend/vite.config.ts` (new)
- `frontend/eslint.config.js` (new)
- `frontend/index.html` (new)
- `frontend/src/main.tsx`, `frontend/src/router.tsx`, `frontend/src/shell.tsx`, `frontend/src/styles.css`, `frontend/src/vite-env.d.ts`, `frontend/src/app.test.tsx`, `frontend/src/api/types.ts` (new)
- `frontend/README.md` (replaced the TASK-003 placeholder with how to run the skeleton)
- `docs/project/handoffs/TASK-005-handoff.md` (this file)

## How to test locally
```bash
cd frontend
npm install
npm run typecheck
npm run lint
npm run test
npm run build
```
The evidence run used Node 24.22.1 (the stack pin). `frontend/package.json` has no `engines` field, so the package does not accept or reject a Node version. react-router 8.5.1 needs a newer Node than 20 (`npm view react-router@8.5.1 engines` is `{"node":">=22.22.0"}`). This VM's default `node` on `PATH` was v22.23.4 (`/exec-daemon/node`); the evidence run put `~/.nvm/versions/node/v24.22.1/bin` first.

## Test results
Environment: Node v24.22.1, npm 11.19.1 (the npm that ships with that Node). `npm install` that wrote `package-lock.json` was the VM's npm 10.9.9. Lockfile was not rewritten by the later script runs.

**Installed versions (`npm ls --depth=0`):**
```
feedback-board-frontend@0.0.0
├── @types/react-dom@19.3.0
├── @types/react@19.3.0
├── @vitejs/plugin-react@6.1.2
├── eslint@10.13.0
├── react-dom@19.3.1
├── react-router@8.5.1
├── react@19.3.1
├── typescript-eslint@8.72.1
├── typescript@6.0.3
├── vite@8.3.5
└── vitest@5.0.5
```

**`npm run typecheck` (exit 0):**
```
> feedback-board-frontend@0.0.0 typecheck
> tsc -b --pretty false
```

**`npm run lint` (exit 0):**
```
> feedback-board-frontend@0.0.0 lint
> eslint .
```

**`npm run test` (exit 0):**
```
> feedback-board-frontend@0.0.0 test
> vitest run

 RUN  v5.0.5 frontend/

 Test Files  1 passed (1)
      Tests  7 passed (7)
   Start at  03:02:14
   Duration  273ms (import 54%, transform 30%, tests 13%, worker 2%)
```

**`npm run build` (exit 0):**
```
> feedback-board-frontend@0.0.0 build
> tsc -b --pretty false && vite build

vite v8.3.5 building client environment for production...
transforming...
✓ 99 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.63 kB │ gzip:  0.40 kB
dist/assets/index-jiXSyk86.css    0.82 kB │ gzip:  0.46 kB
dist/assets/index-DvguPBqz.js   314.36 kB │ gzip: 99.16 kB

✓ built in 258ms
```

**Browser check of the production build** (`vite preview` on 127.0.0.1:4173, Node 24.22.1):
- `/` title "Team Feedback Board", one level-1 heading "Team Feedback Board", a `main` region, and the placeholder sentence.
- Tab focuses "Skip to content". Enter sets the URL hash to `#main` and moves focus to the `main` element.
- At 390×844 the document does not scroll horizontally.
- `localStorage.length` and `sessionStorage.length` are 0.
- `/missing` shows React Router's default "Unexpected Application Error!" / "404 Not Found". That screen is the library default, not a page built in this task.
- The first load, before a favicon link existed, logged a 404 for `/favicon.ico`. After the inline icon link, a reload did not report a new console error.

## Decisions made (and why)
- **Branch base is 11497e9**, as dispatched. That commit is an ancestor of `origin/main`. `api-contract.yaml` and `stack.md` are the same on 11497e9 and `origin/main` at fetch time (`92dedd6`). `plan.md` differs by a few lines on `origin/main`; this branch does not include that later edit.
- **Versions.** Every direct dependency is a `~` range from stack.md's frontend table or the Attempt 2 addendum (Vitest and typescript-eslint are final there). Resolved versions are the exact verified versions in that file. TanStack Query `~5.105.0` is pinned and final in stack.md, and it is not installed: this task has no data fetching. Adding it unused would be a dependency with no caller. TASK-012 can add it.
- **No OpenAPI generator.** stack.md says none is pinned (`openapi-typescript` 7.13.0 peers TypeScript 5; `@hey-api/openapi-ts` is 0.x). Types are hand-written. A vitest check parses the YAML for operation ids, methods, paths, `components/schemas` names, and the `ErrorResponse` code enum so a rename in the contract fails the test. Query parameters `type` and `status` on `GET /posts` are represented as `ListPostsQuery`. That name is not a schema in the file; the fields are the operation's parameters. 415 is described as a convention and is not listed per operation, so it is not a response key on `ApiOperationMap`. `GET /api/v1/health` is not in the contract file, so it is not typed.
- **React Router.** Checked on 2026-10-27 (America/Chicago):
  - `npm view react-router@8.5.1` returns version 8.5.1. Dist-tag `latest` is 8.5.1. Engines: `node >= 22.22.0`. Peers: `react` and `react-dom` `>=19.2.7`.
  - https://reactrouter.com/start/modes (docs selector "latest (8.5.1)") defines three modes. Declarative uses `BrowserRouter`. Data uses `createBrowserRouter` and `RouterProvider`. Framework uses `@react-router/dev`. The page does not say "library mode".
  - https://reactrouter.com/start/data/installation (marked data mode) installs `react-router` and renders with `createBrowserRouter` from `react-router` and `RouterProvider` from `react-router/dom`.
  - https://reactrouter.com/start/library/installation responded as declarative mode (`BrowserRouter`), so that URL is not the 8.5.1 guide for `createBrowserRouter`.
  - The installed package exports both symbols from `react-router`, and `RouterProvider` also from the `react-router/dom` subpath of the same package. The type docs say the DOM app should import `RouterProvider` from `react-router/dom` because that build wires `react-dom`'s `flushSync`. `react-router-dom` (the separate package) was not installed. stack.md note 5 says that package is 7.x only.
  - This is the documented Data-mode SPA, which is the `createBrowserRouter` usage the task named. It is not a switch to another router or another version. The word "library" is the part that does not match the 8.5.1 docs.
- **Tests without unpinned DOM libraries.** jsdom and happy-dom are not pinned. The smoke test renders with `react-dom/server` and calls `createBrowserRouter` with the public `window` option. `createBrowserRouter` still reads the global `window` inside `parseHydrationData` (`window?.` throws in Node when `window` is not declared). The test sets `globalThis.window` for that call and removes it afterwards.
- **`@types/node` is not pinned.** The contract test needs `readFileSync`, `dirname`, `resolve`, and `fileURLToPath`. Those four functions are declared in `frontend/src/vite-env.d.ts` instead of adding the package.
- **ESLint config is JavaScript.** ESLint 10 peers `jiti: *`, which is not pinned. A native ESM `eslint.config.js` loads without it. The config uses `typescript-eslint` 8.72.1 recommended rules.
- **Placeholder shell.** One route, `/`, renders a skip link, one `h1`, and `main`. `main` is `tabIndex={-1}` so the skip link moves focus. Styles use system fonts, fluid type, and a 40rem column. No `localStorage` or `sessionStorage`.

## Open questions
1. Please confirm that React Router 8.5.1 **Data mode** (`createBrowserRouter` + `RouterProvider` from `react-router/dom`) is the accepted reading of "library mode". The version exists and the call works. The docs no longer use the name "library mode". Nothing was switched.
2. `TEAM-CONVENTIONS.md` could not be read (404 / repo not visible). If section 5 requires a heading this file lacks, say which one and I will add it.
3. Unmatched URLs render React Router's default 404 ("Unexpected Application Error!"). TASK-012's route table is the place to replace that. I did not add a not-found page here.
4. `@types/node` is still unpinned. The local declarations cover only the contract test. A later task that needs more Node types should pin `@types/node` in stack.md rather than grow that declaration.
5. The VM default Node is 22.23.4. The four scripts were re-run with Node 24.22.1 and passed. I did not change the lockfile with npm 11.

## Suggested follow-up tasks
- TASK-012: route table, auth session, API client (TanStack Query is already pinned for that).
- TASK-012 and later, not done in this fix: extend the contract-drift test (enum values, per-schema field names and `required`, per-operation status codes and body schema refs), pin `@types/node`, and add a11y lint rules.
- TASK-007: frontend Dockerfile and nginx. Not started here.
- TASK-008: run these four scripts in CI.

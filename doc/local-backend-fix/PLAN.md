# Local Backend Fix Plan

## Goal
- Keep resume editing workflows available for local personal use.
- Remove high-risk security issues (path traversal, guessable default password, broad ID-based updates).
- Keep non-core modules (payment/membership) as simple stubs.

## Scope
- Backend hardening in `/Users/xa/Desktop/简历/resume-backend`.
- Add missing lego export stub APIs required by frontend.
- Document execution and test evidence in this folder.

## Tasks
1. Add local-mode config flags (`APP_MODE`, `LOCAL_ONLY`, `ALLOW_AUTO_LOGIN`, `DEFAULT_LOCAL_EMAIL`).
2. Harden startup flow and local-only middleware in `main.py`.
3. Refactor auth dependency fallback in `deps.py`.
4. Fix upload path traversal in `routers/upload.py`.
5. Add owner checks in `routers/user_resume.py`.
6. Add owner checks in `routers/create_template.py`.
7. Add owner checks in `routers/lego.py`.
8. Add `routers/lego_pdf.py` and register routes.
9. Run smoke/security tests and record outputs.

## Acceptance Criteria
- Upload path traversal attempts return HTTP 400.
- No hardcoded guessable default password remains.
- Core resume edit/save/upload/export paths work without manual login in local mode.
- `/huajian/legoPdf/getPdf` and `/huajian/legoPdf/getPNG` return 200.
- `PLAN.md`, `WORKLOG.md`, `TEST-REPORT.md` are complete and traceable.

## Execution Status
- `2026-02-22`: Completed for current local personal-use scope, including continuation contract fixes for frontend/backend compatibility, AttendanceDialog runtime regression repair, and follow-up adaptation pass for `router-view` directive/`preview` prop/attendance response shape.

## 2026-02-22 Personal Minimal Chain Cleanup Plan (Executed)

### Focus
- Keep only personal local usage semantics and minimal editing chain.
- Align frontend routes/functions with the reduced backend API surface.
- Remove dead/unneeded files and reset runtime artifacts.

### Execution Items
1. Frontend route and feature adaptation kept on minimal chain only.
2. Frontend API and build/lint/type checks recovered to pass state.
3. Backend route surface reduced further (drop admin/audit/category manage endpoints in `resume.py` and admin endpoints in `user_resume.py`).
4. Token helper moved to `deps.py`; unused `routers/auth.py` removed.
5. Non-core frontend docs/config wording rewritten to local personal project language.
6. Unused frontend files removed (`src/views/index/components/*`, unused dialog/store/utils files).
7. Runtime artifacts cleaned (`.playwright-cli`, `output`, backend `venv`, `__pycache__`, `resume.db`).
8. Ignore rules updated (`resume-design/.gitignore`, `resume-backend/.gitignore`).
9. Full verification rerun (`vue-tsc`, `eslint`, `build:dev`, backend `py_compile`, API smoke).
10. 10-point acceptance mapping recorded in `TEST-REPORT.md`.

## 2026-02-22 Final Adaptation Addendum (Executed)

### Final Delta
1. Removed frontend dead API surface that no longer has backend support:
   - `src/http/api/websiteConfig.ts` keeps only `getWebsiteConfigAsync`.
2. Removed unused frontend legacy HTTP entries:
   - deleted `src/http/custom.ts`
   - deleted `src/http/smallpig.ts`
   - `src/config/index.ts` now keeps only `serverAddress`.
3. Cleared stale wording/noise comments:
   - `src/utils/common.ts` removed AI-specific historical wording.
   - `resume-backend/routers/lego_pdf.py` and `resume-backend/routers/pdf.py` removed `Stub` wording.
4. Deleted unreferenced dictionary files:
   - `src/dictionary/ai.ts`
   - `src/dictionary/commentType.ts`
   - `src/dictionary/integralTypeDic.ts`
5. Re-ran full checks and cleaned regenerated runtime artifacts again.

### Acceptance Impact
- Strengthens items #5/#6/#7 (frontend-backend adaptation consistency).
- Strengthens items #8/#9/#10 (unnecessary code/comment/wording cleanup).

## 2026-02-22 UI Regression Addendum (Executed)

### Objective
- Fix post-cleanup UI regressions without expanding scope:
  1. `/designer` blank editor when route has no `id` or API payload is empty.
  2. `/designResume/:id` right-side tools overlapping preview content.

### Executed Changes
1. Added null-safe template loading and local default fallback in:
   - `/Users/xa/Desktop/简历/resume-design/src/views/designer/index.vue`
2. Refactored right-side tool area into non-overlay layout in:
   - `/Users/xa/Desktop/简历/resume-design/src/views/designerResume/index.vue`
3. Regression verification and artifact capture recorded in:
   - `/Users/xa/Desktop/简历/resume-design/doc/local-backend-fix/WORKLOG.md`
   - `/Users/xa/Desktop/简历/resume-design/doc/local-backend-fix/TEST-REPORT.md`

### Verification Gate
- `pnpm exec eslint src/views/designer/index.vue src/views/designerResume/index.vue` -> PASS
- `pnpm exec vue-tsc --noEmit` -> PASS
- Playwright checks:
  - `/designer` component list recovered and console errors cleared.
  - `/designResume/:id` overlap area reduced to `0`.

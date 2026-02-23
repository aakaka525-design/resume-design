# Worklog

> Path note: historical entries may mention `resume-backend` and old frontend root paths.  
> Since 2026-02-23, canonical paths are `backend/` and `frontend/`.

## 2026-02-22

### Phase 0 - Initialization
- Created documentation folder `/Users/xa/Desktop/简历/resume-design/doc/local-backend-fix/`.
- Initialized `PLAN.md`, `WORKLOG.md`, `TEST-REPORT.md`.

### Phase 1 - Config and Startup Hardening
- Updated `/Users/xa/Desktop/简历/resume-backend/config.py`:
  - Added `APP_MODE`, `LOCAL_ONLY`, `ALLOW_AUTO_LOGIN`, `DEFAULT_LOCAL_EMAIL`.
- Updated `/Users/xa/Desktop/简历/resume-backend/main.py`:
  - Added localhost-only middleware guard (`LOCAL_ONLY=true` default).
  - Added secure default local user bootstrap based on `DEFAULT_LOCAL_EMAIL`.
  - Removed guessable default password behavior and weak legacy password rotation for `admin@local.com` if detected.
  - Added `ALLOW_AUTO_LOGIN` check for `/huajian/auth/autoLogin`.
  - Registered lego PDF router and changed `uvicorn` default host to `127.0.0.1`.

### Phase 2 - Auth Dependency Refactor
- Updated `/Users/xa/Desktop/简历/resume-backend/deps.py`:
  - Local mode: no-token/invalid-token fallback allowed.
  - Non-local mode: strict `401` for invalid/missing token.
  - Removed weak password fallback creation.

### Phase 3 - Upload Security
- Updated `/Users/xa/Desktop/简历/resume-backend/routers/upload.py`:
  - Added strict path normalization and whitelist validation.
  - Enforced resolved upload path to stay under `UPLOAD_DIR`.
  - Returned `HTTP 400` for illegal traversal path.
  - Switched absolute `fileUrl` generation to request-based base URL.

### Phase 4 - Owner Constraint Enforcement
- Updated `/Users/xa/Desktop/简历/resume-backend/routers/user_resume.py`:
  - Update/publish/updateOnline now require `id + user_email`.
  - Update with non-owned `id` now returns 404, not implicit create.
- Updated `/Users/xa/Desktop/简历/resume-backend/routers/create_template.py`:
  - `saveDraft` update and `getUsertemplate/{id}` now require `id + user_email`.
  - Update with non-owned `id` now returns 404.
- Updated `/Users/xa/Desktop/简历/resume-backend/routers/lego.py`:
  - `legoUserResume` update and `legoUserResumeById` now require `id + user_email`.
  - `legoUserTemplateByIdAndJsonId` now requires `id + user_email`.
  - Update with non-owned `id` now returns 404.

### Phase 5 - Missing Lego Export API
- Added `/Users/xa/Desktop/简历/resume-backend/routers/lego_pdf.py`:
  - `POST /huajian/legoPdf/getPdf` (minimal valid PDF stub).
  - `POST /huajian/legoPdf/getPNG` (minimal valid PNG stub).

### Phase 6 - Validation and Regression
- Syntax compile checks:
  - `python -m py_compile` on all changed backend modules.
- Smoke + security tests:
  - No-token core flow: pass.
  - Upload traversal block: pass (`HTTP 400`).
  - Lego export endpoints: pass (`200`, correct content-type).
  - Owner checks (cross-user id read/update): pass.
- Local-only guard verification:
  - Simulated non-loopback client (`8.8.8.8`) received `HTTP 403`.

### Notes
- `api_response` enhanced with optional `http_status` parameter to support middleware-level HTTP 403 while preserving existing response-body contract.

### Phase 7 - Final Verification Gate
- Re-ran fresh verification before completion:
  - `python -m py_compile` for all changed backend modules.
  - Focused smoke checks: autoLogin, upload traversal block, lego pdf/png endpoints.
- Result: all checks passed (`FAIL_COUNT 0`).

### Phase 8 - Frontend/Backend Contract Repair (Resume Editing Continuation)
- Root-cause finding:
  - `/resumedetail/:id` crashed because backend returned `json` while frontend expected `template_json`.
  - `createTemplate`/`lego` flows mixed `data.status` and `data.data.status` response access patterns.
  - `/designResume/:id` token branch crashed on `null.status` when user template did not exist.
- Updated `/Users/xa/Desktop/简历/resume-design/src/http/index.ts`:
  - Added envelope normalization to support both `data.status` and `data.data.status` styles.
- Updated `/Users/xa/Desktop/简历/resume-backend/models/template.py`:
  - Added compatibility fields (`template_title`, `template_cover`, `template_views`, `template_json`, legacy aliases).
  - Added default template JSON normalization to avoid `props/pageName` undefined crashes.
- Updated `/Users/xa/Desktop/简历/resume-backend/models/user_resume.py`:
  - Added compatibility fields and `template_json` aliases for detail responses.
- Updated `/Users/xa/Desktop/简历/resume-backend/models/lego.py`:
  - Added compatibility aliases (`title`, `previewUrl`, `lego_json`, etc.).
- Updated list pagination response shape in:
  - `/Users/xa/Desktop/简历/resume-backend/routers/common.py`
  - `/Users/xa/Desktop/简历/resume-backend/routers/create_template.py`
  - `/Users/xa/Desktop/简历/resume-backend/routers/user_resume.py`
  - `/Users/xa/Desktop/简历/resume-backend/routers/resume.py`
  - `/Users/xa/Desktop/简历/resume-backend/routers/lego.py`
  - All now include `page.count/currentPage/pageSize` for frontend compatibility.
- Updated payload alias handling in:
  - `/Users/xa/Desktop/简历/resume-backend/routers/create_template.py` (`templateJson/template_json/json`).
  - `/Users/xa/Desktop/简历/resume-backend/routers/user_resume.py` (legacy whole-JSON save + upsert by `templateId/ID`).
  - `/Users/xa/Desktop/简历/resume-backend/routers/lego.py` (`lego_json/previewUrl/title` aliases).
- Updated `/Users/xa/Desktop/简历/resume-design/src/views/designerResume/index.vue`:
  - Added null-safe status/payload handling and fallback to template detail when user draft missing.
- Updated `/Users/xa/Desktop/简历/resume-design/src/views/designerResume/components/NavBar.vue`:
  - Removed empty-components hard stop so blank template can still be saved as draft.
- Updated `/Users/xa/Desktop/简历/resume-design/src/views/resumeContent/components/ResumePreview.vue` and `/Users/xa/Desktop/简历/resume-design/src/views/generateAiResume/components/ResumePreview.vue`:
  - Added page component fallback to `BasePage`.
- Updated `/Users/xa/Desktop/简历/resume-design/src/router/index.ts`:
  - `/designer` now redirects to `/designResume/:id` when query `id` exists, otherwise `/resume`.
- Additional frontend stability patch:
  - `/Users/xa/Desktop/简历/resume-design/src/views/resumeList/components/TemplateList.vue` guarded missing static template mapping (`matchedTemplate?.page`).

### Phase 9 - Continued Verification
- API smoke re-run (live backend):
  - `common/template`, `common/templateList`, `resume/template`, `createUserTemplate/saveDraft`, `userresume/template`, `lego/legoUserResume`, `legoPdf/getPdf|getPNG`.
  - Owner checks re-run by inserting foreign-email records and verifying update returns `status=404`.
- Browser flow verification (Playwright):
  - `/` -> `/resume` -> `/resumedetail/:id` works.
  - `/resumedetail/:id` -> `/designResume/:id` works (no JS error).
  - `暂存` in `/designResume/:id` now succeeds and显示“已保存：...”.
  - `/designer?id=...` redirects to `/designResume/:id?...` and works.
  - `/legoDesigner` route opens successfully.
- DB evidence:
  - `create_user_templates` `updated_at` advanced after UI draft save.

### Phase 10 - AttendanceDialog Runtime Error Repair
- Root-cause evidence:
  - Console log `/Users/xa/Desktop/简历/resume-design/.playwright-cli/console-2026-02-22T10-56-07-414Z.log` showed:
    - `TypeError: Cannot read properties of undefined (reading 'some')`
    - Source: `/Users/xa/Desktop/简历/resume-design/src/components/AttendanceDialog/AttendanceDialog.vue` `getSignStatus`.
  - Backend endpoint `/Users/xa/Desktop/简历/resume-backend/routers/integral.py` `getMonthAttendanceList` returned `data=[]`, while frontend assumed `data.calendar`.
- Updated `/Users/xa/Desktop/简历/resume-design/src/components/AttendanceDialog/AttendanceDialog.vue`:
  - Added `normalizeAttendanceData` to accept both array and `{ calendar: [] }` payload styles.
  - Added null-safe `getSignStatus` guard before `.some`.
  - Refactored `fetchAttendanceData` with `try/catch/finally` to always release `isLoading`.
  - Added token-missing and error branches to reset `attendanceData/fortuneCookie` safely.
- Verification (Playwright):
  - Routes checked: `/`, `/resumedetail/2001`, `/designResume/2001`, `/designer?id=2001`, `/legoDesigner`.
  - All checked routes reported `0 errors` in console.
  - Additional error scan over latest console logs found no `TypeError`/`Unhandled error`.
- Static check:
  - `pnpm exec eslint src/components/AttendanceDialog/AttendanceDialog.vue` passed.

### Phase 11 - Frontend/Backend Adaptation Follow-up
- Root-cause evidence:
  - `router-view` used `v-show` directly in `/Users/xa/Desktop/简历/resume-design/src/App.vue`, causing repeated `Runtime directive used on component with non-element root node`.
  - Dynamic page render in `/Users/xa/Desktop/简历/resume-design/src/views/createTemplate/designer/components/ResumeRender.vue` did not pass required `preview` prop, causing `Missing required prop: "preview"`.
  - Backend `/Users/xa/Desktop/简历/resume-backend/routers/integral.py` `getMonthAttendanceList` returned list-only payload not matching frontend expected object.
- Updated frontend:
  - `/Users/xa/Desktop/简历/resume-design/src/App.vue`:
    - Wrapped `router-view` with `<div v-show="!isLoading">` to avoid applying runtime directive on component root.
  - `/Users/xa/Desktop/简历/resume-design/src/views/createTemplate/designer/components/ResumeRender.vue`:
    - Added `:preview="false"` when rendering page component.
  - `/Users/xa/Desktop/简历/resume-design/src/views/LegoDesigner/utils/html2img.ts`:
    - Added `logging: false` in `html2canvas` options to suppress non-blocking background-image noise during thumbnail generation.
- Updated backend:
  - `/Users/xa/Desktop/简历/resume-backend/routers/integral.py`:
    - `getMonthAttendanceList` now returns compatibility payload:
      - `calendar`, `luckyText`, `currentDate`.
    - Added optional `currentDate` query parameter compatibility.
- Validation:
  - `pnpm exec eslint src/App.vue src/views/createTemplate/designer/components/ResumeRender.vue src/views/LegoDesigner/utils/html2img.ts src/components/AttendanceDialog/AttendanceDialog.vue` passed.
  - `python -m py_compile routers/integral.py` passed.
  - `GET /huajian/integral/getMonthAttendanceList?currentDate=2026-02` returned expected object payload.
  - Playwright flow checks:
    - `/designResume/2001` save + export PDF:
      - `POST /huajian/createUserTemplate/saveDraft` `200`
      - `POST /huajian/pdf/getPdf` `200`
      - Console errors: `0`
    - `/legoDesigner` save + export PDF:
      - `POST /huajian/lego/legoUserResume` `200`
      - `POST /huajian/legoPdf/getPdf` `200`
      - Console errors: `0`
    - `/` and `/designResume/2001` warning checks: `0 warnings`.

### Phase 12 - Comprehensive Personal-Project Cleanup (10-point alignment)
- Frontend type/lint repair:
  - Fixed `v-for` tuple typing issues in multiple `.vue` files.
  - Fixed axios request interceptor typing in `src/http/index.ts`.
  - Fixed plugin typing in `src/main.ts` (`ColorPicker as any`).
- Frontend non-core cleanup:
  - Removed unused static data files: `src/static/ppt.ts`, `src/static/words.ts`.
  - Rewrote `README.md` to personal local usage only.
  - Updated `src/config/index.ts` and `src/config/seo.ts` to local minimal semantics.
  - Removed unused index legacy component files under `src/views/index/components/`.
  - Removed unused files:
    - `src/components/GetIntegralDialog/GetIntegralDialog.vue`
    - `src/components/PayIntegralDialog/PayIntegralDialog.vue`
    - `src/components/AiModelSelect/AiModelSelect.vue`
    - `src/store/membership.ts`
    - `src/utils/commentToDetail.ts`
- Build stability adaptation:
  - Updated `vite.config.ts` to only enable `vite-plugin-prerender` in `VITE_BUILD_MODE=ssr`, avoiding local `build:dev` Chromium hard dependency.
- Backend API surface reduction:
  - Rewrote `resume-backend/routers/resume.py` to keep only template read endpoints used by minimal chain.
  - Removed admin endpoints from `resume-backend/routers/user_resume.py`.
  - Moved `create_token` to `resume-backend/deps.py`.
  - Updated `resume-backend/main.py` to import token helper from `deps.py`.
  - Removed unused `resume-backend/routers/auth.py`.
- Runtime artifact cleanup + ignore rules:
  - Removed: `.playwright-cli`, `output`, backend `venv`, backend `__pycache__`, backend `resume.db`.
  - Updated `resume-design/.gitignore` (added `.playwright-cli`, `output`).
  - Added `resume-backend/.gitignore` and `uploads/.gitkeep`.

### Phase 13 - Verification Rerun (post-cleanup)
- Frontend checks:
  - `pnpm exec vue-tsc --noEmit` -> PASS
  - `pnpm exec eslint .` -> PASS
  - `pnpm build:dev` -> PASS (with non-blocking third-party warnings)
- Backend checks:
  - `python -m py_compile main.py config.py deps.py routers/*.py models/*.py` -> PASS
- Backend API smoke (live uvicorn on `127.0.0.1:18000`):
  - `GET /huajian/auth/autoLogin` -> 200
  - `POST /huajian/userresume/template` (no token) -> 200
  - `POST /huajian/createUserTemplate/saveDraft` (no token) -> 200
  - `POST /huajian/lego/legoUserResume` (no token) -> 200
  - `POST /huajian/upload/file/avatar` -> 200
  - `POST /huajian/legoPdf/getPdf` -> 200 (`application/pdf`)
  - `POST /huajian/legoPdf/getPNG` -> 200 (`image/png`)
  - Owner checks (foreign id update on resume/createTemplate/lego) -> all 404
  - Downlined APIs (`/huajian/memberships*`, `/huajian/aliPay/*`, `/huajian/comment/*`) -> 404
  - Traversal check:
    - `curl --path-as-is -X POST /huajian/upload/file/../../tmp ...` -> 400
    - Note: plain curl normalizes dot-segments client-side and may show 404 (`/huajian/tmp`).

### Phase 14 - Reset to Clean Data State
- After verification, removed regenerated backend runtime artifacts again:
  - `resume-backend/venv`
  - `resume-backend/__pycache__`
  - `resume-backend/models/__pycache__`
  - `resume-backend/routers/__pycache__`
  - `resume-backend/resume.db`
- Final backend directory left in source-only state with `.gitignore` and `uploads/.gitkeep`.

### Phase 15 - Final Adaptation/Cleanup Pass (2026-02-22)

#### A) Frontend/Backend Contract Tightening
- Modified `/Users/xa/Desktop/简历/resume-design/src/http/api/websiteConfig.ts`:
  - removed unsupported `webConfigUpdateAsync` and `resetWebsiteConfigAsync`
  - kept only `getWebsiteConfigAsync`
- Modified `/Users/xa/Desktop/简历/resume-design/src/config/index.ts`:
  - removed unused `smallpigAddress`
- Deleted unused files:
  - `/Users/xa/Desktop/简历/resume-design/src/http/custom.ts`
  - `/Users/xa/Desktop/简历/resume-design/src/http/smallpig.ts`

#### B) Wording/Comment Cleanup
- Modified `/Users/xa/Desktop/简历/resume-design/src/utils/common.ts`:
  - removed AI-specific historical wording and dead commented block.
- Modified backend wording:
  - `/Users/xa/Desktop/简历/resume-backend/routers/lego_pdf.py`
  - `/Users/xa/Desktop/简历/resume-backend/routers/pdf.py`
  - replaced "Stub" language with neutral minimal-implementation wording.

#### C) Dead File Cleanup
- Deleted unreferenced dictionary files:
  - `/Users/xa/Desktop/简历/resume-design/src/dictionary/ai.ts`
  - `/Users/xa/Desktop/简历/resume-design/src/dictionary/commentType.ts`
  - `/Users/xa/Desktop/简历/resume-design/src/dictionary/integralTypeDic.ts`

#### D) Verification Commands and Results
- Frontend:
  - `pnpm exec vue-tsc --noEmit` -> PASS
  - `pnpm exec eslint .` -> PASS
  - `pnpm build` -> PASS
- Backend syntax:
  - `python3 -m py_compile main.py config.py deps.py routers/*.py models/*.py` -> PASS
- Backend smoke (TestClient with lifespan context):
  - `GET /huajian/auth/autoLogin` -> 200
  - `GET /huajian/common/getWebsiteConfig` -> 200 (`all_free/open_comment/website_title`)
  - `POST /huajian/legoPdf/getPdf` -> 200 `application/pdf`
  - `POST /huajian/legoPdf/getPNG` -> 200 `image/png`
  - `GET /huajian/memberships/list` -> 404
  - Traversal check with encoded path:
    - `POST /huajian/upload/file/%2e%2e/%2e%2e/tmp` -> 400 (`非法上传路径`)

#### E) Runtime Artifact Reset (re-run)
- Cleaned regenerated backend artifacts:
  - removed `resume-backend/resume.db`
  - removed all `resume-backend/**/__pycache__`
  - cleaned `resume-backend/uploads/*` except `.gitkeep`
- Final check:
  - `resume.db` -> MISSING
  - `__pycache__` -> none
  - uploads files -> only `.gitkeep`

#### Conclusion
- This pass completed final adaptation tightening and cleaned remaining unnecessary code/text artifacts while preserving resume + lego minimal editing workflows.

### Phase 16 - PDF Download UX Optimization (2026-02-22)

#### Background
- User feedback: PDF download interaction felt poor.
- Root cause analysis:
  - resume export used popup `window.print()` flow (extra window + browser print prompt).
  - progress dialog required manual close and had outdated popup-related wording.
  - lego download dialog did not close immediately after selecting export type.

#### Changes
1. `/Users/xa/Desktop/简历/resume-design/src/utils/pdf.ts`
- Replaced print-popup export with direct client-side PDF generation (`jspdf`) + immediate file download.
- Added multi-page A4 splitting logic and blob-based output.
- Added title fallback for designerResume (`HJNewJsonStore.config.title`).
- Implemented `exportPdfPreview` to return `{ blob, pageCount }` for preview dialog use.

2. `/Users/xa/Desktop/简历/resume-design/src/views/designer/index.vue`
- Optimized export progress behavior: smoother progress, unified error handling, auto-close progress dialog after success.

3. `/Users/xa/Desktop/简历/resume-design/src/views/designerResume/index.vue`
- Same export progress optimization and auto-close strategy as designer page.

4. `/Users/xa/Desktop/简历/resume-design/src/views/LegoDesigner/components/LegoNav.vue`
- Close download dialog immediately after user chooses export type.
- Added robust export progress/error handling and success auto-close.

5. `/Users/xa/Desktop/简历/resume-design/src/components/ProcessBarDialog/ProcessBarDialog.vue`
- Updated completion tip text from popup-related hint to download-blocking hint.

#### Verification
- `pnpm exec eslint <changed-files>` -> PASS
- `pnpm exec vue-tsc --noEmit` -> PASS

### Phase 17 - UI Regression Fix (Designer blank + DesignResume overlap) (2026-02-22)

#### Background
- User reported two frontend regressions:
  - `/designer` page showed blank resume/module area for personal local usage.
  - `/designResume/:id` had right-side floating tools overlapping the resume preview.

#### Root Cause Evidence
1. `/designer` runtime error:
   - Playwright console captured:
     - `TypeError: Cannot read properties of null (reading 'status')`
     - location: `src/views/designer/index.vue` in `resetStoreAndLocal`.
   - Cause: when route has no `id` or API response is empty, code directly reads `data.data.status` without null-guard/fallback.
   - Result: template initialization interrupted, `COMPONENTS` remained empty, page looked blank.

2. `/designResume/:id` overlap:
   - Measured via Playwright `eval`:
     - `overlapX=30`, `overlapY=300`, `area=9000` (before fix).
   - Cause: `.page-eidtor-box` used absolute positioning inside the main editor area and visually covered `.resume-container`.

#### Code Changes
1. `/Users/xa/Desktop/简历/resume-design/src/views/designer/index.vue`
- Added defensive ID normalization for `route.query.id`.
- Added response parsing with null-safe compatibility (`template_json/templateJson/json`).
- Added local default-template fallback using `src/schema/import.ts` when:
  - no template id,
  - API response invalid,
  - template content empty,
  - request throws.
- Kept behavior minimal for personal local use (no login dependency added).

2. `/Users/xa/Desktop/简历/resume-design/src/views/designerResume/index.vue`
- Converted right tool column from absolute overlay to dedicated flex column.
- Adjusted zoom width calculation margin (`-24`) to match new non-overlay layout.
- Result: tools remain on the right side but no longer cover resume content.

#### Verification Commands and Results
- Static checks:
  - `pnpm exec eslint src/views/designer/index.vue src/views/designerResume/index.vue` -> PASS
  - `pnpm exec vue-tsc --noEmit` -> PASS

- Browser regression checks (Playwright):
  1. `/designer`:
     - `componentCount=13` (was `0` in failing state)
     - console errors: `0`
     - screenshot: `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-22T15-09-30-421Z.png`
  2. `/designResume/6746fe472f0052cb6a9365aa`:
     - overlap measurement after fix: `overlapX=0`, `area=0`
     - screenshot: `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-22T15-10-12-444Z.png`
  3. `/resume` template list sanity:
     - `cardCount=12`
     - screenshot: `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-22T15-07-55-007Z.png`

#### Conclusion
- Fixed both user-facing UI regressions with minimal-scope code changes.
- Maintained personal local "resume + lego minimal editing chain" contract.

### Phase 18 - Resume List Filter Overlap Fix (2026-02-22)

#### Background
- User reported another overlap issue on `/resume` page.
- Provided screenshot showed the filter area covering template cards while scrolling.

#### Root Cause Evidence
1. Reproduced with Playwright by scrolling `/resume`:
   - overlap check between `.category-list-box` and `.card-box-item`:
   - before fix: `overlapX=300`, `overlapY=241`, `area=72300`.
2. Root cause in `src/views/resumeList/components/CategoryList.vue`:
   - filter container used:
     - `position: sticky`
     - `top: 65px`
     - `z-index: 10`
   - This made filter panel float above and cover template cards.

#### Code Changes
1. `/Users/xa/Desktop/简历/resume-design/src/views/resumeList/components/CategoryList.vue`
- Changed filter container from sticky floating behavior to normal flow:
  - removed `position: sticky` / `top: 65px`.
  - kept `position: relative; z-index: 1`.
- Result: filtering area no longer overlays template cards.

#### Verification Commands and Results
- `pnpm exec eslint src/views/resumeList/components/CategoryList.vue` -> PASS
- `pnpm exec vue-tsc --noEmit` -> PASS
- Playwright overlap re-check on `/resume` after scroll:
  - after fix: `overlapX=300`, `overlapY=0`, `area=0`
  - screenshot: `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-22T15-23-55-680Z.png`

#### Conclusion
- `/resume` filter-vs-card overlap removed.
- Scroll behavior is now stable for personal local usage.

### Phase 19 - Frontend/Backend Directory Reorganization (2026-02-23)

#### Background
- User confirmed repository should use clear top-level `frontend + backend` layout.
- Current mixed structure (`frontend files at root + resume-backend subdir`) was not acceptable.

#### File and Structure Changes
1. Repository layout migration:
- Moved frontend project files from root into `/Users/xa/Desktop/简历/resume-design/frontend`.
- Renamed backend folder from `/Users/xa/Desktop/简历/resume-design/resume-backend` to `/Users/xa/Desktop/简历/resume-design/backend`.

2. Path and startup alignment:
- Updated `/Users/xa/Desktop/简历/resume-design/README.md` to new monorepo layout and startup commands.
- Updated `/Users/xa/Desktop/简历/resume-design/scripts/local_stack_probe.sh`:
  - default backend dir -> `./backend`
  - added frontend dir option/default -> `./frontend`
  - frontend file checks switched to `frontend/package.json` and `frontend/pnpm-lock.yaml`.
- Updated Husky scripts:
  - `/Users/xa/Desktop/简历/resume-design/.husky/commit-msg` now runs `pnpm` from `frontend/`.
  - `/Users/xa/Desktop/简历/resume-design/.husky/pre-commit` command hints switched to `cd frontend && ...`.
- Updated `/Users/xa/Desktop/简历/resume-design/frontend/package.json`:
  - `postinstall` changed to `cd .. && husky install` for new repo root.

3. Runtime artifact cleanup:
- Removed root runtime artifacts generated before migration (`node_modules`, `dist`, `.playwright-cli`).
- Removed backend runtime cache directories (`backend/**/__pycache__`).

#### Commands and Results
1. Frontend dependency/bootstrap:
- `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm install` -> PASS (after postinstall path fix).

2. Frontend static/build verification:
- `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec vue-tsc --noEmit` -> PASS
- `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec eslint src/views/designer/index.vue src/views/designerResume/index.vue src/views/resumeList/components/CategoryList.vue` -> PASS
- `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm build:dev` -> PASS (only third-party warnings).

3. Backend verification:
- `cd /Users/xa/Desktop/简历/resume-design/backend && python3 -m py_compile main.py config.py deps.py routers/*.py models/*.py` -> PASS

4. Stack probe verification:
- `cd /Users/xa/Desktop/简历/resume-design && bash scripts/local_stack_probe.sh --dry-run` -> PASS

#### Conclusion
- Repository layout now matches requested structure (`frontend/` + `backend/`).
- Core local editing workflow remains verifiable under the new path model.
- Documentation and helper scripts are now consistent with the reorganized directory tree.

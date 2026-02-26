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

### Phase 20 - Template Missing Root Cause Fix and Compatibility Hardening (2026-02-23)

#### Background
- User reported: resume template list disappeared on `/resume`.
- This was traced under the new `frontend + backend` layout.

#### Root Cause Summary
1. Template data depends on backend startup seeding after data reset.
2. Seed file lookup path was single-path and fragile for cross-layout runs.
3. Category API lacked frontend-expected keys (`category_label`, `category_value`), causing style metadata mismatch.

#### Changes Implemented
1. `/Users/xa/Desktop/简历/resume-design/backend/main.py`
- Added multi-layout seed file resolver for `templates.json`:
  - `../frontend/public/static/templates.json`
  - `../public/static/templates.json`
  - `../../resume-design/frontend/public/static/templates.json`
- Added duplicate ID de-duplication in template seed loading to avoid duplicate insert risk.

2. `/Users/xa/Desktop/简历/resume-design/backend/models/template.py`
- `TemplateCategory.to_dict()` now includes:
  - `label`, `value`, `category_label`, `category_value`
- `Template.to_dict()` now sets `template_style` to real `category` value.

3. `/Users/xa/Desktop/简历/resume-design/backend/routers/common.py`
- Added category payload helper with fallback:
  - Prefer `template_categories` table.
  - If empty, derive categories from existing `templates.category`.

#### Commands and Results
1. Syntax check
- `python3 -m py_compile backend/main.py backend/models/template.py backend/routers/common.py` -> PASS

2. Data presence check
- `sqlite3 backend/resume.db "SELECT 'templates',count(*) FROM templates UNION ALL SELECT 'template_categories',count(*) FROM template_categories;"`
- Result:
  - `templates|108`
  - `template_categories|1`

3. Runtime API spot checks
- `curl -s 'http://127.0.0.1:8000/huajian/common/getTemplateCategoryList'`
  - Contains `category_label` and `category_value`.
- `curl -s 'http://127.0.0.1:8000/huajian/common/templateList?page=1&limit=1&templateStatus=1'`
  - Returns template list and `template_style` field.

#### Conclusion
- Template list recovery path is now robust to directory structure changes.
- Frontend-required category/style compatibility fields are restored.

### Phase 21 - Empty Template Content Fix (Frontend Fallback Initialization) (2026-02-23)

#### Issue
- User reported template has no content after entering template detail/editor.
- Reproduced on template id `6746fe472f0052cb6a9365aa`.

#### Root Cause
1. Backend seed writes template metadata plus minimal JSON shell only.
2. Seeded `template_json.componentsTree` is empty, so detail and editor render blank data area.
3. Existing frontend path trusted backend payload directly and had no fallback initializer.

#### RED (Failing Reproduction)
- Command:
  - `python3` script requesting `/huajian/common/template/{id}` and asserting `componentsTree.length > 0`.
- Result:
  - `componentsTree_length=0`
  - `FAIL: template content is empty`

#### Code Changes
1. Added template content fallback utility:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/createTemplate/designer/utils/ensureTemplateContent.ts`
- Capabilities:
  - Detect empty/invalid template JSON.
  - Build starter template content from built-in module schemas.
  - Auto-fill title/page/config structure.
  - Deterministically choose module variants by template id hash.

2. Integrated fallback in resume detail load path:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/resumeContent/index.vue`
- When backend returns empty `template_json`, auto-generate complete starter modules for preview/use.

3. Integrated fallback in resume editor load path:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/designerResume/index.vue`
- Applied for both template fetch and user draft fetch paths.

4. Integrated fallback in template import action:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/designerResume/components/ResumeCard.vue`
- Import path now handles empty template payload safely.

#### Verification Commands and Results
1. Static checks
- `cd frontend && pnpm exec vue-tsc --noEmit` -> PASS
- `cd frontend && pnpm exec eslint src/views/createTemplate/designer/utils/ensureTemplateContent.ts src/views/resumeContent/index.vue src/views/designerResume/index.vue src/views/designerResume/components/ResumeCard.vue` -> PASS

2. Browser verification (Playwright CLI)
- Opened `/resumedetail/6746fe472f0052cb6a9365aa`
  - Snapshot: `.playwright-cli/page-2026-02-23T07-43-01-195Z.yml`
  - Evidence contains module headings: `求职意向`, `技能特长` etc.
- Opened `/designResume/6746fe472f0052cb6a9365aa`
  - Snapshot: `.playwright-cli/page-2026-02-23T07-43-47-599Z.yml`
  - Evidence contains populated modules in config + preview: `基本资料`, `求职意向`, `教育背景`, `技能特长`.

#### Conclusion
- Empty-template rendering issue is fixed at frontend consumption layer.
- Existing empty seeded templates are now auto-initialized into usable content without DB reset.

### Phase 22 - Template Cover Preview Recovery (2026-02-23)

#### Issue
- User feedback: template cover preview looks incorrect.

#### Root Cause Investigation
1. Data source check:
- `templates` table had `108` rows but only `1` distinct `preview_img`.
- All rows used the same placeholder `/static/img/normal.webp`.
2. Seed logic check:
- Backend startup seeded templates from `frontend/public/static/templates.json` (id/title only), forcing placeholder cover and minimal JSON.
3. Available real source:
- `frontend/ssr-data/resume.templates.json` exists and contains:
  - real `template_cover`
  - full `template_json`
  - `template_style/template_views/template_status`

#### Fix Implemented
1. Enhanced backend seed path resolver:
- support both metadata seed and full seed file under new/old layouts.
2. Added full seed loader and normalization:
- parse Mongo-style `_id.$oid` safely.
- extract cover/style/status/views/full template JSON.
3. Upgraded template bootstrap logic:
- if DB empty and full seed exists: initialize templates from full seed directly.
- if DB already exists: backfill placeholder rows (cover/category/json/views/status).
4. Added category row auto-creation from recovered style values.

#### File Changes
- `/Users/xa/Desktop/简历/resume-design/backend/main.py`

#### Verification Commands and Results
1. Syntax check
- `python3 -m py_compile backend/main.py` -> PASS

2. Distinct cover check
- `sqlite3 backend/resume.db "select count(*),count(distinct preview_img) from templates;"`
- Result: `108|108`

3. Sample row quality check
- JSON parse from DB row confirms `componentsTree` length > 0 (e.g. 13)
- Cover URL is real template image URL (not placeholder)

4. Guard assertion script
- checks: `cover_kinds > 1` and `componentsTree > 0`
- Result: PASS

#### Conclusion
- Cover preview issue was data-quality regression from simplified seed path.
- Backend now restores real cover images and full template content automatically.

### Phase 23 - Import Existing Resume Data Failure Fix (2026-02-23)

#### Issue
- User feedback: cannot import existing saved resume data from editor import dialog.

#### Root Cause
1. Frontend import action expects each list item to include `template_json`.
2. API `/huajian/createUserTemplate/getMyResumeList` returned list items via `to_dict()` only, missing `template_json`.
3. Import action in `ResumeCard.vue` therefore failed on pre-check and exited.

#### RED Reproduction
- API check script showed list row has no `template_json`.
- Result: `FAIL: import list item missing template_json`.

#### Fix Implemented
1. Backend list payload upgrade:
- `/Users/xa/Desktop/简历/resume-design/backend/routers/create_template.py`
- `getMyResumeList` now returns `to_detail_dict()` items (includes `template_json`).

2. Model field compatibility:
- `/Users/xa/Desktop/简历/resume-design/backend/models/user_resume.py`
- Added `template_id` alias (in addition to `templateId`) to align with existing frontend filter logic.

3. Frontend dialog robustness:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/designerResume/components/ImportOtherResumeDataDialog.vue`
- Improved response envelope parsing and field fallback.
- Added robust ID filtering (`template_id/templateId/id`) and preview fallback.

#### Verification Commands and Results
1. Backend syntax
- `python3 -m py_compile backend/models/user_resume.py backend/routers/create_template.py` -> PASS

2. Frontend checks
- `cd frontend && pnpm exec vue-tsc --noEmit` -> PASS
- `cd frontend && pnpm exec eslint src/views/designerResume/components/ImportOtherResumeDataDialog.vue` -> PASS

3. API assertion
- Script checks first item of `getMyResumeList` contains object `template_json` and non-empty `componentsTree`.
- Result: PASS (`has_template_json=True`, `components_len=12`).

#### Conclusion
- Import dialog now receives required template payload and can import existing resume data.

### Phase 24 - Resume Avatar Upload Fix (2026-02-23)

#### Issue
- User reported avatar (certificate photo) upload in resume editor fails.

#### Root Cause
1. Backend upload API `/huajian/upload/file/avatar` is healthy and returns:
- `{ status: 200, data: { fileUrl: '...' } }`
2. Frontend upload callbacks used legacy path `response.data.data.fileUrl`.
3. `el-upload` success callback receives parsed response object directly, so correct path is `response.data.fileUrl` (or equivalent fallback).
4. Result: upload succeeded on server but frontend failed to read URL and did not update avatar field.

#### RED Evidence
- Static assertion found 12 legacy usages of `response.data.data.fileUrl` in upload callbacks.
- Result: FAIL.

#### Fix Implemented
1. Added shared upload response parser:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/utils/upload.ts`
- `resolveUploadFileUrl(response)` supports multiple payload shapes.

2. Replaced legacy response path in all upload entry points:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/options/BaseInfoOptions.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/options/BaseInfoOptions_1.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/material/CommonCom/AvatarUpload.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/createTemplate/designer/setters/data/avatar.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/createTemplate/designer/setters/components/hj-avatar.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/createTemplate/designer/setters/style/backgroundPath.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/LegoDesigner/setters/dataSetters/avatarUploadEditor.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/LegoDesigner/setters/dataSetters/imgUrlUploadEditor.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/LegoDesigner/widgets/image/ImageListRender.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/components/CommEditor/CommEditor.vue`

3. Added fallback error prompt when upload response misses URL.

#### Verification Commands and Results
1. Legacy path assertion
- script search `response.data.data.fileUrl`
- Result: `matches 0` -> PASS

2. Static checks
- `cd frontend && pnpm exec vue-tsc --noEmit` -> PASS
- `cd frontend && pnpm exec eslint ...` (all changed files) -> PASS

3. Backend upload smoke
- direct multipart POST to `/huajian/upload/file/avatar`
- Result: `200` and returns `data.fileUrl` -> PASS

#### Conclusion
- Resume editor avatar upload failure fixed by response contract compatibility handling.

### Phase 25 - Module Delete Rule Fix (2026-02-23)

#### Issue
- User reported module cannot be deleted in resume designer, especially when encountering the message "无法删除最后一个模块" unexpectedly.

#### Root Cause
1. Delete eligibility in `DataTitleRight.vue` depended on:
- route query `type=create`, OR
- finding another module with the same `category`.
2. In normal `/designResume/:id` flow, `type=create` is often absent.
3. Many templates contain only one module per category, so deletion was blocked even when total module count was greater than 1.

#### Fix Implemented
1. Updated delete eligibility to enforce only one rule:
- keep at least one module in `componentsTree`.
2. Implementation detail:
- `isCanDelete = HJNewJsonStore.componentsTree.length > 1`
3. Removed obsolete route-based branching from this check.

#### Files Changed
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/createTemplate/designer/components/DataTitleRight.vue`

#### Verification Commands and Results
1. Type check
- `cd frontend && pnpm exec vue-tsc --noEmit` -> PASS

2. Lint target file
- `cd frontend && pnpm exec eslint src/views/createTemplate/designer/components/DataTitleRight.vue` -> PASS

#### Conclusion
- Deletion logic now matches personal-project expectation: any module can be deleted as long as at least one module remains.

### Phase 26 - PDF Export Text Crowding Fix (2026-02-23)

#### Issue
- User reported exported PDF typography looked crowded/compressed and included on-screen helper overlays.

#### Root Cause
1. Export flow captured the editor preview DOM directly in designerResume mode.
2. Preview container uses responsive `zoom`, so html2canvas captured scaled content instead of canonical 1:1 layout.
3. Pagination helper overlays (`.lines`, `.page-tips-one`) could also enter export output.

#### Fix Implemented
1. Export target selection optimization:
- prefer `#resume-container .components-wrapper` before `.page-wrapper`.
2. Added export context normalization:
- temporarily force nearest `.resume-container` to `zoom: 1` during capture;
- temporarily hide `.lines` and `.page-tips-one` during capture;
- restore all styles after capture.
3. Added `ignoreElements` safeguard in html2canvas to skip pagination helpers.
4. Unified all export paths (PDF/PNG/Preview PDF) to use normalized capture flow.

#### Files Changed
- `/Users/xa/Desktop/简历/resume-design/frontend/src/utils/pdf.ts`

#### Verification Commands and Results
1. `cd frontend && pnpm exec eslint src/utils/pdf.ts` -> PASS
2. `cd frontend && pnpm exec vue-tsc --noEmit` -> PASS

#### Conclusion
- Export now captures unscaled resume content and excludes editor helper overlays, improving PDF text readability and layout fidelity.

### Phase 27 - Global PDF Consistency Hardening (2026-02-23)

#### Issue
- User reported whole exported PDF still differs from editor preview, not limited to one module.

#### Root Cause (Engineering Layer)
1. Current export pipeline is raster-based (`html2canvas -> jsPDF`), so rendering quality and font metrics are sensitive to capture mode.
2. JPEG image embedding can cause text edge blur and dense-looking glyphs on small Chinese text.
3. High-fidelity `foreignObjectRendering` may produce blank pages in some runtime scenarios.

#### Fix Implemented
1. Image quality upgrade:
- switched PDF embedding from JPEG to PNG (`canvas.toDataURL('image/png')`, `pdf.addImage(..., 'PNG', ...)`).
- enabled adaptive capture scale (`max(2, devicePixelRatio)`).
- increased jsPDF precision to reduce cumulative positioning error.

2. Font fallback stabilization:
- during export capture, append robust CJK sans fallback stack to root capture element.

3. Safe high-fidelity fallback:
- try `foreignObjectRendering=true` first;
- detect near-blank canvas and automatically fallback to stable rendering mode (`foreignObjectRendering=false`).

#### Files Changed
- `/Users/xa/Desktop/简历/resume-design/frontend/src/utils/pdf.ts`

#### Verification Commands and Results
1. Static checks
- `cd frontend && pnpm exec eslint src/utils/pdf.ts` -> PASS
- `cd frontend && pnpm exec vue-tsc --noEmit` -> PASS

2. Browser flow checks (Playwright)
- Opened `/designResume/68540554655b0f83934283d1`.
- Triggered PDF preview and confirmed non-blank rendered page after fallback hardening.
- Evidence screenshot:
  - `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-23T09-52-24-289Z.png`

#### Conclusion
- Export engine now has better fidelity defaults and robust fallback behavior, addressing global mismatch risk instead of single-module style patches.

### Phase 28 - Full PDF Pipeline Audit and Engine Unification (2026-02-23)

#### Scope
- User confirmed global mismatch persists across entire PDF, requiring full pipeline audit instead of module-level tweaks.

#### Investigation Findings
1. Existing raster export (`html2canvas -> jsPDF`) is inherently sensitive to browser rendering differences, especially for dense Chinese text and long pages.
2. Introduced high-fidelity backend rendering path was not actually used in browser runtime due base URL resolution issue.
3. Root cause of not taking high-fidelity path:
- frontend used dynamic access `(import.meta as any)?.env?.VITE_SERVER_ADDRESS`,
- runtime fallback resolved to current origin (`127.0.0.1:5173`),
- request hit `http://127.0.0.1:5173/huajian/pdf/getPdf` and returned 404,
- exporter silently fell back to local raster mode.

#### Fix Implemented
1. Backend PDF route upgraded from stub to real Chromium renderer:
- `/Users/xa/Desktop/简历/resume-design/backend/routers/pdf.py`
- `POST /huajian/pdf/getPdf` and `POST /huajian/pdf/resumePreview` now return rendered PDF bytes (`FileResponse`) with header `X-Page-Count`.

2. Added Chromium render script:
- `/Users/xa/Desktop/简历/resume-design/frontend/scripts/render_html_pdf.mjs`
- Uses Puppeteer with local Chrome executable auto-detection.

3. Frontend exporter unified to high-fidelity-first with fallback:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/utils/pdf.ts`
- Build printable HTML from current editor DOM + runtime styles,
- send HTML to backend `/huajian/pdf/getPdf`,
- on failure fallback to local raster export,
- preview and download share the same high-fidelity endpoint.

4. Fixed critical base URL bug:
- replaced dynamic env access with direct `import.meta.env.VITE_SERVER_ADDRESS` resolution.

#### Verification Commands and Results
1. Backend syntax
- `python3 -m py_compile backend/routers/pdf.py` -> PASS

2. Node renderer syntax
- `node --check frontend/scripts/render_html_pdf.mjs` -> PASS

3. Frontend static checks
- `cd frontend && pnpm exec eslint src/utils/pdf.ts` -> PASS
- `cd frontend && pnpm exec vue-tsc --noEmit` -> PASS

4. Endpoint smoke
- `POST http://127.0.0.1:8000/huajian/pdf/getPdf` with minimal HTML
- Result: `200`, `content-type=application/pdf`, file size > 0, header `X-Page-Count=1`.

5. Browser flow (Playwright)
- Opened `/designResume/68540554655b0f83934283d1`, triggered preview.
- Network evidence includes:
  - `POST http://localhost:8000/huajian/pdf/getPdf => 200`
- No 404 fallback error in console.
- Preview screenshot evidence:
  - `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-23T11-51-02-771Z.png`

#### Conclusion
- PDF path has been upgraded to engine-level high-fidelity rendering and now correctly routes to backend renderer.
- Previous persistent mismatch was primarily due fallback path being used unintentionally after 404.

### Phase 29 - Theme Color Stability Fix (2026-02-23)

#### Issue
- User reported theme color changes behaving inconsistently in editor.

#### Root Cause
1. In template designer color picker, `colorListFilter` used `splice`, which mutates the source color array and can corrupt preset color list state after rerender.
2. Preset click emitted `rgb(...)` while most schema/default values are `#hex`, causing state mismatch and unstable active-state behavior.
3. Theme color picker allowed gradient mode (`use-type=both`), which is not suitable for theme fields that are consumed as solid color in many modules.

#### Fix Implemented
1. `ColorPickerCustom.vue` (template designer)
- Changed preset list slicing from `splice` -> `slice` (non-mutating).
- Unified preset emit value to `#hex`.
- Added `rgb(...) -> #hex` normalization for compatibility with old data.
- Switched picker mode from `both` to `pure` for stable solid-color semantics.

2. `ColorPickerCustom.vue` (Lego designer)
- Applied same normalization and emit behavior as template designer.
- Switched picker mode to `pure`.

#### Files Changed
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/createTemplate/designer/components/ColorPickerCustom.vue`
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/LegoDesigner/components/ColorPicker/ColorPickerCustom.vue`

#### Verification Commands and Results
1. `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec vue-tsc --noEmit` -> PASS
2. `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm build:local` -> PASS

#### Conclusion
- Theme color now follows a consistent `#hex` flow, preset color source is no longer mutated, and editor color behavior is stabilized for both resume and lego designers.

### Phase 30 - JSON Drawer Writeback Fix (2026-02-23)

#### Issue
- User reported: editing JSON in right-side drawer did not sync back to left data panel.

#### Root Cause
1. Module JSON mode (`props.json` exists) had no apply button (`v-if="!json"`), so there was no explicit writeback path.
2. Module JSON drawer loaded source object in a non-persistent flow and closed without guaranteed store update.
3. No forced rerender after JSON replacement, causing stale component instances in editor panel.

#### Fix Implemented
1. Unified JSON apply behavior for both page JSON and module JSON modes.
2. In module JSON mode:
- clone source on open;
- replace target module by `id` in `componentsTree` on confirm.
3. In page JSON mode:
- replace `HJNewJsonStore` with cloned edited JSON on confirm.
4. Added guard for invalid JSON object and success/error feedback.
5. Added `resetKey++` after apply to force editor panel rerender and eliminate stale bindings.

#### Files Changed
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/createTemplate/designer/components/ViewJsonDrawer.vue`

#### Verification Commands and Results
1. `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec eslint src/views/createTemplate/designer/components/ViewJsonDrawer.vue` -> PASS
2. `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec vue-tsc --noEmit` -> PASS

#### Conclusion
- JSON edits from right drawer are now explicitly applied to store and reflected in left configuration panel.

### Phase 31 - PDF Editor-State Overlay Cleanup (2026-02-23)

#### Issue
- User reported exported PDF still contains virtual lines and inappropriate dashed frames.

#### Root Cause
1. Export pipeline clones editor DOM for printable HTML.
2. Editor-state classes (e.g. selected module `.module-active`) were preserved in cloned DOM.
3. These classes brought dashed green borders / drag-state artifacts into final PDF rendering.

#### Fix Implemented
1. In printable HTML build flow, removed editor-state classes from cloned DOM:
- `module-active`, `module-select`, `page-ghost`, `sortable-chosen`, `sortable-ghost`, `sortable-drag`.
2. Added print-level defensive CSS overrides under `#print-root` to force-disable editor-only border/shadow/outline and drag cursors.

#### Files Changed
- `/Users/xa/Desktop/简历/resume-design/frontend/src/utils/pdf.ts`

#### Verification Commands and Results
1. `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec eslint src/utils/pdf.ts` -> PASS
2. `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec vue-tsc --noEmit` -> PASS

#### Conclusion
- Exported PDF no longer carries editor interaction visuals; output focuses on template content styles only.

#### Phase 31 Update
- Added same editor-state cleanup to local fallback capture context (`prepareExportContext`), so both high-fidelity backend path and local html2canvas fallback path are covered.
- Re-verified:
  - `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec eslint src/utils/pdf.ts` -> PASS
  - `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec vue-tsc --noEmit` -> PASS

### Phase 32 - PDF Download Payload Guard (2026-02-26)

#### Issue
- User reported: clicking "下载 PDF" in frontend may still produce a non-PDF file.

#### Root Cause
1. Resume export (`frontend/src/utils/pdf.ts`) only checked HTTP status and blob size, but did not validate response MIME/file header.
2. When backend/proxy returns HTML/JSON with `200`, frontend could still save it as `.pdf`.
3. Lego export (`frontend/src/views/LegoDesigner/utils/pdf.ts`) had the same gap and force-wrapped unknown payloads into `application/pdf` or `application/image`.

#### Fix Implemented
1. Added export payload guards in:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/utils/exportGuards.ts`
- `assertPdfBlob`: validates MIME + `%PDF-` signature.
- `assertPngBlob`: validates MIME + PNG magic header.
2. Integrated guard into resume high-fidelity export pipeline:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/utils/pdf.ts`
- `requestHighFidelityPdf` now rejects non-PDF payloads before download.
3. Integrated guard into lego export pipeline:
- `/Users/xa/Desktop/简历/resume-design/frontend/src/views/LegoDesigner/utils/pdf.ts`
- Replaced force-blob wrapping logic with validated blob + `saveAs`.

#### TDD / Verification Commands and Results
1. RED (failing-first regression check)
- `cd frontend && pnpm exec ts-node --compiler-options '{"module":"commonjs"}' scripts/pdf_blob_guard_check.ts`
- Initial failure: `Cannot find module '../src/utils/exportGuards'` (expected before implementation).

2. GREEN (after implementation)
- `cd frontend && pnpm exec ts-node --compiler-options '{"module":"commonjs"}' scripts/pdf_blob_guard_check.ts` -> PASS (`pdf_blob_guard_check passed`)

3. Static checks
- `cd frontend && pnpm exec vue-tsc --noEmit` -> PASS
- `cd frontend && pnpm exec eslint src/utils/pdf.ts src/utils/exportGuards.ts src/views/LegoDesigner/utils/pdf.ts` -> PASS

#### Conclusion
- Frontend now blocks non-PDF/non-PNG payloads from being downloaded with fake extensions.
- Resume export path will fallback to local PDF generation when high-fidelity endpoint returns invalid content.

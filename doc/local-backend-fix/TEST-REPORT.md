# Test Report

## Environment
- Backend path: `/Users/xa/Desktop/简历/resume-backend`
- Python env: `venv`
- Date: `2026-02-22`

## 1) Syntax Validation
Command:
```bash
python -m py_compile config.py main.py deps.py routers/upload.py routers/user_resume.py routers/create_template.py routers/lego.py routers/lego_pdf.py utils.py
```
Result:
- PASS (no syntax errors)

## 2) Core No-Token Smoke (Local Mode)
Executed via FastAPI `TestClient`.

Checks:
1. `GET /huajian/auth/autoLogin`
2. `POST /huajian/userresume/template`
3. `POST /huajian/createUserTemplate/saveDraft`
4. `POST /huajian/lego/legoUserResume`
5. `POST /huajian/upload/file/avatar`
6. `POST /huajian/pdf/getPdf`
7. `POST /huajian/pdf/resumePreview`
8. `GET /huajian/pdf/getPNG`
9. `POST /huajian/legoPdf/getPdf`
10. `POST /huajian/legoPdf/getPNG`

Result:
- PASS (10/10)
- Export content-types verified:
  - PDF: `application/pdf`
  - PNG: `image/png`
  - Preview: `text/plain; charset=utf-8`

## 3) Upload Traversal Security
Case:
- `POST /huajian/upload/file/%2E%2E/%2E%2E/tmp`

Expected:
- HTTP `400`

Result:
- PASS (`400`)

## 4) Owner Constraint Checks
Setup:
- Created second user `other@local` and token.
- Used ids created by default local user.

Checks:
1. `GET /huajian/createUserTemplate/getUsertemplate/{ownerId}` with other token -> body `status=404`
2. `POST /huajian/createUserTemplate/saveDraft` with owner id + other token -> body `status=404`
3. `GET /huajian/lego/legoUserResumeById/{ownerId}` with other token -> body `status=404`
4. `POST /huajian/lego/legoUserResume` with owner id + other token -> body `status=404`

Result:
- PASS (4/4)

## 5) Local-Only Access Guard
Method:
- Simulated non-loopback client (`8.8.8.8`) using ASGI transport.

Check:
- `GET /`

Expected:
- HTTP `403`

Result:
- PASS (`403`, body status `403`)

## Summary
- Total checks: 16
- Passed: 16
- Failed: 0

Status: **All acceptance checks passed for this implementation scope.**

## Final Gate Re-Run
Command set:
1. `python -m py_compile` on all changed modules.
2. Focused smoke: autoLogin + traversal + lego export endpoints.

Result:
- PASS (`FAIL_COUNT 0`)

## 6) Continuation Regression (Contract Compatibility)
Date:
- `2026-02-22` (continued fix pass)

API checks (live service):
1. `GET /huajian/common/template/{id}` returns `template_json` with `props.pageName`.
2. `GET /huajian/common/templateList?page=1&limit=6` returns `page.count/currentPage/pageSize`.
3. `GET /huajian/resume/template/{id}` returns direct editable JSON.
4. `POST /huajian/createUserTemplate/saveDraft` with `templateJson` returns `status=200`.
5. `POST /huajian/userresume/template` with legacy full JSON body returns `status=200`.
6. `POST /huajian/lego/legoUserResume` with `lego_json + previewUrl` returns `status=200`.
7. `GET /huajian/lego/legoUserResumeList?page=1&limit=5` returns paged format.
8. `POST /huajian/legoPdf/getPdf` returns `200` + `application/pdf`.
9. `POST /huajian/legoPdf/getPNG` returns `200` + `image/png`.

Owner checks (manual DB setup + API):
1. `POST /huajian/createUserTemplate/saveDraft` with foreign-owned `id` -> body `status=404`.
2. `POST /huajian/lego/legoUserResume` with foreign-owned `id` -> body `status=404`.

Result:
- PASS (11/11)

## 7) Frontend Route/Flow Validation (Playwright)
Routes and flows:
1. `/` -> click “免费制作专业简历” -> `/resume` (PASS)
2. `/resume` -> click first card “立即免费制作” -> `/resumedetail/:id` (PASS)
3. `/resumedetail/:id` title render + preview render (PASS, no JS error)
4. `/resumedetail/:id` -> click “使用此模版” -> `/designResume/:id` (PASS)
5. `/designResume/:id` click “暂存” -> UI shows `已保存：...` (PASS)
6. `/designer?id=<id>` auto-redirects to `/designResume/<id>?id=<id>` (PASS)
7. `/legoDesigner` opens successfully (PASS)

Console/runtime notes:
- `/resumedetail/:id` and `/designResume/:id` after fixes: no runtime `TypeError`.
- Remaining console warnings are non-blocking framework warnings unrelated to core editing path.

Result:
- PASS (7/7)

## 8) Frontend Runtime Regression Fix (AttendanceDialog)
Date:
- `2026-02-22` (follow-up pass)

Root-cause reproduction evidence:
1. Console log `/Users/xa/Desktop/简历/resume-design/.playwright-cli/console-2026-02-22T10-56-07-414Z.log` contained:
   - `TypeError: Cannot read properties of undefined (reading 'some')`
   - `AttendanceDialog.vue` `getSignStatus`.
2. Backend attendance stub returned `data=[]` (no `calendar` field), causing `attendanceData.value` to become `undefined` in old frontend logic.

Fix verification (Playwright CLI route checks):
1. `GET /` -> Console `0 errors` (warning only).
2. `GET /resumedetail/2001` -> Console `0 errors`.
3. `GET /designResume/2001` -> Console `0 errors` (warnings only).
4. `GET /designer?id=2001` -> Console `0 errors` (warnings only).
5. `GET /legoDesigner` -> `console error` query returned `Errors: 0`.

Additional scan:
- `rg "TypeError|Unhandled error|Cannot read properties"` over latest console logs returned no matches.
- `pnpm exec eslint src/components/AttendanceDialog/AttendanceDialog.vue` passed.

Result:
- PASS (5/5 routes, runtime error cleared)

## 9) Frontend/Backend Adaptation Follow-up
Date:
- `2026-02-22` (continuation)

Compatibility checks:
1. `GET /huajian/integral/getMonthAttendanceList?currentDate=2026-02`
   - Result includes `data.calendar`, `data.luckyText`, `data.currentDate`.
2. Frontend lint for changed adaptation files:
   - `src/App.vue`
   - `src/views/createTemplate/designer/components/ResumeRender.vue`
   - `src/views/LegoDesigner/utils/html2img.ts`
   - Result: PASS.
3. Backend syntax:
   - `python -m py_compile routers/integral.py`
   - Result: PASS.

Flow checks (Playwright):
1. `/designResume/2001`:
   - Save action -> `POST /huajian/createUserTemplate/saveDraft` `200`.
   - Export PDF action -> `POST /huajian/pdf/getPdf` `200`.
   - Console errors: `0`.
2. `/legoDesigner`:
   - Save action -> `POST /huajian/lego/legoUserResume` `200`.
   - Export PDF action -> `POST /huajian/legoPdf/getPdf` `200`.
   - Console errors: `0`.
3. Warning regression:
   - `/` and `/designResume/2001` warning query returned `0` warnings.

Result:
- PASS (frontend/backend adaptation stable for resume editing and lego core flows)

## 10) Personal Project 10-Point Acceptance Mapping (Latest)
Date: `2026-02-22`

1. 前端不必要表述:
- Result: PASS
- Evidence:
  - `src/config/seo.ts` rewritten to local editor wording (removed AI/commercial SEO phrasing).
  - `README.md` rewritten to local personal scope.

2. 前端不必要功能:
- Result: PASS (minimal chain kept, non-core entries removed from active routes and key entry content)
- Evidence:
  - Active router kept only minimal route set.
  - Unused legacy index components removed (`src/views/index/components/*`).
  - Unused payment/membership/comment helper files removed.

3. 后端不必要表述:
- Result: PASS
- Evidence:
  - `main.py` description/startup wording kept local personal semantics.
  - Removed legacy auth router file and related signup/login wording source (`routers/auth.py`).

4. 后端不必要功能:
- Result: PASS
- Evidence:
  - `routers/resume.py` reduced to template read endpoints only.
  - `routers/user_resume.py` admin-list/admin-delete endpoints removed.

5. 前端端点与后端适配:
- Result: PASS
- Evidence:
  - `vue-tsc` PASS, `eslint` PASS.
  - Core API wrappers and backend endpoints align for save/read/export flows.

6. 前端功能与后端适配:
- Result: PASS
- Evidence:
  - No-token core saves succeeded for resume/createTemplate/lego.
  - Export endpoints `legoPdf/getPdf|getPNG` returned 200 with correct content type.

7. 后端 API 与前端适配:
- Result: PASS
- Evidence:
  - Downlined non-core APIs now 404 (`memberships`, `aliPay`, `comment`).
  - Owner checks return 404 on foreign-id updates.

8. 清理不必要文件与代码:
- Result: PASS
- Evidence:
  - Removed runtime artifacts and dead files.
  - Added ignore rules for regenerated local artifacts.

9. 清理不必要注释:
- Result: PASS (targeted files)
- Evidence:
  - Updated touched config/router/backend files to minimal explanatory comments only.

10. 修正不必要表述:
- Result: PASS
- Evidence:
  - Frontend SEO/README/nav context unified to local personal resume editor language.

## Latest Command Evidence
- Frontend:
  - `pnpm exec vue-tsc --noEmit` -> PASS
  - `pnpm exec eslint .` -> PASS
  - `pnpm build:dev` -> PASS
- Backend:
  - `python -m py_compile main.py config.py deps.py routers/*.py models/*.py` -> PASS
  - Smoke:
    - `/huajian/auth/autoLogin` -> 200
    - `/huajian/userresume/template` -> 200
    - `/huajian/createUserTemplate/saveDraft` -> 200
    - `/huajian/lego/legoUserResume` -> 200
    - `/huajian/upload/file/avatar` -> 200
    - `/huajian/legoPdf/getPdf` -> 200 `application/pdf`
    - `/huajian/legoPdf/getPNG` -> 200 `image/png`
    - Owner forged id updates -> 404
    - Downlined APIs -> 404
    - Traversal: `curl --path-as-is /huajian/upload/file/../../tmp` -> 400

## 11) Final Re-validation After Last Cleanup Pass
Date: `2026-02-22`

### A. Contract and Build Checks
1. `pnpm exec vue-tsc --noEmit` -> PASS
2. `pnpm exec eslint .` -> PASS
3. `pnpm build` -> PASS
4. `python3 -m py_compile main.py config.py deps.py routers/*.py models/*.py` -> PASS

### B. API Smoke (with app lifespan)
1. `GET /huajian/auth/autoLogin` -> 200 / body `status=200`
2. `GET /huajian/common/getWebsiteConfig` -> 200 / body keys include `all_free`, `open_comment`, `website_title`
3. `POST /huajian/legoPdf/getPdf` -> 200 / `Content-Type: application/pdf`
4. `POST /huajian/legoPdf/getPNG` -> 200 / `Content-Type: image/png`
5. `GET /huajian/memberships/list` -> 404 (downlined API remains unavailable as expected)
6. Upload traversal attack (encoded path):
   - `POST /huajian/upload/file/%2e%2e/%2e%2e/tmp`
   - Result: 400 / message `非法上传路径`

### C. 10-point Delta Confirmation (this pass)
1. 前端不必要表述: PASS (removed extra AI/legacy wording in touched files).
2. 前端不必要功能: PASS (removed dead custom/smallpig HTTP and dead dictionary files).
3. 后端不必要表述: PASS (`Stub` wording removed from export routers).
4. 后端不必要功能: PASS (no rollback; non-core APIs still downlined).
5. 前端端点与后端适配: PASS (frontend no longer keeps removed websiteConfig write endpoints).
6. 前端功能与后端适配: PASS (core build/type/lint all green).
7. 后端 API 与前端适配: PASS (core smoke endpoints 200, downlined 404).
8. 清理不必要文件与代码: PASS (deleted dead HTTP and dictionary files, runtime artifacts reset).
9. 清理不必要注释: PASS (removed stale AI/dead-comment blocks in touched files).
10. 修正不必要的表述: PASS (router/module wording updated to personal-minimal semantics).

### D. Data/Artifact Reset Confirmation
- `resume-backend/resume.db` -> removed
- `resume-backend/**/__pycache__` -> removed
- `resume-backend/uploads/*` -> only `.gitkeep`

## 12) PDF Export UX Regression Check
Date: `2026-02-22`

### Scope
- Resume designer PDF export interaction.
- DesignerResume PDF export interaction.
- Lego export progress interaction consistency.

### Static Validation
1. `pnpm exec eslint /Users/xa/Desktop/简历/resume-design/src/utils/pdf.ts /Users/xa/Desktop/简历/resume-design/src/views/designer/index.vue /Users/xa/Desktop/简历/resume-design/src/views/designerResume/index.vue /Users/xa/Desktop/简历/resume-design/src/views/LegoDesigner/components/LegoNav.vue /Users/xa/Desktop/简历/resume-design/src/components/ProcessBarDialog/ProcessBarDialog.vue` -> PASS
2. `pnpm exec vue-tsc --noEmit` -> PASS

### Behavior Expectations (implemented)
1. PDF export now uses direct client-side file generation/download; no print popup required.
2. Export progress dialog reaches 100% then auto closes.
3. Export failure shows explicit error message and closes progress dialog.
4. Lego export dialog closes immediately after selecting export type.
5. Preview interface now receives actual `{ blob, pageCount }` from `exportPdfPreview`.

## 13) UI Regression Check (Designer Blank + Overlap)
Date: `2026-02-22`

### Scope
1. `/designer` no-id entry should still show editable default content for local personal usage.
2. `/designResume/:id` right-side tool column should not overlap resume preview.
3. `/resume` template list should remain available.

### Evidence and Results
1. `/designer` runtime stability
- Command: Playwright open + eval + console
- Before: `TypeError: Cannot read properties of null (reading 'status')`, `componentCount=0`
- After:
  - `componentCount=13`
  - console error count `0`
  - Result: PASS

2. `/designResume/6746fe472f0052cb6a9365aa` overlap
- Command: Playwright `eval` bounding-box intersection between `.page-eidtor-box` and `.resume-container`
- Before: `overlapX=30`, `overlapY=300`, `area=9000`
- After: `overlapX=0`, `overlapY=300`, `area=0`
- Result: PASS

3. `/resume` template availability
- Command: Playwright `eval` template card count
- Result: `cardCount=12`, no empty-state display
- Result: PASS

### Artifacts
1. `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-22T15-09-30-421Z.png`
2. `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-22T15-10-12-444Z.png`
3. `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-22T15-07-55-007Z.png`

### Summary
- Both reported UI regressions are fixed and verified.
- Core personal workflow (`模板列表 -> 详情 -> 编辑 -> 导出`) remains available.

## 14) Resume List Overlap Check (`/resume` filter panel)
Date: `2026-02-22`

### Scope
1. Verify filter panel does not overlap template cards while scrolling on `/resume`.

### Evidence and Results
1. Before fix:
- Playwright overlap check (`.category-list-box` vs `.card-box-item`) after `scrollY=420`
- Result: `overlapX=300`, `overlapY=241`, `area=72300`
- Status: FAIL

2. After fix:
- Same check and scroll position
- Result: `overlapX=300`, `overlapY=0`, `area=0`
- Status: PASS

### Static Validation
1. `pnpm exec eslint src/views/resumeList/components/CategoryList.vue` -> PASS
2. `pnpm exec vue-tsc --noEmit` -> PASS

### Artifact
1. `/Users/xa/Desktop/简历/resume-design/.playwright-cli/page-2026-02-22T15-23-55-680Z.png`

## 15) Repository Layout Reorganization Check (`frontend + backend`)
Date: `2026-02-23`

### Scope
1. Validate top-level directory migration to `frontend/` + `backend/`.
2. Validate startup/probe path alignment.
3. Validate frontend/backend basic compile/build checks after migration.

### Structure Result
1. Repo root now contains:
- `/Users/xa/Desktop/简历/resume-design/frontend`
- `/Users/xa/Desktop/简历/resume-design/backend`
- `/Users/xa/Desktop/简历/resume-design/doc`
- `/Users/xa/Desktop/简历/resume-design/scripts`

2. Previous backend path `resume-backend/` is removed from active layout (renamed to `backend/`).

### Verification Commands and Results
1. Frontend install:
- `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm install` -> PASS
- Note: `postinstall` adjusted to run Husky from repo root in new layout.

2. Frontend static/build checks:
- `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec vue-tsc --noEmit` -> PASS
- `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm exec eslint src/views/designer/index.vue src/views/designerResume/index.vue src/views/resumeList/components/CategoryList.vue` -> PASS
- `cd /Users/xa/Desktop/简历/resume-design/frontend && pnpm build:dev` -> PASS

3. Backend syntax check:
- `cd /Users/xa/Desktop/简历/resume-design/backend && python3 -m py_compile main.py config.py deps.py routers/*.py models/*.py` -> PASS

4. Script path check:
- `cd /Users/xa/Desktop/简历/resume-design && bash scripts/local_stack_probe.sh --dry-run` -> PASS
- Verified script now checks `./frontend` and `./backend` by default.

### Conclusion
- Directory structure now matches requested monorepo shape.
- Frontend/backend adaptation is valid under new paths.
- Core resume+lego local editing chain remains buildable and testable.

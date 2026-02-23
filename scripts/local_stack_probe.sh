#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR_DEFAULT="$(cd "${PROJECT_DIR}/backend" 2>/dev/null && pwd || true)"
FRONTEND_DIR_DEFAULT="$(cd "${PROJECT_DIR}/frontend" 2>/dev/null && pwd || true)"

BACKEND_DIR="${BACKEND_DIR_DEFAULT}"
FRONTEND_DIR="${FRONTEND_DIR_DEFAULT}"
BACKEND_URL="http://127.0.0.1:8000"
FRONTEND_URL="http://127.0.0.1:5173"
TIMEOUT=3
DRY_RUN=0
STRICT=0

PASSED=0
WARNED=0

log_info() { printf '[INFO] %s\n' "$*"; }
log_warn() { printf '[WARN] %s\n' "$*"; }
log_error() { printf '[ERROR] %s\n' "$*" >&2; }

die() {
  log_error "$*"
  exit 2
}

on_error() {
  local line="$1"
  local cmd="$2"
  local status="$3"
  log_error "line=${line} status=${status} cmd=${cmd}"
  exit "${status}"
}

trap 'on_error "$LINENO" "$BASH_COMMAND" "$?"' ERR

usage() {
  cat <<'EOF'
Usage:
  local_stack_probe.sh [options]

Options:
  --backend-dir <dir>      Backend project directory (default: ./backend)
  --frontend-dir <dir>     Frontend project directory (default: ./frontend)
  --backend-url <url>      Backend base URL (default: http://127.0.0.1:8000)
  --frontend-url <url>     Frontend base URL (default: http://127.0.0.1:5173)
  --timeout <sec>          curl timeout seconds (default: 3)
  --dry-run                Print checks without sending network requests
  --strict                 Fail when endpoint probe fails
  -h, --help               Show this help
EOF
}

require_cmd() {
  local cmd="$1"
  command -v "${cmd}" >/dev/null 2>&1 || die "missing command: ${cmd}"
}

validate_url() {
  local value="$1"
  [[ "${value}" =~ ^https?://[^[:space:]]+$ ]] || die "invalid url: ${value}"
}

validate_timeout() {
  local value="$1"
  [[ "${value}" =~ ^[0-9]+$ ]] || die "timeout must be integer: ${value}"
  (( value > 0 )) || die "timeout must be > 0: ${value}"
}

check_file() {
  local path="$1"
  [[ -f "${path}" ]] || die "required file not found: ${path}"
  log_info "file exists: ${path}"
  PASSED=$((PASSED + 1))
}

check_dir() {
  local path="$1"
  [[ -d "${path}" ]] || die "required directory not found: ${path}"
  log_info "directory exists: ${path}"
  PASSED=$((PASSED + 1))
}

probe_endpoint() {
  local name="$1"
  local url="$2"
  if (( DRY_RUN )); then
    log_info "DRY-RUN probe: ${name} -> ${url}"
    PASSED=$((PASSED + 1))
    return 0
  fi

  if curl --silent --show-error --fail --max-time "${TIMEOUT}" "${url}" >/dev/null; then
    log_info "probe ok: ${name} -> ${url}"
    PASSED=$((PASSED + 1))
    return 0
  fi

  log_warn "probe failed: ${name} -> ${url}"
  WARNED=$((WARNED + 1))
  if (( STRICT )); then
    die "strict mode enabled and probe failed: ${name}"
  fi
  return 1
}

while (($#)); do
  case "$1" in
    --backend-dir)
      [[ $# -ge 2 ]] || die "missing value for --backend-dir"
      BACKEND_DIR="$2"
      shift 2
      ;;
    --frontend-dir)
      [[ $# -ge 2 ]] || die "missing value for --frontend-dir"
      FRONTEND_DIR="$2"
      shift 2
      ;;
    --backend-url)
      [[ $# -ge 2 ]] || die "missing value for --backend-url"
      BACKEND_URL="$2"
      shift 2
      ;;
    --frontend-url)
      [[ $# -ge 2 ]] || die "missing value for --frontend-url"
      FRONTEND_URL="$2"
      shift 2
      ;;
    --timeout)
      [[ $# -ge 2 ]] || die "missing value for --timeout"
      TIMEOUT="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --strict)
      STRICT=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown argument: $1"
      ;;
  esac
done

validate_url "${BACKEND_URL}"
validate_url "${FRONTEND_URL}"
validate_timeout "${TIMEOUT}"

require_cmd curl
require_cmd pnpm
require_cmd python3

check_dir "${PROJECT_DIR}"
[[ -n "${FRONTEND_DIR}" ]] || die "frontend directory is empty, set --frontend-dir explicitly"
check_dir "${FRONTEND_DIR}"
check_file "${FRONTEND_DIR}/package.json"
check_file "${FRONTEND_DIR}/pnpm-lock.yaml"

[[ -n "${BACKEND_DIR}" ]] || die "backend directory is empty, set --backend-dir explicitly"
check_dir "${BACKEND_DIR}"
check_file "${BACKEND_DIR}/main.py"

probe_endpoint "frontend-home" "${FRONTEND_URL}"
probe_endpoint "backend-autologin" "${BACKEND_URL}/huajian/auth/autoLogin"

log_info "summary: passed=${PASSED} warned=${WARNED} dry_run=${DRY_RUN} strict=${STRICT}"
if (( WARNED > 0 )); then
  log_warn "completed with warnings"
else
  log_info "all checks passed"
fi

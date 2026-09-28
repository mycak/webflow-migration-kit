#!/usr/bin/env bash
# Setup script for the Claude Code cloud environment (claude.ai/code → environment → Setup script).
# Runs once per environment and gets cached (~5 min limit). Needs network access level Full (or Custom, see README).
# Deliberately no `set -e`: a failed optional step must not abort the whole setup (and the session start).
# Pair it with the environment variable PLAYWRIGHT_CHROMIUM_EXECUTABLE=/opt/pw-browsers/chromium (see README).

log() { echo "[cloud-setup] $*"; }

# 1. Python deps for scripts/audit.py, assets.py, qa.py
python3 -m pip install --quiet --break-system-packages "playwright>=1.45" "pillow>=10.0" "requests>=2.31" 2>/dev/null \
  || python3 -m pip install --quiet "playwright>=1.45" "pillow>=10.0" "requests>=2.31" \
  || log "WARN: pip install failed"

# 2. Chromium for the Python scripts (skipped when a preinstalled browser is available)
CHROMIUM="${PLAYWRIGHT_CHROMIUM_EXECUTABLE:-/opt/pw-browsers/chromium}"
if [ -x "$CHROMIUM" ]; then
  log "using preinstalled Chromium: $CHROMIUM"
else
  python3 -m playwright install --with-deps chromium 2>/dev/null \
    || python3 -m playwright install chromium \
    || log "WARN: python playwright install failed"
fi

# 3. Playwright MCP server (npx @playwright/mcp): warm the npx cache and install a browser build
#    matching the MCP's own Playwright version (used when PLAYWRIGHT_CHROMIUM_EXECUTABLE is not set
#    or points to a missing file).
npx -y @playwright/mcp@latest --version >/dev/null 2>&1 || log "WARN: could not warm @playwright/mcp"
npx -y playwright@latest install chromium >/dev/null 2>&1 || log "WARN: playwright (npx) chromium install failed"
npx -y playwright@latest install-deps chromium >/dev/null 2>&1 || true

log "migration kit environment ready"
exit 0

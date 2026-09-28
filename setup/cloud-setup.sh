#!/usr/bin/env bash
# Setup script for the Claude Code cloud environment (claude.ai/code → environment → Setup script).
# Runs once per environment and gets cached (~5 min limit). Needs network access level Full (or Custom, see README).
set -euo pipefail
python3 -m pip install --quiet --break-system-packages "playwright>=1.45" "pillow>=10.0" "requests>=2.31" || \
python3 -m pip install --quiet "playwright>=1.45" "pillow>=10.0" "requests>=2.31"
# Chromium for Python scripts and for the Playwright MCP server (npx @playwright/mcp)
python3 -m playwright install --with-deps chromium || python3 -m playwright install chromium
npx -y @playwright/mcp@latest --version >/dev/null 2>&1 || true   # warm the npx cache
npx -y playwright@latest install chromium >/dev/null 2>&1 || true  # browser build matching the MCP server
echo "migration kit environment ready"

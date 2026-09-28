#!/usr/bin/env bash
# Starts the Playwright MCP server (headless) with the session's egress proxy, if any.
set -euo pipefail
ARGS=(--headless --isolated --browser chromium --ignore-https-errors --output-dir "${CLAUDE_PROJECT_DIR:-.}/migrations/.playwright")
PROXY="${HTTPS_PROXY:-${https_proxy:-${HTTP_PROXY:-}}}"
if [[ -n "$PROXY" ]]; then
  ARGS+=(--proxy-server "$PROXY" --proxy-bypass "localhost,127.0.0.1")
fi
if [[ -n "${PLAYWRIGHT_CHROMIUM_EXECUTABLE:-}" ]]; then
  ARGS+=(--executable-path "$PLAYWRIGHT_CHROMIUM_EXECUTABLE")
fi
exec npx -y @playwright/mcp@latest "${ARGS[@]}"

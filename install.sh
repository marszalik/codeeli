#!/usr/bin/env bash
#
# Codeeli installer for Linux and macOS.
#
# Clones the repo, creates a virtualenv, installs dependencies.
# Does not start the server — the last step prints how to do that.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/marszalik/codeeli/main/install.sh | bash
#
# Override target directory:
#   CODEELI_DIR=~/code/codeeli curl -fsSL .../install.sh | bash

set -euo pipefail

REPO_URL="${CODEELI_REPO:-https://github.com/marszalik/codeeli.git}"
TARGET="${CODEELI_DIR:-$HOME/codeeli}"

c_red=$'\033[31m'; c_green=$'\033[32m'; c_cyan=$'\033[36m'; c_off=$'\033[0m'

err()  { printf '%serror:%s %s\n' "$c_red" "$c_off" "$*" >&2; exit 1; }
info() { printf '%s›%s %s\n' "$c_cyan" "$c_off" "$*"; }
ok()   { printf '%s✓%s %s\n' "$c_green" "$c_off" "$*"; }

# --- dependency checks --------------------------------------------------------

command -v git     >/dev/null 2>&1 || err "git is required"
command -v python3 >/dev/null 2>&1 || err "python3 is required (>= 3.10)"

py_check=$(python3 - <<'PY'
import sys
print("ok" if sys.version_info >= (3, 10) else f"{sys.version_info[0]}.{sys.version_info[1]}")
PY
)
if [ "$py_check" != "ok" ]; then
  err "python 3.10+ required (found $py_check)"
fi

# --- clone or update ----------------------------------------------------------

if [ -d "$TARGET/.git" ]; then
  info "Updating existing checkout at $TARGET"
  git -C "$TARGET" pull --ff-only
elif [ -e "$TARGET" ]; then
  err "$TARGET exists and is not a git checkout — refusing to overwrite"
else
  info "Cloning into $TARGET"
  git clone --depth 1 "$REPO_URL" "$TARGET"
fi

# --- venv + dependencies ------------------------------------------------------

if [ ! -d "$TARGET/.venv" ]; then
  info "Creating virtualenv"
  python3 -m venv "$TARGET/.venv"
fi

info "Installing dependencies"
"$TARGET/.venv/bin/pip" install --upgrade --quiet pip
"$TARGET/.venv/bin/pip" install --quiet -r "$TARGET/requirements.txt"

# --- done ---------------------------------------------------------------------

ok "Codeeli installed at $TARGET"
cat <<EOF

Start the dev server:
  cd $TARGET
  .venv/bin/python scripts/dev.py

It will pick the first free port starting at 8000 and print the URL.

You also need a local model available, for example:
  - Ollama:     https://ollama.com  (then 'ollama pull qwen2.5-coder:7b')
  - llama.cpp:  any OpenAI-compatible server (LM Studio, vLLM, llama-server)

Configure your model in the AI tab inside the app.
EOF

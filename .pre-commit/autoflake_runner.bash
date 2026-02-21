#! /usr/bin/bash

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

autoflake ./locstat --check --ignore-init-module-imports --recursive
autoflake ./tests --check --ignore-init-module-imports --recursive

#! /usr/bin/bash

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

if [ ! command -v pytest > /dev/null ]; then
    echo "pytest could not be resolved"
    exit 1
fi

if [ ! -d "tests" ]; then
    echo "No 'tests' directory found at TLD for pytest to run against"
    exit 1
fi

files=$(git diff --cached --name-only -z --diff-filter=ACM -- '*.py')

if [ -z "$files" ]; then
    exit 0
fi

pytest -vv --tb=short

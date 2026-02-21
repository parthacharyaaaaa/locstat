#! /usr/bin/bash

set -euo pipefail

files=$(git diff --cached --name-only -z --diff-filter=ACM -- '*.py')

if [ -z "$files" ]; then
    exit 0
fi

autoflake --check --remove-all-unused-imports --ignore-init-modules-imports --verbose

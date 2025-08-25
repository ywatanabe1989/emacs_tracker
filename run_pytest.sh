#!/bin/bash
# Test runner script for emacs-tracker project

set -e

echo "=============================================="
echo "Running emacs-tracker tests with pytest"
echo "=============================================="

# Run all tests in the tests directory
python -m pytest tests/ -v --tb=short

echo ""
echo "=============================================="
echo "Tests completed"
echo "=============================================="
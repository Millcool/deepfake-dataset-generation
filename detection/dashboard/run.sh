#!/bin/bash
# Запуск dashboard локально.
# Использование: bash detection/dashboard/run.sh
# Dashboard: http://localhost:5050

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VENV_DIR="$PROJECT_ROOT/detection/dashboard/.venv"

# Создать venv если нет
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --upgrade pip -q
    "$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" -q
    echo "Dependencies installed."
fi

echo "Starting dashboard on http://localhost:5050"
echo "Press Ctrl+C to stop."

cd "$SCRIPT_DIR"
"$VENV_DIR/bin/python" app.py

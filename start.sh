#!/bin/bash

VENV_DIR="kahoot-joiner"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

echo "Installing necessary libraries..."
pip install flask requests py_mini_racer websocket-client uuid

echo "Starting Flask application..."
export FLASK_APP=app.py
export FLASK_ENV=development
xdg-open http://127.0.0.1:5000 & clear && flask run

read -p "Press Enter to continue..."

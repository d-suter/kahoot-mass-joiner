VENV_DIR="kahoot-joiner"

python3 -m venv "$VENV_DIR"

$VENV_DIR/bin/activate

pip install flask requests py_mini_racer websocket-client uuid

export FLASK_APP=app.py
export FLASK_ENV=development
flask run

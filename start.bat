@echo off
SET "VENV_DIR=kahoot-joiner"

IF NOT EXIST "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%
)

echo Activating virtual environment...
CALL %VENV_DIR%\Scripts\activate

echo Installing necessary libraries...
pip install flask requests py_mini_racer websocket-client uuid threading json logging random time base64 re websocket

echo Starting Flask application...
set FLASK_APP=app.py
set FLASK_ENV=development
start http://127.0.0.1:5000 & cls & flask run

pause

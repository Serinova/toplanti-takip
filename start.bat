@echo off
cd "C:\Users\yusuf\toplanti-takip-flask"
call venv\Scripts\activate.bat
set FLASK_APP=run.py
set FLASK_ENV=development
unicorn run --host=0.0.0.0 --port=5000

@echo off
set PYTHONPATH=%~dp0;%~dp0.venv\Lib\site-packages
"C:\Users\fence\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

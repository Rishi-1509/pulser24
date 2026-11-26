$py = "C:\Users\fence\AppData\Roaming\uv\python\cpython-3.11-windows-x86_64-none\python.exe"
$env:PYTHONPATH = "$PSScriptRoot;$PSScriptRoot\.venv\Lib\site-packages"
& $py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

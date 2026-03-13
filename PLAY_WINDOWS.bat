@echo off
title Tung Tung Sahur Run - Launcher
cd /d "%~dp0"
echo ============================================
echo   TUNG TUNG SAHUR RUN - Launcher
echo ============================================
echo.

set RUNTIME_DIR=%~dp0python_runtime
set PYTHON=%RUNTIME_DIR%\python.exe

:: Download embedded Python 3.12 if not already present
if not exist "%PYTHON%" (
    echo [SETUP] First-time setup: downloading Python 3.12...
    echo         This only happens once!
    echo.

    set PY_ZIP=%TEMP%\python312_embed.zip
    set PY_URL=https://www.python.org/ftp/python/3.12.9/python-3.12.9-embed-amd64.zip

    powershell -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_ZIP%' -UseBasicParsing"
    if errorlevel 1 (
        echo [ERROR] Failed to download Python. Check your internet connection.
        pause
        exit /b 1
    )

    echo [SETUP] Extracting Python...
    powershell -Command "Expand-Archive -Path '%PY_ZIP%' -DestinationPath '%RUNTIME_DIR%' -Force"
    del "%PY_ZIP%"

    :: Uncomment "import site" in the ._pth file so pip packages are importable
    powershell -Command "(Get-Content '%RUNTIME_DIR%\python312._pth') -replace '#import site','import site' | Set-Content '%RUNTIME_DIR%\python312._pth'"

    echo [SETUP] Installing pip...
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%RUNTIME_DIR%\get-pip.py' -UseBasicParsing"
    "%PYTHON%" "%RUNTIME_DIR%\get-pip.py" --quiet
    del "%RUNTIME_DIR%\get-pip.py"

    echo [SETUP] Installing game dependencies...
    "%PYTHON%" -m pip install customtkinter "pygame==2.5.2" --prefer-binary --quiet

    echo [OK] Setup complete!
    echo.
) else (
    echo [OK] Python 3.12 runtime found.
    echo.
)

echo Launching game...
"%PYTHON%" tung_online.py
pause

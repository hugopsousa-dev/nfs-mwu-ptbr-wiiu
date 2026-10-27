@echo off
cd /d "%~dp0"
py -3 -c "import sys, tkinter; assert sys.version_info >= (3,10)" >nul 2>&1
if errorlevel 1 (
  echo Instale Python 3.10+ com Tcl/Tk e Python Launcher em python.org.
  echo Veja COMO_INSTALAR.md para o modo de terminal.
  pause
  exit /b 1
)
py -3 instalar.py
if errorlevel 1 pause

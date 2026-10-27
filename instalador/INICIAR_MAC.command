#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
for py in /Library/Frameworks/Python.framework/Versions/Current/bin/python3 /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 python3; do
  if command -v "$py" >/dev/null 2>&1 && "$py" -c 'import sys, tkinter; assert sys.version_info >= (3,10)' >/dev/null 2>&1; then
    "$py" instalar.py
    exit $?
  fi
done
printf '%s\n' 'Instale Python 3.10+ com Tcl/Tk pelo python.org para usar as janelas.' 'O modo de terminal está em COMO_INSTALAR.md.'
read -r -p 'Pressione Enter para fechar.'
exit 1

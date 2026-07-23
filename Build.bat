@echo off

echo Clear

del /Q dist\ 2>nul

echo Build

nuitka --onefile --jobs=12 --lto=no --include-package=src --output-dir=dist src/main.py --python-for-scons=python

echo Done

pause
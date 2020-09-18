@echo off
title Python program compiler
pyinstaller --clean --onefile --distpath . --add-data *.ttf;. --add-data *.png;. main.pyw
pause
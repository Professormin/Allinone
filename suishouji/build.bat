@echo off
chcp 65001 >nul
rem 打包成单文件 exe：dist\Suiji.exe
cd /d "%~dp0"
python -m pip install -U pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name Suiji suiji.py
echo.
echo 完成：dist\Suiji.exe
pause

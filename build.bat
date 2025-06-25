@echo off
echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller pillow pywin32-ctypes

echo Creating icon...
python create_icon.py

echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "installer" rmdir /s /q installer
if exist "*.spec" del /f /q *.spec

REM Clean previous dist/Password Manager folder for fresh build
if exist "dist\Password Manager" rmdir /s /q "dist\Password Manager"

REM Reminder to rebuild after code changes
REM Run this script after making any code changes to update the EXE

echo Creating version info...
echo VSVersionInfo( > version_info.txt
echo     ffi=FixedFileInfo( >> version_info.txt
echo         filevers=(1, 0, 0, 0), >> version_info.txt
echo         prodvers=(1, 0, 0, 0), >> version_info.txt
echo         mask=0x3f, >> version_info.txt
echo         flags=0x0, >> version_info.txt
echo         OS=0x40004, >> version_info.txt
echo         fileType=0x1, >> version_info.txt
echo         subtype=0x0, >> version_info.txt
echo         date=(0, 0) >> version_info.txt
echo     ), >> version_info.txt
echo     kids=[ >> version_info.txt
echo         StringFileInfo( >> version_info.txt
echo             [ >> version_info.txt
echo                 StringTable( >> version_info.txt
echo                     u'040904B0', >> version_info.txt
echo                     [StringStruct(u'CompanyName', u'Bhupender (Mrone)'), >> version_info.txt
echo                     StringStruct(u'FileDescription', u'Secure Password Manager'), >> version_info.txt
echo                     StringStruct(u'FileVersion', u'1.0.0.0'), >> version_info.txt
echo                     StringStruct(u'InternalName', u'SecurePasswordManager'), >> version_info.txt
echo                     StringStruct(u'LegalCopyright', u'Copyright (c) 2024 Bhupender (Mrone)'), >> version_info.txt
echo                     StringStruct(u'OriginalFilename', u'Password Manager.exe'), >> version_info.txt
echo                     StringStruct(u'ProductName', u'Secure Password Manager'), >> version_info.txt
echo                     StringStruct(u'ProductVersion', u'1.0.0.0')] >> version_info.txt
echo                 ) >> version_info.txt
echo             ] >> version_info.txt
echo         ), >> version_info.txt
echo         VarFileInfo([VarStruct(u'Translation', [1033, 1200])]) >> version_info.txt
echo     ] >> version_info.txt
echo ) >> version_info.txt

echo Building executable...
pyinstaller --clean ^
    --onedir ^
    --noconsole ^
    --icon=icon.ico ^
    --manifest password_manager.manifest ^
    --add-data "theme.py;." ^
    --add-data "utils.py;." ^
    --version-file version_info.txt ^
    password_manager_gui.py

echo Optimizing executable...
if exist "dist\Password Manager" (
    cd "dist\Password Manager"
    if exist "*.pyc" del /s /q "*.pyc"
    if exist "*.pyo" del /s /q "*.pyo"
    if exist "*.pyd" del /s /q "*.pyd"
    cd ..\..
)

mkdir installer 2>nul

echo Creating installer...
set "ISCC_FOUND="

:: Try Program Files (x86) first
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    set "ISCC_FOUND=1"
    goto RunInnoSetup
)

:: Try Program Files next
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe"
    set "ISCC_FOUND=1"
    goto RunInnoSetup
)

if not defined ISCC_FOUND (
    echo ERROR: Inno Setup not found!
    echo Please install Inno Setup 6 from https://jrsoftware.org/isdl.php
    echo Expected paths:
    echo - C:\Program Files (x86)\Inno Setup 6\ISCC.exe
    echo - C:\Program Files\Inno Setup 6\ISCC.exe
    pause
    exit /b 1
)

:RunInnoSetup
echo Found Inno Setup at: %ISCC_PATH%
call "%ISCC_PATH%" "installer.iss"
if errorlevel 1 (
    echo Error running Inno Setup compiler
    pause
    exit /b 1
)

echo Cleaning up temporary files...
if exist "build" rmdir /s /q build
if exist "Password Manager.spec" del /f /q "Password Manager.spec"
if exist "version_info.txt" del /f /q "version_info.txt"

echo Done! The installer is in the installer folder.
echo Note: The installer will create a desktop shortcut if requested and install to Program Files.
pause 
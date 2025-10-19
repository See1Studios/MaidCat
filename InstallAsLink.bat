@echo off
REM This batch file runs the CreatePluginLink.ps1 PowerShell script.
REM The PowerShell script will handle asking for Administrator privileges.

SET "SCRIPT_DIR=%~dp0"
powershell.exe -ExecutionPolicy Bypass -File "%SCRIPT_DIR%CreatePluginLink.ps1"

echo.
echo Script execution finished.
pause
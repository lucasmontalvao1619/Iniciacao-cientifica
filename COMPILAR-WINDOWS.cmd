@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0packaging\build-windows.ps1"
set "PLANEJADOR_BUILD_RESULT=%ERRORLEVEL%"
if not "%PLANEJADOR_BUILD_RESULT%"=="0" echo A compilacao falhou. Copie a mensagem exibida acima.
pause
exit /b %PLANEJADOR_BUILD_RESULT%

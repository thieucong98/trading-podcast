@echo off
rem Wrapper to invoke agy CLI through WSL from Windows Command Prompt or PowerShell
wsl.exe -d Ubuntu -e bash -c "export PATH=\"$HOME/.local/bin:$PATH\"; agy %*"

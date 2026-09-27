<#
.SYNOPSIS
    Antigravity CLI wrapper for Windows PowerShell
.DESCRIPTION
    Runs the agy CLI tool inside WSL Ubuntu seamlessly from Windows.
#>
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CommandArgs
)

$joinedArgs = ($CommandArgs -join " ")
wsl.exe -d Ubuntu -e bash -c "export PATH=`"`$HOME/.local/bin:`$PATH`"; agy $joinedArgs"

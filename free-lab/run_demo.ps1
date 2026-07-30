$ErrorActionPreference = "Stop"
python (Join-Path $PSScriptRoot "run_demo.py")
exit $LASTEXITCODE

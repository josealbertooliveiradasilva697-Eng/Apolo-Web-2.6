param(
    [ValidateSet('operador','admin','desenvolvedor')]
    [string]$Perfil = 'operador',
    [string]$Python = ''
)
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if (-not $Python) {
        $projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
        $sessionPython = Join-Path $PSScriptRoot '..\..\work\venv\Scripts\python.exe'
        if (Test-Path -LiteralPath $projectPython) { $Python = $projectPython }
        elseif (Test-Path -LiteralPath $sessionPython) { $Python = $sessionPython }
        else { $Python = 'python' }
    }
    $env:APOLO_AUTH_MODE = 'local'
    $env:APOLO_LOCAL_ROLE = $Perfil
    & $Python -m streamlit run app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
} finally {
    Pop-Location
}

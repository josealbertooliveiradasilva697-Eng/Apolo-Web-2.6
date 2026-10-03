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
        if (Test-Path -LiteralPath $projectPython) { $Python = $projectPython }
        else { $Python = 'python' }
    }
    $env:APOLO_AUTH_MODE = 'local'
    $env:APOLO_REPOSITORY_MODE = 'sqlite'
    $env:APOLO_ENV = 'development'
    $env:APOLO_LOCAL_ROLE = $Perfil
    & $Python -m streamlit run app.py --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
    if ($LASTEXITCODE -ne 0) { throw 'Streamlit encerrou com erro. Confira o Python e requirements.txt.' }
} finally {
    Pop-Location
}

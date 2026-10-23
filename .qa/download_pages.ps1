param([string]$Manifest = '.qa/page-downloads.json')
$ErrorActionPreference = 'Stop'
$items = Get-Content $Manifest -Raw -Encoding UTF8 | ConvertFrom-Json
$count = 0
foreach ($item in $items) {
    if (Test-Path -LiteralPath $item.target) { continue }
    New-Item -ItemType Directory -Force -Path (Split-Path $item.target) | Out-Null
    try {
        Invoke-WebRequest -Uri $item.url -OutFile $item.target
        $count++
    } catch {
        Write-Output ('FAILED ' + $item.url + ' ' + $_.Exception.Message)
    }
}
Write-Output ('Downloaded ' + $count + ' assets.')

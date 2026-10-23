$ErrorActionPreference = 'Stop'
$archive = Get-Content '.qa/pages/collections.json' -Raw -Encoding UTF8 | ConvertFrom-Json
$collection = $archive.'/api/public/press-releases'
$all = @($collection.data.data)
$total = [int]$collection.data.pagination.total
$pages = [math]::Ceiling($total / 100)
for ($page = 2; $page -le $pages; $page++) {
    $url = 'https://prd-new-api.corp.musinsa.com/api/public/press-releases?lang=ko&page=' + $page + '&limit=100'
    $response = Invoke-RestMethod -Uri $url
    $all += @($response.data.data)
}
$collection.data.data = $all
$collection.data.pagination.page = 1
$collection.data.pagination.limit = $all.Count
$collection.data.pagination.totalPages = 1
$json = $archive | ConvertTo-Json -Depth 100 -Compress
[IO.File]::WriteAllText((Join-Path (Get-Location) '.qa/pages/collections.json'), $json, [Text.UTF8Encoding]::new($false))
Write-Output ('Cached ' + $all.Count + ' press releases for search and pagination.')

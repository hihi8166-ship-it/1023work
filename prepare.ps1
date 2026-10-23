$ErrorActionPreference = 'Stop'
$base = 'https://corp.musinsa.com'
$html = Get-Content reference.html -Raw -Encoding UTF8
$paths = [regex]::Matches($html, '(?:src|href)="(/images/[^"]+|/_next/static/chunks/[^" ]+\.css)"') | ForEach-Object {$_.Groups[1].Value} | Sort-Object -Unique
foreach ($path in $paths) {
  $target = Join-Path (Get-Location) ('assets' + $path)
  New-Item -ItemType Directory -Force -Path (Split-Path $target) | Out-Null
  Invoke-WebRequest -Uri ($base + $path) -OutFile $target
  $html = $html.Replace($path, ('assets' + $path))
}
$html = [regex]::Replace($html, '<script\b[^>]*>[\s\S]*?</script>', '')
$html = [regex]::Replace($html, '<link[^>]+as="script"[^>]*>', '')
$html = [regex]::Replace($html, '<link[^>]+rel="icon"[^>]*>', '')
$html = [regex]::Replace($html, '<meta[^>]+(?:property="og:[^"]+"|name="twitter:[^"]+")[^>]*>', '')
$html = $html.Replace('무신사','무신사카피').Replace('MUSINSA','MUSINSACOPY')
$html = [regex]::Replace($html, '<img[^>]+src="assets/images/common/(?:musinsa_logo_b|footer_logo)\.svg"[^>]*>', '<span class="copy-logo">MUSINSACOPY</span>')
$html = [regex]::Replace($html, '(<a href="/ko">)<svg[\s\S]*?</svg>', '$1<span class="copy-logo">MUSINSACOPY</span>')
$html = $html.Replace('href="/ko"', 'href="#"').Replace('href="/company"', 'href="#company"').Replace('href="/business"', 'href="#business"').Replace('href="/impact"', 'href="#impact"').Replace('href="/newsroom/press"', 'href="#newsroom"')
$html = $html.Replace('</head>', '<link rel="stylesheet" href="css/style.css"/></head>')
$html = $html.Replace('</body>', '<script src="js/main.js"></script></body>')
[IO.File]::WriteAllText((Join-Path (Get-Location) 'index.html'), $html, [Text.UTF8Encoding]::new($false))
Write-Output ('Saved homepage and ' + $paths.Count + ' local assets.')

# Safe upgrade: updates V3 layout/build/CMS without overwriting existing CMS content or uploads.
$ErrorActionPreference = 'Stop'
$owner = 'Harshad8623'
$repoName = 'Harshad8623.github.io'
$repo = "$owner/$repoName"
$source = $PSScriptRoot

function Need($command) {
  if (-not (Get-Command $command -ErrorAction SilentlyContinue)) {
    throw "Missing $command. See README.md for installation steps."
  }
}
Need git
Need gh
$who = (& gh api user --jq .login).Trim()
if ($LASTEXITCODE -ne 0 -or $who -ine $owner) {throw "Log in to the correct account first. Expected $owner, got $who."}
& gh repo view $repo --json name > $null
if ($LASTEXITCODE -ne 0) {throw "Portfolio repository $repo does not exist. Use PUBLISH_WINDOWS.bat instead."}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupDir = Join-Path ([Environment]::GetFolderPath('MyDocuments')) "HarshadPortfolioBackups\$stamp"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
$mirror = Join-Path $backupDir 'full-git-history.git'
$working = Join-Path $backupDir 'working-copy'
Write-Host "Creating full Git-history backup in $backupDir" -ForegroundColor Cyan
& git clone --mirror "https://github.com/$repo.git" "$mirror"
if ($LASTEXITCODE -ne 0) {throw 'Backup could not be completed. Nothing was changed.'}
& git clone "https://github.com/$repo.git" "$working"
if ($LASTEXITCODE -ne 0) {throw 'Cannot clone portfolio repository. Nothing was changed.'}

$updatePaths = @(
  'index.html', '.pages.yml', '.nojekyll', '.gitignore',
  'assets/styles.css', 'assets/site.js', 'assets/v3.css', 'assets/favicon.svg',
  '.github/workflows/pages.yml',
  'scripts/build.py', 'scripts/test_build.py', 'scripts/import_from_v2.py',
  'README.md', 'DEPLOYMENT.md', 'V3_CHANGELOG.md'
)
foreach ($rel in $updatePaths) {
  $srcFile = Join-Path $source $rel
  if (-not (Test-Path -LiteralPath $srcFile -PathType Leaf)) {throw "Missing release file: $rel"}
  $destFile = Join-Path $working $rel
  $destParent = Split-Path $destFile -Parent
  New-Item -ItemType Directory -Path $destParent -Force | Out-Null
  Copy-Item -LiteralPath $srcFile -Destination $destFile -Force
}

# Add the new default image assets only if the site owner has not already replaced them.
foreach ($rel in @('assets/college-logo.png','assets/uploads/images/profile-portrait.webp','assets/uploads/images/csmss-college-logo.png')) {
  $dst = Join-Path $working $rel
  if (-not (Test-Path -LiteralPath $dst)) {
    New-Item -ItemType Directory -Path (Split-Path $dst -Parent) -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $source $rel) -Destination $dst
  }
}

# Keep all existing CMS edits and media intact. Only seed content on first-time conversion.
if (-not (Test-Path (Join-Path $working 'content/site.json'))) {
  Copy-Item -Path (Join-Path $source 'content') -Destination $working -Recurse -Force
  Write-Host 'Initialized CMS content because the existing repository had none.' -ForegroundColor Yellow
} else {
  Write-Host 'Existing content/site.json and project entries preserved.' -ForegroundColor Green
}

# Empty CMS collections are otherwise lost by Git (Git does not track empty directories).
# Create marker files without replacing any existing resume/certificate JSON data.
foreach ($collection in @('projects', 'certificates', 'resumes')) {
  $folder = Join-Path $working "content/$collection"
  New-Item -ItemType Directory -Path $folder -Force | Out-Null
  $marker = Join-Path $folder '.gitkeep'
  if (-not (Test-Path -LiteralPath $marker)) {
    Set-Content -LiteralPath $marker -Value '' -NoNewline -Encoding UTF8
  }
}
foreach ($mediaFolder in @('assets/uploads', 'assets/uploads/images', 'assets/uploads/documents')) {
  $folder = Join-Path $working $mediaFolder
  New-Item -ItemType Directory -Path $folder -Force | Out-Null
  $marker = Join-Path $folder '.gitkeep'
  if (-not (Test-Path -LiteralPath $marker)) {
    Set-Content -LiteralPath $marker -Value '' -NoNewline -Encoding UTF8
  }
}
Write-Host 'Existing CMS content and uploaded files preserved; missing collection directories initialized.' -ForegroundColor Green

$python = Get-Command py -ErrorAction SilentlyContinue
Push-Location $working
try {
  if ($python) {
    & py -3 scripts/test_build.py
    if ($LASTEXITCODE -ne 0) {throw 'Build tests failed. Nothing was pushed.'}
    & py -3 scripts/build.py
  } else {
    Need python
    & python scripts/test_build.py
    if ($LASTEXITCODE -ne 0) {throw 'Build tests failed. Nothing was pushed.'}
    & python scripts/build.py
  }
  if ($LASTEXITCODE -ne 0) {throw 'Static website build failed. Nothing was pushed.'}
  $diff = & git status --short
  if (-not $diff) {Write-Host 'Already up to date. No commit was needed.' -ForegroundColor Green; exit 0}
  Write-Host "`nFiles to update:" -ForegroundColor Cyan
  $diff | ForEach-Object {Write-Host "  $_"}
  Write-Host "`nConfirm that no content files or uploaded documents are being removed." -ForegroundColor Yellow
  $confirmation = Read-Host 'Type UPDATE to commit and push'
  if ($confirmation -cne 'UPDATE') {Write-Host 'Cancelled; no remote changes.';exit 0}
  & git add -A
  if ($LASTEXITCODE -ne 0) {throw 'Could not stage changes.'}
  & git commit -m 'Upgrade portfolio design, CMS, accessibility and build safeguards'
  if ($LASTEXITCODE -ne 0) {throw 'Git commit failed. No remote changes.'}
  & git push origin HEAD
  if ($LASTEXITCODE -ne 0) {throw "Push failed. Your backup and working copy remain at $backupDir."}
  Write-Host "`nUpdate pushed. Verify your Actions tab and https://harshad8623.github.io/" -ForegroundColor Green
  Write-Host "Backup: $backupDir"
} finally {Pop-Location}

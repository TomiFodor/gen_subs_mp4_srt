# Activate venv first, then run this
Get-ChildItem -Filter *.mkv -Recurse | ForEach-Object {
    $srtPath = $_.FullName -replace '\.[^.]+$', '.*.srt'
    if (-not (Test-Path $srtPath)) {
        Write-Host "Processing: $($_.Name)"
        python generate_subs.py $_.FullName
    } else {
        Write-Host "Skipping: $($_.Name) (subtitle exists)"
    }
}

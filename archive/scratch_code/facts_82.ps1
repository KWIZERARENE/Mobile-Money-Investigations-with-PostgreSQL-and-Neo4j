$R = "C:\assignement\results"
$o = "$R\facts_82.txt"
"=== head of collect_82.txt ===" | Out-File $o
Get-Content "$R\collect_82.txt" -TotalCount 40 | Out-File $o -Append
foreach ($f in (Get-ChildItem $R -File | Where-Object { $_.Name -like "pg_*" -or $_.Name -like "import_log*" })) {
  "`n=== $($f.Name) ===" | Out-File $o -Append
  Get-Content $f.FullName -Tail 40 | Out-File $o -Append
}
"`n=== Neo4j database folders ===" | Out-File $o -Append
$dirs = Get-ChildItem "$env:USERPROFILE\.Neo4jDesktop*","$env:USERPROFILE\AppData\Local\Neo4j*","$env:USERPROFILE\AppData\Roaming\Neo4j*","C:\neo4j*" -Recurse -Directory -Filter neo4j -ErrorAction SilentlyContinue | Where-Object { $_.Parent.Name -eq "databases" }
foreach ($d in $dirs) {
  $sz = (Get-ChildItem $d.FullName -Recurse -File | Measure-Object Length -Sum).Sum
  $tx = Join-Path (Split-Path $d.Parent.FullName) "transactions\neo4j"
  $tsz = if (Test-Path $tx) { (Get-ChildItem $tx -Recurse -File | Measure-Object Length -Sum).Sum } else { "n/a" }
  "$($d.FullName)  store_bytes=$sz  txlog_bytes=$tsz  last_write=$($d.LastWriteTime)" | Out-File $o -Append
}
"done" | Out-File $o -Append
Write-Host "saved $o"

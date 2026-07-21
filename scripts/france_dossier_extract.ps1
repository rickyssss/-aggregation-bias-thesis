# Stream the 672MB INSEE dossier_complet.csv, extract chosen columns, aggregate to
# department level, derive rates, save small coarse/fine CSVs, compute pairwise correlations.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"
$srcFile = "$repo\scratch\dossier_complet\dossier_complet.csv"

$wantedCols = @("CODGEO","P22_POP","P22_POP0014","P22_POP7589","P22_POP90P","P22_ACTOCC15P","P22_SAL15P","P22_LOG","P22_RSECOCC","P22_LOGVAC","MED_SL23","PR_MD60_23","P22_RP","P22_MAISON","P22_APPART")

$reader = New-Object System.IO.StreamReader($srcFile)
$header = $reader.ReadLine() -split ";"
$idx = @{}
foreach ($w in $wantedCols) { $idx[$w] = [array]::IndexOf($header, $w) }

function ParseNum($s) {
    if ([string]::IsNullOrWhiteSpace($s)) { return [double]::NaN }
    $n = 0.0
    if ([double]::TryParse($s.Replace(",","."), [System.Globalization.NumberStyles]::Any, [System.Globalization.CultureInfo]::InvariantCulture, [ref]$n)) { return $n }
    return [double]::NaN
}

$fineRows = New-Object System.Collections.Generic.List[object]
$deptAgg = @{}   # dept code -> hashtable of sums
$lineCount = 0

while (-not $reader.EndOfStream) {
    $line = $reader.ReadLine()
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    $f = $line -split ";"
    $codgeo = $f[$idx["CODGEO"]]
    if ([string]::IsNullOrWhiteSpace($codgeo)) { continue }

    $dept = $null
    if ($codgeo.StartsWith("97")) { $dept = $codgeo.Substring(0,3) }
    elseif ($codgeo.StartsWith("2A") -or $codgeo.StartsWith("2B")) { $dept = $codgeo.Substring(0,2) }
    else { $dept = $codgeo.Substring(0,2) }

    $vals = @{}
    foreach ($w in $wantedCols) { $vals[$w] = ParseNum $f[$idx[$w]] }

    # fine row (rates derived per commune)
    $pop = $vals["P22_POP"]
    if ($pop -gt 0) {
        $fineRows.Add([PSCustomObject]@{
            geo = $codgeo
            elderly_rate = 1000.0 * ($vals["P22_POP7589"] + $vals["P22_POP90P"]) / $pop
            young_rate = 1000.0 * $vals["P22_POP0014"] / $pop
            employed_rate = 1000.0 * $vals["P22_ACTOCC15P"] / $pop
            salaried_rate = 1000.0 * $vals["P22_SAL15P"] / $pop
            vacant_housing_rate = if ($vals["P22_LOG"] -gt 0) { 1000.0 * $vals["P22_LOGVAC"] / $vals["P22_LOG"] } else { [double]::NaN }
            secondary_housing_rate = if ($vals["P22_LOG"] -gt 0) { 1000.0 * $vals["P22_RSECOCC"] / $vals["P22_LOG"] } else { [double]::NaN }
            house_share = if ($vals["P22_LOG"] -gt 0) { 1000.0 * $vals["P22_MAISON"] / $vals["P22_LOG"] } else { [double]::NaN }
            median_living_standard = $vals["MED_SL23"]
            poverty_rate = $vals["PR_MD60_23"]
        })
    }

    # department aggregation (sum raw counts; medians/rates handled via population-weighted average as approximation)
    if (-not $deptAgg.ContainsKey($dept)) {
        $deptAgg[$dept] = @{ pop=0.0; pop0014=0.0; pop7589=0.0; pop90p=0.0; actocc=0.0; sal=0.0; log=0.0; logvac=0.0; rsecocc=0.0; maison=0.0; medsl_wsum=0.0; pov_wsum=0.0 }
    }
    $d = $deptAgg[$dept]
    if (-not [double]::IsNaN($pop)) { $d.pop += $pop }
    if (-not [double]::IsNaN($vals["P22_POP0014"])) { $d.pop0014 += $vals["P22_POP0014"] }
    if (-not [double]::IsNaN($vals["P22_POP7589"])) { $d.pop7589 += $vals["P22_POP7589"] }
    if (-not [double]::IsNaN($vals["P22_POP90P"])) { $d.pop90p += $vals["P22_POP90P"] }
    if (-not [double]::IsNaN($vals["P22_ACTOCC15P"])) { $d.actocc += $vals["P22_ACTOCC15P"] }
    if (-not [double]::IsNaN($vals["P22_SAL15P"])) { $d.sal += $vals["P22_SAL15P"] }
    if (-not [double]::IsNaN($vals["P22_LOG"])) { $d.log += $vals["P22_LOG"] }
    if (-not [double]::IsNaN($vals["P22_LOGVAC"])) { $d.logvac += $vals["P22_LOGVAC"] }
    if (-not [double]::IsNaN($vals["P22_RSECOCC"])) { $d.rsecocc += $vals["P22_RSECOCC"] }
    if (-not [double]::IsNaN($vals["P22_MAISON"])) { $d.maison += $vals["P22_MAISON"] }
    if (-not [double]::IsNaN($vals["MED_SL23"]) -and $pop -gt 0) { $d.medsl_wsum += $vals["MED_SL23"] * $pop }
    if (-not [double]::IsNaN($vals["PR_MD60_23"]) -and $pop -gt 0) { $d.pov_wsum += $vals["PR_MD60_23"] * $pop }

    $lineCount++
}
$reader.Close()

"Processed $lineCount commune rows into $($fineRows.Count) valid fine rows and $($deptAgg.Count) departments"

$coarseRows = New-Object System.Collections.Generic.List[object]
foreach ($dept in $deptAgg.Keys) {
    $d = $deptAgg[$dept]
    if ($d.pop -le 0) { continue }
    $coarseRows.Add([PSCustomObject]@{
        geo = $dept
        elderly_rate = 1000.0 * ($d.pop7589 + $d.pop90p) / $d.pop
        young_rate = 1000.0 * $d.pop0014 / $d.pop
        employed_rate = 1000.0 * $d.actocc / $d.pop
        salaried_rate = 1000.0 * $d.sal / $d.pop
        vacant_housing_rate = if ($d.log -gt 0) { 1000.0 * $d.logvac / $d.log } else { [double]::NaN }
        secondary_housing_rate = if ($d.log -gt 0) { 1000.0 * $d.rsecocc / $d.log } else { [double]::NaN }
        house_share = if ($d.log -gt 0) { 1000.0 * $d.maison / $d.log } else { [double]::NaN }
        median_living_standard = $d.medsl_wsum / $d.pop
        poverty_rate = $d.pov_wsum / $d.pop
    })
}
"Coarse (department, aggregated from communes) rows: $($coarseRows.Count)"

New-Item -ItemType Directory -Force -Path "$repo\data\France" | Out-Null
$coarseRows | Export-Csv "$repo\data\France\dossier_coarse_deptagg.csv" -NoTypeInformation -Encoding UTF8
$fineRows | Export-Csv "$repo\data\France\dossier_fine_commune.csv" -NoTypeInformation -Encoding UTF8
"Saved coarse/fine CSVs."

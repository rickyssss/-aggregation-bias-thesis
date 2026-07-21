# CDC/ATSDR Social Vulnerability Index 2022: county (coarse) vs census tract (fine).
# EP_* fields are already published as percentages -- used as-is, no conversion needed.

$ErrorActionPreference = "Stop"
$repo = "C:\Users\saika\-aggregation-bias-thesis"

$vars = @("EP_POV150","EP_UNEMP","EP_HBURD","EP_NOHSDP","EP_UNINSUR","EP_AGE65","EP_AGE17","EP_DISABL","EP_SNGPNT","EP_LIMENG","EP_MINRTY","EP_MUNIT","EP_MOBILE","EP_CROWD","EP_NOVEH","EP_GROUPQ","EP_NOINT","EP_AFAM","EP_HISP","EP_ASIAN","EP_AIAN","EP_NHPI","EP_TWOMORE","EP_OTHERRACE")

function LoadVals($path) {
    $reader = New-Object System.IO.StreamReader($path)
    $header = ($reader.ReadLine()) -split ","
    $idx = @{}
    foreach ($v in $vars) { $idx[$v] = [array]::IndexOf($header, $v) }
    $vals = @{}
    foreach ($v in $vars) { $vals[$v] = New-Object System.Collections.Generic.List[double] }
    $n = 0
    while (-not $reader.EndOfStream) {
        $line = $reader.ReadLine()
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        $f = $line -split ","
        foreach ($v in $vars) {
            $s = $f[$idx[$v]]
            $d = 0.0
            if ($s -ne $null -and $s -ne "" -and $s -ne "-999" -and [double]::TryParse($s, [ref]$d)) {
                $vals[$v].Add($d)
            } else {
                $vals[$v].Add([double]::NaN)
            }
        }
        $n++
    }
    $reader.Close()
    return @{ vals = $vals; n = $n }
}

$coarse = LoadVals "$repo\scratch\svi\county.csv"
$fine = LoadVals "$repo\scratch\svi\tract.csv"
"Coarse (county) rows: $($coarse.n), Fine (tract) rows: $($fine.n)"

function Get-Correlation($xs, $ys) {
    $n = $xs.Count
    if ($n -lt 4) { return $null }
    $mx = ($xs | Measure-Object -Average).Average
    $my = ($ys | Measure-Object -Average).Average
    $sumXY = 0.0; $sumX2 = 0.0; $sumY2 = 0.0
    for ($i = 0; $i -lt $n; $i++) {
        $dx = $xs[$i] - $mx; $dy = $ys[$i] - $my
        $sumXY += $dx * $dy; $sumX2 += $dx * $dx; $sumY2 += $dy * $dy
    }
    if ($sumX2 -eq 0 -or $sumY2 -eq 0) { return $null }
    return $sumXY / [Math]::Sqrt($sumX2 * $sumY2)
}
$tTable = @{1=12.706;2=4.303;3=3.182;4=2.776;5=2.571;6=2.447;7=2.365;8=2.306;9=2.262;10=2.228;11=2.201;12=2.179;13=2.160;14=2.145;15=2.131;16=2.120;17=2.110;18=2.101;19=2.093;20=2.086;21=2.080;22=2.074;23=2.069;24=2.064;25=2.060;26=2.056;27=2.052;28=2.048;29=2.045;30=2.042}
function Get-CriticalT($df) { if ($df -le 30) { return $tTable[$df] }; return 1.96 + (2.042-1.96)*[Math]::Max(0,(30.0/$df)) }
function Test-Sig($r,$n) { if ($null -eq $r -or $n -lt 4) { return "n/a" }; $df=$n-2; $absR=[Math]::Abs($r); if ($absR -ge 0.999999) {return "yes"}; $t=$absR*[Math]::Sqrt($df/(1-$absR*$absR)); if ($t -ge (Get-CriticalT $df)) {return "yes"} else {return "no"} }

function ValidPairs($xList, $yList) {
    $xs = New-Object System.Collections.Generic.List[double]
    $ys = New-Object System.Collections.Generic.List[double]
    for ($i = 0; $i -lt $xList.Count; $i++) {
        if (-not [double]::IsNaN($xList[$i]) -and -not [double]::IsNaN($yList[$i])) {
            $xs.Add($xList[$i]); $ys.Add($yList[$i])
        }
    }
    return @($xs, $ys)
}

$results = New-Object System.Collections.Generic.List[object]
for ($i = 0; $i -lt $vars.Count; $i++) {
    for ($j = $i + 1; $j -lt $vars.Count; $j++) {
        $c1 = $vars[$i]; $c2 = $vars[$j]

        $pc = ValidPairs $coarse.vals[$c1] $coarse.vals[$c2]
        $rCoarse = Get-Correlation $pc[0] $pc[1]
        $nCoarse = $pc[0].Count

        $pf = ValidPairs $fine.vals[$c1] $fine.vals[$c2]
        $rFine = Get-Correlation $pf[0] $pf[1]
        $nFine = $pf[0].Count

        if ($null -eq $rCoarse -or $null -eq $rFine) { continue }

        $diffType = "similar"
        if ([Math]::Sign($rCoarse) -ne [Math]::Sign($rFine) -and [Math]::Abs($rCoarse) -gt 0.05 -and [Math]::Abs($rFine) -gt 0.05) {
            $diffType = "reversed"
        } elseif ([Math]::Abs($rCoarse) -gt 0.001) {
            $relChange = [Math]::Abs([Math]::Abs($rCoarse) - [Math]::Abs($rFine)) / [Math]::Abs($rCoarse)
            if ($relChange -gt 0.3) { $diffType = "magnitude_change" }
        }

        $obj = New-Object PSObject
        $obj | Add-Member -MemberType NoteProperty -Name id -Value ""
        $obj | Add-Member -MemberType NoteProperty -Name country -Value "US"
        $obj | Add-Member -MemberType NoteProperty -Name variable -Value ($c1 + " vs " + $c2)
        $obj | Add-Member -MemberType NoteProperty -Name coarse_level -Value ("county(n=" + $nCoarse + ")")
        $obj | Add-Member -MemberType NoteProperty -Name coarse_stat -Value ("corr=" + [Math]::Round($rCoarse,3))
        $obj | Add-Member -MemberType NoteProperty -Name fine_level -Value ("tract(n=" + $nFine + ")")
        $obj | Add-Member -MemberType NoteProperty -Name fine_stat -Value ("corr=" + [Math]::Round($rFine,3))
        $obj | Add-Member -MemberType NoteProperty -Name diff_type -Value $diffType
        $obj | Add-Member -MemberType NoteProperty -Name notes -Value "CDC/ATSDR Social Vulnerability Index 2022. EP_* fields are published percentages (ACS-based), used as-is. No registration required. County vs census tract."
        $obj | Add-Member -MemberType NoteProperty -Name coarse_significant_p05 -Value (Test-Sig $rCoarse $nCoarse)
        $obj | Add-Member -MemberType NoteProperty -Name fine_significant_p05 -Value (Test-Sig $rFine $nFine)
        $results.Add($obj)
    }
}
"Pairs: $($results.Count)"
$results | Export-Csv "$repo\results\cdc_svi_pairwise.csv" -NoTypeInformation -Encoding UTF8
"Saved."

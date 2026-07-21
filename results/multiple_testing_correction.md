# 多重検定補正

results/summary_table.csv から抽出できる全ての相関検定に対して、Benjamini-Hochberg 法で false discovery rate を補正した。各行は最大2件の検定、すなわち粗い集計単位の相関と細かい集計単位の相関を持つ。CV比較など、corr= ではない行は除外した。

- 入力行数: 3420
- 補正対象の相関検定数: 6826
- 補正前 p <= 0.05: 5617
- BH補正後 q <= 0.05: 5570
- 粗い単位でBH補正後も有意: 2529 / 3413
- 細かい単位でBH補正後も有意: 3041 / 3413
- 少なくとも片側の相関がBH補正後も有意な行: 3212
- 粗い単位・細かい単位の両方がBH補正後も有意な行: 2358
- 符号反転(reversed)の検定のうちBH補正後も有意: 452
- 符号反転(reversed)行のうち粗細両方がBH補正後も有意: 136

## diff_type別

| diff_type | 検定数 | BH q <= 0.05 |
|---|---:|---:|
| magnitude_change | 3500 | 2556 |
| reversed | 634 | 452 |
| similar | 2692 | 2562 |

## q値が最小の例

| id | country | level | variable | stat | p | BH q |
|---|---|---|---|---:|---:|---:|
| 2339 | US | fine | EP_AFAM vs EP_HISP | corr=0.925 | 0.000E+000 | 0.000E+000 |
| 1447 | US | fine | CANCER_CrudePrev vs COPD_CrudePrev | corr=0.299 | 0.000E+000 | 0.000E+000 |
| 2193 | US | fine | EP_AGE65 vs EP_MINRTY | corr=0.918 | 0.000E+000 | 0.000E+000 |
| 1449 | US | fine | CANCER_CrudePrev vs DENTAL_CrudePrev | corr=0.38 | 0.000E+000 | 0.000E+000 |
| 2192 | US | fine | EP_AGE65 vs EP_LIMENG | corr=0.988 | 0.000E+000 | 0.000E+000 |
| 2192 | US | coarse | EP_AGE65 vs EP_LIMENG | corr=0.731 | 0.000E+000 | 0.000E+000 |
| 1452 | US | fine | CANCER_CrudePrev vs GHLTH_CrudePrev | corr=-0.262 | 0.000E+000 | 0.000E+000 |
| 1453 | US | fine | CANCER_CrudePrev vs HIGHCHOL_CrudePrev | corr=0.664 | 0.000E+000 | 0.000E+000 |
| 1456 | US | fine | CANCER_CrudePrev vs MHLTH_CrudePrev | corr=-0.511 | 0.000E+000 | 0.000E+000 |
| 2191 | US | fine | EP_AGE65 vs EP_SNGPNT | corr=0.808 | 0.000E+000 | 0.000E+000 |

詳細は results/multiple_testing_correction.csv に保存した。

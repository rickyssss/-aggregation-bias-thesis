# 多重検定補正

results/summary_table.csv から抽出できる全ての相関検定に対して、Benjamini-Hochberg 法で false discovery rate を補正した。各行は最大2件の検定、すなわち粗い集計単位の相関と細かい集計単位の相関を持つ。CV比較など、corr= ではない行は除外した。

- 入力行数: 2359
- 補正対象の相関検定数: 4706
- 補正前 p <= 0.05: 3898
- BH補正後 q <= 0.05: 3873
- 粗い単位でBH補正後も有意: 1733 / 2353
- 細かい単位でBH補正後も有意: 2140 / 2353
- 少なくとも片側の相関がBH補正後も有意な行: 2225
- 粗い単位・細かい単位の両方がBH補正後も有意な行: 1648
- 符号反転(reversed)の検定のうちBH補正後も有意: 350
- 符号反転(reversed)行のうち粗細両方がBH補正後も有意: 106

## diff_type別

| diff_type | 検定数 | BH q <= 0.05 |
|---|---:|---:|
| magnitude_change | 2296 | 1693 |
| reversed | 490 | 350 |
| similar | 1920 | 1830 |

## q値が最小の例

| id | country | level | variable | stat | p | BH q |
|---|---|---|---|---:|---:|---:|
| 2359 | US | fine | EP_TWOMORE vs EP_OTHERRACE | corr=0.999 | 0.000E+000 | 0.000E+000 |
| 1866 | US | fine | OBESITY_CrudePrev vs PHLTH_CrudePrev | corr=0.655 | 0.000E+000 | 0.000E+000 |
| 824 | US | fine | B01002_001E vs B25024_002E | corr=0.609 | 0.000E+000 | 0.000E+000 |
| 1867 | US | fine | OBESITY_CrudePrev vs SLEEP_CrudePrev | corr=0.56 | 0.000E+000 | 0.000E+000 |
| 1868 | US | fine | OBESITY_CrudePrev vs STROKE_CrudePrev | corr=0.57 | 0.000E+000 | 0.000E+000 |
| 1869 | US | fine | OBESITY_CrudePrev vs TEETHLOST_CrudePrev | corr=0.652 | 0.000E+000 | 0.000E+000 |
| 1870 | US | fine | OBESITY_CrudePrev vs HEARING_CrudePrev | corr=0.381 | 0.000E+000 | 0.000E+000 |
| 1871 | US | fine | OBESITY_CrudePrev vs VISION_CrudePrev | corr=0.607 | 0.000E+000 | 0.000E+000 |
| 1872 | US | fine | OBESITY_CrudePrev vs COGNITION_CrudePrev | corr=0.662 | 0.000E+000 | 0.000E+000 |
| 1873 | US | coarse | OBESITY_CrudePrev vs MOBILITY_CrudePrev | corr=0.639 | 0.000E+000 | 0.000E+000 |

詳細は results/multiple_testing_correction.csv に保存した。

# 多重検定補正

results/summary_table.csv から抽出できる全ての相関検定に対して、Benjamini-Hochberg 法で false discovery rate を補正した。各行は最大2件の検定、すなわち粗い集計単位の相関と細かい集計単位の相関を持つ。CV比較など、corr= ではない行は除外した。

- 入力行数: 5658
- 補正対象の相関検定数: 11302
- 補正前 p <= 0.05: 8494
- BH補正後 q <= 0.05: 8354
- 粗い単位でBH補正後も有意: 3520 / 5651
- 細かい単位でBH補正後も有意: 4834 / 5651
- 少なくとも片側の相関がBH補正後も有意な行: 5057
- 粗い単位・細かい単位の両方がBH補正後も有意な行: 3297
- 符号反転(reversed)の検定のうちBH補正後も有意: 647
- 符号反転(reversed)行のうち粗細両方がBH補正後も有意: 151

## diff_type別

| diff_type | 検定数 | BH q <= 0.05 |
|---|---:|---:|
| magnitude_change | 5664 | 3627 |
| reversed | 1158 | 647 |
| similar | 4480 | 4080 |

## q値が最小の例

| id | country | level | variable | stat | p | BH q |
|---|---|---|---|---:|---:|---:|
| 2297 | US | fine | EP_MOBILE vs EP_NOINT | corr=0.973 | 0.000E+000 | 0.000E+000 |
| 1678 | US | coarse | CSMOKING_CrudePrev vs DISABILITY_CrudePrev | corr=0.81 | 0.000E+000 | 0.000E+000 |
| 1678 | US | fine | CSMOKING_CrudePrev vs DISABILITY_CrudePrev | corr=0.813 | 0.000E+000 | 0.000E+000 |
| 1679 | US | fine | CSMOKING_CrudePrev vs LONELINESS_CrudePrev | corr=0.431 | 0.000E+000 | 0.000E+000 |
| 1680 | US | fine | CSMOKING_CrudePrev vs FOODSTAMP_CrudePrev | corr=0.727 | 0.000E+000 | 0.000E+000 |
| 1681 | US | fine | CSMOKING_CrudePrev vs FOODINSECU_CrudePrev | corr=0.714 | 0.000E+000 | 0.000E+000 |
| 1682 | US | fine | CSMOKING_CrudePrev vs HOUSINSECU_CrudePrev | corr=0.644 | 0.000E+000 | 0.000E+000 |
| 1683 | US | coarse | CSMOKING_CrudePrev vs SHUTUTILITY_CrudePrev | corr=0.706 | 0.000E+000 | 0.000E+000 |
| 1683 | US | fine | CSMOKING_CrudePrev vs SHUTUTILITY_CrudePrev | corr=0.76 | 0.000E+000 | 0.000E+000 |
| 1684 | US | fine | CSMOKING_CrudePrev vs LACKTRPT_CrudePrev | corr=0.732 | 0.000E+000 | 0.000E+000 |

詳細は results/multiple_testing_correction.csv に保存した。

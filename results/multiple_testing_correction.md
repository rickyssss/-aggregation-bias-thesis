# 多重検定補正

results/summary_table.csv から抽出できる全ての相関検定に対して、Benjamini-Hochberg 法で false discovery rate を補正した。各行は最大2件の検定、すなわち粗い集計単位の相関と細かい集計単位の相関を持つ。CV比較など、corr= ではない行は除外した。

- 入力行数: 5707
- 補正対象の相関検定数: 11400
- 補正前 p <= 0.05: 8579
- BH補正後 q <= 0.05: 8448
- 粗い単位でBH補正後も有意: 3563 / 5700
- 細かい単位でBH補正後も有意: 4885 / 5700
- 少なくとも片側の相関がBH補正後も有意な行: 5112
- 粗い単位・細かい単位の両方がBH補正後も有意な行: 3336
- 符号反転(reversed)の検定のうちBH補正後も有意: 649
- 符号反転(reversed)行のうち粗細両方がBH補正後も有意: 151

## diff_type別

| diff_type | 検定数 | BH q <= 0.05 |
|---|---:|---:|
| magnitude_change | 5702 | 3667 |
| reversed | 1162 | 649 |
| similar | 4536 | 4132 |

## q値が最小の例

| id | country | level | variable | stat | p | BH q |
|---|---|---|---|---:|---:|---:|
| 2169 | US | fine | EP_NOHSDP vs EP_OTHERRACE | corr=0.972 | 0.000E+000 | 0.000E+000 |
| 2019 | US | fine | LONELINESS_CrudePrev vs SHUTUTILITY_CrudePrev | corr=0.677 | 0.000E+000 | 0.000E+000 |
| 2019 | US | coarse | LONELINESS_CrudePrev vs SHUTUTILITY_CrudePrev | corr=0.714 | 0.000E+000 | 0.000E+000 |
| 2018 | US | fine | LONELINESS_CrudePrev vs HOUSINSECU_CrudePrev | corr=0.747 | 0.000E+000 | 0.000E+000 |
| 2018 | US | coarse | LONELINESS_CrudePrev vs HOUSINSECU_CrudePrev | corr=0.777 | 0.000E+000 | 0.000E+000 |
| 2017 | US | fine | LONELINESS_CrudePrev vs FOODINSECU_CrudePrev | corr=0.715 | 0.000E+000 | 0.000E+000 |
| 2017 | US | coarse | LONELINESS_CrudePrev vs FOODINSECU_CrudePrev | corr=0.736 | 0.000E+000 | 0.000E+000 |
| 2016 | US | fine | LONELINESS_CrudePrev vs FOODSTAMP_CrudePrev | corr=0.672 | 0.000E+000 | 0.000E+000 |
| 2020 | US | coarse | LONELINESS_CrudePrev vs LACKTRPT_CrudePrev | corr=0.734 | 0.000E+000 | 0.000E+000 |
| 2016 | US | coarse | LONELINESS_CrudePrev vs FOODSTAMP_CrudePrev | corr=0.694 | 0.000E+000 | 0.000E+000 |

詳細は results/multiple_testing_correction.csv に保存した。

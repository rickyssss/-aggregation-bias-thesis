# 多重検定補正

results/summary_table.csv から抽出できる全ての相関検定に対して、Benjamini-Hochberg 法で false discovery rate を補正した。各行は最大2件の検定、すなわち粗い集計単位の相関と細かい集計単位の相関を持つ。CV比較など、corr= ではない行は除外した。

- 入力行数: 5583
- 補正対象の相関検定数: 11152
- 補正前 p <= 0.05: 8391
- BH補正後 q <= 0.05: 8263
- 粗い単位でBH補正後も有意: 3494 / 5576
- 細かい単位でBH補正後も有意: 4769 / 5576
- 少なくとも片側の相関がBH補正後も有意な行: 4995
- 粗い単位・細かい単位の両方がBH補正後も有意な行: 3268
- 符号反転(reversed)の検定のうちBH補正後も有意: 645
- 符号反転(reversed)行のうち粗細両方がBH補正後も有意: 151

## diff_type別

| diff_type | 検定数 | BH q <= 0.05 |
|---|---:|---:|
| magnitude_change | 5588 | 3597 |
| reversed | 1154 | 645 |
| similar | 4410 | 4021 |

## q値が最小の例

| id | country | level | variable | stat | p | BH q |
|---|---|---|---|---:|---:|---:|
| 5583 | Switzerland | fine | swiss_male_per1000 vs swiss_female_per1000 | corr=0.85 | 0.000E+000 | 0.000E+000 |
| 1968 | US | fine | VISION_CrudePrev vs SHUTUTILITY_CrudePrev | corr=0.912 | 0.000E+000 | 0.000E+000 |
| 1968 | US | coarse | VISION_CrudePrev vs SHUTUTILITY_CrudePrev | corr=0.913 | 0.000E+000 | 0.000E+000 |
| 1967 | US | fine | VISION_CrudePrev vs HOUSINSECU_CrudePrev | corr=0.891 | 0.000E+000 | 0.000E+000 |
| 1967 | US | coarse | VISION_CrudePrev vs HOUSINSECU_CrudePrev | corr=0.893 | 0.000E+000 | 0.000E+000 |
| 1966 | US | fine | VISION_CrudePrev vs FOODINSECU_CrudePrev | corr=0.945 | 0.000E+000 | 0.000E+000 |
| 1966 | US | coarse | VISION_CrudePrev vs FOODINSECU_CrudePrev | corr=0.945 | 0.000E+000 | 0.000E+000 |
| 1969 | US | coarse | VISION_CrudePrev vs LACKTRPT_CrudePrev | corr=0.927 | 0.000E+000 | 0.000E+000 |
| 1965 | US | fine | VISION_CrudePrev vs FOODSTAMP_CrudePrev | corr=0.916 | 0.000E+000 | 0.000E+000 |
| 1964 | US | fine | VISION_CrudePrev vs LONELINESS_CrudePrev | corr=0.56 | 0.000E+000 | 0.000E+000 |

詳細は results/multiple_testing_correction.csv に保存した。

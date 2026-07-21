# 多重検定補正

results/summary_table.csv から抽出できる全ての相関検定に対して、Benjamini-Hochberg 法で false discovery rate を補正した。各行は最大2件の検定、すなわち粗い集計単位の相関と細かい集計単位の相関を持つ。CV比較など、corr= ではない行は除外した。

- 入力行数: 2081
- 補正対象の相関検定数: 4154
- 補正前 p <= 0.05: 3375
- BH補正後 q <= 0.05: 3345
- 粗い単位でBH補正後も有意: 1485 / 2077
- 細かい単位でBH補正後も有意: 1860 / 2077
- 少なくとも片側の相関がBH補正後も有意な行: 1947
- 粗い単位・細かい単位の両方がBH補正後も有意な行: 1398
- 符号反転(reversed)の検定のうちBH補正後も有意: 308
- 符号反転(reversed)行のうち粗細両方がBH補正後も有意: 85

## diff_type別

| diff_type | 検定数 | BH q <= 0.05 |
|---|---:|---:|
| magnitude_change | 1974 | 1394 |
| reversed | 448 | 308 |
| similar | 1732 | 1643 |

## q値が最小の例

| id | country | level | variable | stat | p | BH q |
|---|---|---|---|---:|---:|---:|
| 1708 | US | fine | DENTAL_CrudePrev vs HOUSINSECU_CrudePrev | corr=-0.731 | 0.000E+000 | 0.000E+000 |
| 1523 | US | fine | CHD_CrudePrev vs PHLTH_CrudePrev | corr=0.773 | 0.000E+000 | 0.000E+000 |
| 1824 | US | coarse | LPA_CrudePrev vs SHUTUTILITY_CrudePrev | corr=0.763 | 0.000E+000 | 0.000E+000 |
| 1824 | US | fine | LPA_CrudePrev vs SHUTUTILITY_CrudePrev | corr=0.768 | 0.000E+000 | 0.000E+000 |
| 1825 | US | coarse | LPA_CrudePrev vs LACKTRPT_CrudePrev | corr=0.716 | 0.000E+000 | 0.000E+000 |
| 1825 | US | fine | LPA_CrudePrev vs LACKTRPT_CrudePrev | corr=0.725 | 0.000E+000 | 0.000E+000 |
| 924 | US | coarse | B01001_002E vs B01001_026E | corr=-1 | 0.000E+000 | 0.000E+000 |
| 428 | 日本 | fine | 15～64歳人口 per1000pop(A1302_rate) vs 15～64歳人口（男） per1000pop(A130201_rate) | corr=0.879 | 0.000E+000 | 0.000E+000 |
| 924 | US | fine | B01001_002E vs B01001_026E | corr=-1 | 0.000E+000 | 0.000E+000 |
| 1523 | US | coarse | CHD_CrudePrev vs PHLTH_CrudePrev | corr=0.812 | 0.000E+000 | 0.000E+000 |

詳細は results/multiple_testing_correction.csv に保存した。

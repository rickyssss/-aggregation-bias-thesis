# 多重検定補正

`results/summary_table.csv` から抽出できる全ての相関検定に対して、Benjamini-Hochberg 法で false discovery rate を補正した。各行は最大2件の検定、すなわち粗い集計単位の相関と細かい集計単位の相関を持つ。CV比較など、`corr=` ではない行は除外した。

- 入力行数: 798
- 補正対象の相関検定数: 1590
- 補正前 p <= 0.05: 1185
- BH補正後 q <= 0.05: 1162
- 粗い単位でBH補正後も有意: 454 / 795
- 細かい単位でBH補正後も有意: 708 / 795
- 少なくとも片側の相関がBH補正後も有意な行: 735
- 粗い単位・細かい単位の両方がBH補正後も有意な行: 427
- 符号反転(reversed)の検定のうちBH補正後も有意: 190
- 符号反転(reversed)行のうち粗細両方がBH補正後も有意: 48

## diff_type別

| diff_type | 検定数 | BH q <= 0.05 |
|---|---:|---:|
| magnitude_change | 904 | 609 |
| reversed | 286 | 190 |
| similar | 400 | 363 |

## q値が最小の例

| id | country | level | variable | stat | p | BH q |
|---|---|---|---|---:|---:|---:|
| 6 | イギリス | fine | 人口と高齢化率(65歳以上割合)の相関 | corr=-0.309 | 0.000e+0 | 0.000e+0 |
| 12 | カナダ | coarse | num_households_2021_total と num_households_2016_total の相関 | corr=1.000 | 0.000e+0 | 0.000e+0 |
| 12 | カナダ | fine | num_households_2021_total と num_households_2016_total の相関 | corr=1.000 | 0.000e+0 | 0.000e+0 |
| 17 | カナダ | fine | num_households_2021_total と num_households_2021_1person の相関 | corr=0.982 | 0.000e+0 | 0.000e+0 |
| 19 | カナダ | fine | num_households_2021_total と num_households_2021_census_family の相関 | corr=0.994 | 0.000e+0 | 0.000e+0 |
| 21 | カナダ | fine | num_households_2021_total と num_households_2021_non_census_family の相関 | corr=0.985 | 0.000e+0 | 0.000e+0 |
| 27 | カナダ | fine | num_households_2016_total と num_households_2021_1person の相関 | corr=0.984 | 0.000e+0 | 0.000e+0 |
| 29 | カナダ | fine | num_households_2016_total と num_households_2021_census_family の相関 | corr=0.993 | 0.000e+0 | 0.000e+0 |
| 31 | カナダ | fine | num_households_2016_total と num_households_2021_non_census_family の相関 | corr=0.986 | 0.000e+0 | 0.000e+0 |
| 33 | カナダ | fine | median_total_income_2020_total_cad と median_total_income_2015_total_cad の相関 | corr=0.874 | 0.000e+0 | 0.000e+0 |

詳細は `results/multiple_testing_correction.csv` に保存した。

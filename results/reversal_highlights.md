# 集計単位による結果の変化：抜粋ハイライト

このファイルは `results/aggregation_effect_log.md`（全件記録）の中から、粗い集計単位と細かい集計単位で相関の符号（プラス/マイナス）が逆転した、または符号は同じでも大きさが大きく変わったケースだけを抜き出したものです。全件の記録はあくまで `aggregation_effect_log.md` にあり、このファイルはその省略版ではなく「抜粋・目立たせ」のためのものです。

---

## 2026-07-20: 日本の人口と高齢化率の相関（id=1）

- **変数**: 総人口 と 高齢化率（65歳以上人口÷総人口）の相関係数（2020年）
- **都道府県単位（47件）**: 相関係数 -0.688（人口が多いほど高齢化率が低い、という比較的強い負の相関）
- **市区町村単位（1,740件）**: 相関係数 -0.323（同じくマイナスだが、強さはおよそ半分）
- **分類**: 符号は同じ（マイナス）だが、大きさが大きく変化（-0.688 → -0.323、絶対値でおよそ半減）
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-20（2回目：id=1 日本・人口）」の項、要約統計量は `results/summaries/id01_japan_population_2020.csv` を参照。

---

## 2026-07-20: アメリカの人口と一人当たり個人所得の相関（id=5）

- **変数**: 人口 と 一人当たり個人所得（Per capita personal income）の相関係数（2024年）
- **州単位（51件、50州＋DC）**: 相関係数 +0.140（弱い正の相関）
- **郡単位（3,115件）**: 相関係数 +0.216（州単位よりやや強い、弱〜中程度の正の相関）
- **分類**: 符号は同じ（プラス）だが、大きさが変化（+0.140 → +0.216、相対的に約5割増加）
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-20（5回目：id=5 アメリカ・個人所得）」の項、要約統計量は `results/summaries/id05_usa_personal_income_2024.csv` を参照。

---

## 2026-07-20: カナダの世帯数と世帯所得中央値の相関（id=10）

- **変数**: 世帯数（2021年） と 世帯の総所得中央値（2020年、カナダドル）の相関係数
- **州・準州単位（13件）**: 相関係数 -0.136（弱いマイナスの相関）
- **国勢調査細分区域単位（3,660件）**: 相関係数 +0.075（弱いプラスの相関）
- **分類**: 符号が逆転（マイナス→プラス）。ただしどちらも0に近い弱い値であり、ほぼ無相関に近い数値の符号が入れ替わっただけの可能性がある点に注意。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-20（6回目：id=10 カナダ・世帯所得統計）」の項、要約統計量は `results/summaries/id10_canada_household_income_2021.csv` を参照。

---

## 2026-07-20: イギリスの人口と高齢化率の相関（id=6）

- **変数**: 総人口 と 高齢化率（65歳以上人口の割合、%）の相関係数（2023年）
- **地域単位（10件：イングランド9地域＋ウェールズ）**: 相関係数 -0.582（人口が多いほど高齢化率が低い、中程度の負の相関）
- **LSOA単位（35,672地区）**: 相関係数 -0.309（同じくマイナスだが、強さはおよそ半分）
- **分類**: 符号は同じ（マイナス）だが、大きさが大きく変化（-0.582 → -0.309、およそ半減）
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-20（7回目：id=6 イギリス・人口推計）」の項、要約統計量は `results/summaries/id06_uk_population_2023.csv` を参照。

---

## 2026-07-20: イギリスの人口と一人当たりGDHI(世帯可処分所得)の相関（id=7）

- **変数**: 総人口 と 一人当たりGDHI（Gross Disposable Household Income per head、ポンド）の相関係数（2022年）
- **ITL1地域単位（12件：イングランド9地域＋ウェールズ・スコットランド・北アイルランド）**: 相関係数 +0.746（人口が多い地域ほど一人当たり所得も高い、かなり強い正の相関）
- **地方自治体単位（361件）**: 相関係数 -0.082（弱いマイナスの相関）
- **分類**: 符号が逆転（強いプラス→弱いマイナス）。今回の中で最も逆転の幅が大きいケース。
- **背景**: 地方自治体単位で一人当たりGDHIが特に高いのは、City of London・Kensington and Chelsea・Westminsterなどロンドン中心部の「人口は少ないが所得は高い」自治体で、逆に人口の多いバーミンガムやリーズなどは一人当たり所得がむしろ平均以下。地域単位では人口も所得も突出したロンドン全体が強い正の相関を作り出しているが、地方自治体という細かい単位で見ると逆の傾向が見える。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-20（8回目：id=7 イギリス・世帯可処分所得(GDHI)）」の項、要約統計量は `results/summaries/id07_uk_gdhi_2022.csv` を参照。

---

## 2026-07-20: イギリスの所得水準のばらつき（変動係数）（id=8）

- **変数**: 所得水準の変動係数（標準偏差÷平均）。粗い単位は一人当たりGDHI（2020年）、細かい単位は世帯総所得のモデル推計（2020年3月期）※変数の定義は完全には一致しない点に注意
- **ITL1地域単位（イングランド・ウェールズ10地域）**: 変動係数 0.186、最大値/最小値の比 約1.69倍
- **MSOA単位（7,201地区）**: 変動係数 0.240、最大値/最小値の比 約4.87倍
- **分類**: 符号（プラス/マイナス）はそもそも存在しない指標だが、ばらつきの大きさが大きく変化（変動係数が約3割増、最大/最小比はおよそ3倍近くに拡大）
- **注意**: 比較している2つの所得変数の定義が完全一致しないため、他のケースより参考程度の位置づけ。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-20（9回目：id=8 イギリス・所得の推計値、地域 vs MSOA）」の項、要約統計量は `results/summaries/id08_uk_income_msoa_2020.csv` を参照。

---

## 2026-07-20: オーストラリアの人口と人口増加率の相関（id=11）

- **変数**: 総人口（2025年）と 人口増加率（2024〜2025年度、%）の相関係数
- **州・準州単位（8件）**: 相関係数 +0.158（弱いプラスの相関）
- **LGA（地方自治体地域）単位（546件）**: 相関係数 +0.283（州・準州単位よりやや強いプラスの相関）
- **分類**: 符号は同じ（プラス）だが、大きさが大きく変化（+0.158 → +0.283、相対的におよそ8割増加）
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-20（11回目：id=11 オーストラリア・推計人口）」の項、要約統計量は `results/summaries/id11_australia_population_2025.csv` を参照。

---

## 2026-07-20: カナダ（id=12〜77） 世帯所得・世帯数に関する12変数の総当たり相関

データ元: Statistics Canada Table 98-10-0057-01「Household income statistics by household type」（2021年国勢調査、州・準州単位 n=13 と 国勢細分区単位 n=5,161 の同一表）。12個の数値変数（総世帯数、単身/家族/非家族世帯数、世帯総所得・可処分所得の中央値など）の全組み合わせ66通りのうち、符号が逆転またはおおむね30%以上変化したものは以下35通り。

- **分類の内訳**: reversed 27件、magnitude_change 8件、similar 31件（詳細全件は`results/summary_table.csv`のid=12〜77）。
- **傾向**: 「世帯数」系の変数と「所得の中央値」系の変数の組み合わせのほとんどで、州・準州単位ではマイナスの弱い相関（-0.08〜-0.25程度）なのに、国勢細分区単位ではプラスの弱い相関（+0.03〜+0.12程度）に転じている。ただしいずれも絶対値0.3未満の弱い相関であり、「粗い単位でだけ見えている見かけの負の相関が、細かい単位では消えて符号が変わる」という典型的な生態学的相関（ecological correlation）の例と言える。

<details><summary>該当ペア一覧（クリックで展開）</summary>

| 変数の組み合わせ | 粗い単位の相関 | 細かい単位の相関 | 分類 |
|---|---|---|---|
| median_total_income_2015_total_cad と num_households_2021_1person | corr=-0.251 | corr=0.033 | magnitude_change |
| median_total_income_2015_total_cad と num_households_2021_non_census_family | corr=-0.243 | corr=0.034 | magnitude_change |
| median_total_income_2020_total_cad と num_households_2021_1person | corr=-0.176 | corr=0.043 | magnitude_change |
| median_aftertax_income_2020_total_cad と num_households_2021_1person | corr=-0.181 | corr=0.040 | magnitude_change |
| median_aftertax_income_2020_total_cad と num_households_2021_non_census_family | corr=-0.173 | corr=0.041 | magnitude_change |
| median_aftertax_income_2015_total_cad と num_households_2021_1person | corr=-0.250 | corr=0.031 | magnitude_change |
| median_total_income_2020_total_cad と num_households_2021_non_census_family | corr=-0.168 | corr=0.043 | magnitude_change |
| median_aftertax_income_2015_total_cad と num_households_2021_non_census_family | corr=-0.242 | corr=0.032 | magnitude_change |
| num_households_2021_1person と median_total_income_2020_census_family_cad | corr=-0.125 | corr=0.077 | reversed |
| median_aftertax_income_2015_total_cad と num_households_2021_census_family | corr=-0.188 | corr=0.076 | reversed |
| num_households_2021_1person と median_total_income_2020_non_census_family_cad | corr=-0.239 | corr=0.068 | reversed |
| median_total_income_2020_1person_cad と num_households_2021_census_family | corr=-0.197 | corr=0.088 | reversed |
| median_aftertax_income_2020_total_cad と num_households_2021_census_family | corr=-0.123 | corr=0.092 | reversed |
| median_total_income_2020_1person_cad と num_households_2021_non_census_family | corr=-0.220 | corr=0.057 | reversed |
| num_households_2021_census_family と median_total_income_2020_census_family_cad | corr=-0.084 | corr=0.122 | reversed |
| num_households_2021_census_family と median_total_income_2020_non_census_family_cad | corr=-0.208 | corr=0.104 | reversed |
| num_households_2021_1person と median_total_income_2020_1person_cad | corr=-0.222 | corr=0.057 | reversed |
| median_total_income_2015_total_cad と num_households_2021_census_family | corr=-0.191 | corr=0.077 | reversed |
| num_households_2021_total と median_total_income_2020_total_cad | corr=-0.136 | corr=0.075 | reversed |
| median_total_income_2020_total_cad と num_households_2021_census_family | corr=-0.119 | corr=0.094 | reversed |
| num_households_2016_total と median_total_income_2020_non_census_family_cad | corr=-0.219 | corr=0.089 | reversed |
| num_households_2016_total と median_total_income_2020_census_family_cad | corr=-0.097 | corr=0.103 | reversed |
| num_households_2016_total と median_total_income_2020_1person_cad | corr=-0.206 | corr=0.075 | reversed |
| num_households_2016_total と median_aftertax_income_2015_total_cad | corr=-0.208 | corr=0.076 | reversed |
| num_households_2016_total と median_aftertax_income_2020_total_cad | corr=-0.141 | corr=0.071 | reversed |
| num_households_2016_total と median_total_income_2015_total_cad | corr=-0.210 | corr=0.078 | reversed |
| num_households_2016_total と median_total_income_2020_total_cad | corr=-0.137 | corr=0.073 | reversed |
| num_households_2021_total と median_total_income_2020_non_census_family_cad | corr=-0.218 | corr=0.091 | reversed |
| num_households_2021_total と median_total_income_2020_census_family_cad | corr=-0.096 | corr=0.105 | reversed |
| num_households_2021_total と median_total_income_2020_1person_cad | corr=-0.205 | corr=0.077 | reversed |
| num_households_2021_total と median_aftertax_income_2015_total_cad | corr=-0.207 | corr=0.059 | reversed |
| num_households_2021_total と median_aftertax_income_2020_total_cad | corr=-0.140 | corr=0.073 | reversed |
| num_households_2021_total と median_total_income_2015_total_cad | corr=-0.209 | corr=0.061 | reversed |
| median_total_income_2020_census_family_cad と num_households_2021_non_census_family | corr=-0.119 | corr=0.077 | reversed |
| num_households_2021_non_census_family と median_total_income_2020_non_census_family_cad | corr=-0.236 | corr=0.069 | reversed |

</details>

---

## 2026-07-20: オーストラリア（id=78〜113） 人口動態・面積・人口密度に関する9変数の総当たり相関

データ元: ABS「Regional Population, 2024–25」datacube 32180DS0002（州・準州単位 n=9 と LGA=地方自治体地域単位 n=544、いずれも2024〜2025年会計年度・同一発表）。9個の数値変数（推計人口2024/2025、人口増減数・増減率、自然増加、純国内移動、純海外移動、面積、人口密度）の全組み合わせ36通りのうち、符号が逆転またはおおむね30%以上変化したものは以下25通り。

- **分類の内訳**: reversed 12件、magnitude_change 13件、similar 11件（詳細全件は`results/summary_table.csv`のid=78〜113）。
- **傾向**: 特に「面積(area_km2)」や「人口密度」が絡む組み合わせでほぼ全て符号が逆転している。例えば人口増減率と面積の相関は、州単位では+0.719という強い正の相関に見えるが、LGA単位では-0.126という弱い負の相関に転じる。州単位ではオーストラリア特有の「面積が広い州（西オーストラリア・北部準州など）ほど人口増加率が高い資源ブーム地域を含む」という少数の州の影響を強く受けるが、LGA単位まで細かく見ると、都市部の小さく高密度なLGAでも高い人口増加率を示すところが多数あるため、この関係が消えて逆転する。集計単位を粗くすることで少数の外れ値（州）が全体の相関を支配してしまう典型例。

<details><summary>該当ペア一覧（クリックで展開）</summary>

| 変数の組み合わせ | 粗い単位の相関 | 細かい単位の相関 | 分類 |
|---|---|---|---|
| ERP_2024 と ERP_change_pct | corr=0.480 | corr=0.280 | magnitude_change |
| net_internal_migration と population_density_2025 | corr=-0.082 | corr=-0.413 | magnitude_change |
| net_internal_migration と area_km2 | corr=0.459 | corr=-0.003 | magnitude_change |
| net_internal_migration と net_overseas_migration | corr=-0.193 | corr=-0.385 | magnitude_change |
| ERP_change_pct と population_density_2025 | corr=-0.009 | corr=0.162 | magnitude_change |
| ERP_change_pct と net_overseas_migration | corr=0.543 | corr=0.237 | magnitude_change |
| ERP_change_no と net_internal_migration | corr=0.043 | corr=0.240 | magnitude_change |
| ERP_change_no と ERP_change_pct | corr=0.649 | corr=0.453 | magnitude_change |
| ERP_change_pct と natural_increase | corr=0.544 | corr=0.371 | magnitude_change |
| ERP_2025 と net_internal_migration | corr=-0.208 | corr=-0.087 | magnitude_change |
| ERP_2025 と ERP_change_pct | corr=0.483 | corr=0.284 | magnitude_change |
| ERP_2024 と net_internal_migration | corr=-0.211 | corr=-0.094 | magnitude_change |
| area_km2 と population_density_2025 | corr=-0.455 | corr=-0.129 | magnitude_change |
| ERP_2025 と area_km2 | corr=0.202 | corr=-0.128 | reversed |
| ERP_change_no と area_km2 | corr=0.315 | corr=-0.107 | reversed |
| ERP_change_no と population_density_2025 | corr=-0.246 | corr=0.231 | reversed |
| net_overseas_migration と population_density_2025 | corr=-0.238 | corr=0.476 | reversed |
| ERP_change_pct と area_km2 | corr=0.719 | corr=-0.126 | reversed |
| natural_increase と net_internal_migration | corr=-0.199 | corr=0.096 | reversed |
| natural_increase と area_km2 | corr=0.161 | corr=-0.085 | reversed |
| natural_increase と population_density_2025 | corr=-0.179 | corr=0.244 | reversed |
| ERP_2024 と population_density_2025 | corr=-0.245 | corr=0.318 | reversed |
| ERP_2024 と area_km2 | corr=0.200 | corr=-0.128 | reversed |
| net_overseas_migration と area_km2 | corr=0.216 | corr=-0.103 | reversed |
| ERP_2025 と population_density_2025 | corr=-0.245 | corr=0.317 | reversed |

</details>

---

## 2026-07-20: フランス（id=114〜191） 所得・貧困率・世帯構成に関する13変数の総当たり相関

データ元: INSEE「Dossier complet」(id=2011101)から抽出した県(département)単位 n=98 とコミューン(commune)単位 n=34,804 の所得・貧困関連指標。13個の数値変数の全組み合わせ78通りのうち、符号が逆転またはおおむね30%以上変化したものは以下50通り。

- **分類の内訳**: reversed 5件、magnitude_change 45件、similar 28件（詳細全件は`results/summary_table.csv`のid=114〜191）。
- **傾向**: 符号自体が逆転する例は少ない（5件）が、大きさが変化する例(magnitude_change)が全体の6割近くと非常に多い。特に「所得の低い層（第1十分位）の所得水準」と「所得構成の割合（賃金・年金・社会給付・税など）」の組み合わせで、県単位よりコミューン単位のほうが相関がずっと強く出る傾向が目立つ（例: 第1十分位所得と課税世帯割合の相関は県単位+0.452→コミューン単位+0.808）。これは、県という広域単位では都市と農村・裕福な地域と貧しい地域が混ざって平均化されてしまい、コミューン単位まで細分化して初めて所得構成の違いがはっきり見える例と考えられる。符号が逆転した5件はいずれも「年金の割合」または「社会給付の割合」が絡む変数で、値そのものは弱い相関(|r|<0.25)同士の逆転である。

<details><summary>該当ペア一覧（クリックで展開）</summary>

| 変数の組み合わせ | 粗い単位の相関 | 細かい単位の相関 | 分類 |
|---|---|---|---|
| num_persons_fiscal_households と median_living_standard_eur | corr=0.459 | corr=0.007 | magnitude_change |
| d1_living_standard_eur と share_taxed_households_pct | corr=0.452 | corr=0.808 | magnitude_change |
| d1_living_standard_eur と share_activity_income_pct | corr=0.111 | corr=0.491 | magnitude_change |
| d1_living_standard_eur と share_wages_pct | corr=0.171 | corr=0.485 | magnitude_change |
| d1_living_standard_eur と share_direct_taxes_pct | corr=-0.080 | corr=-0.563 | magnitude_change |
| d9_living_standard_eur と poverty_rate_pct_60med | corr=-0.193 | corr=-0.440 | magnitude_change |
| d9_living_standard_eur と share_activity_income_pct | corr=0.735 | corr=0.408 | magnitude_change |
| d9_living_standard_eur と share_wages_pct | corr=0.693 | corr=0.368 | magnitude_change |
| d9_living_standard_eur と share_pensions_pct | corr=-0.648 | corr=-0.281 | magnitude_change |
| interdecile_ratio_d9_d1 と share_taxed_households_pct | corr=0.434 | corr=0.032 | magnitude_change |
| d1_living_standard_eur と d9_living_standard_eur | corr=0.133 | corr=0.511 | magnitude_change |
| interdecile_ratio_d9_d1 と share_activity_income_pct | corr=0.621 | corr=0.044 | magnitude_change |
| interdecile_ratio_d9_d1 と share_pensions_pct | corr=-0.675 | corr=-0.145 | magnitude_change |
| interdecile_ratio_d9_d1 と share_direct_taxes_pct | corr=-0.776 | corr=-0.397 | magnitude_change |
| poverty_rate_pct_60med と share_activity_income_pct | corr=-0.114 | corr=-0.373 | magnitude_change |
| poverty_rate_pct_60med と share_wages_pct | corr=-0.174 | corr=-0.367 | magnitude_change |
| poverty_rate_pct_60med と share_direct_taxes_pct | corr=0.181 | corr=0.502 | magnitude_change |
| share_taxed_households_pct と share_pensions_pct | corr=-0.538 | corr=-0.309 | magnitude_change |
| share_activity_income_pct と share_social_benefits_pct | corr=-0.198 | corr=-0.338 | magnitude_change |
| share_activity_income_pct と share_direct_taxes_pct | corr=-0.770 | corr=-0.503 | magnitude_change |
| share_wages_pct と share_direct_taxes_pct | corr=-0.722 | corr=-0.444 | magnitude_change |
| interdecile_ratio_d9_d1 と share_wages_pct | corr=0.548 | corr=0.006 | magnitude_change |
| median_living_standard_eur と interdecile_ratio_d9_d1 | corr=0.484 | corr=0.290 | magnitude_change |
| median_living_standard_eur と share_pensions_pct | corr=-0.458 | corr=-0.318 | magnitude_change |
| num_households と median_living_standard_eur | corr=0.485 | corr=0.004 | magnitude_change |
| num_persons_fiscal_households と d1_living_standard_eur | corr=-0.053 | corr=-0.164 | magnitude_change |
| num_persons_fiscal_households と d9_living_standard_eur | corr=0.550 | corr=0.065 | magnitude_change |
| num_persons_fiscal_households と interdecile_ratio_d9_d1 | corr=0.537 | corr=0.241 | magnitude_change |
| num_persons_fiscal_households と poverty_rate_pct_60med | corr=0.026 | corr=0.145 | magnitude_change |
| num_persons_fiscal_households と share_taxed_households_pct | corr=0.562 | corr=-0.009 | magnitude_change |
| num_persons_fiscal_households と share_activity_income_pct | corr=0.697 | corr=0.064 | magnitude_change |
| num_persons_fiscal_households と share_wages_pct | corr=0.685 | corr=0.053 | magnitude_change |
| num_persons_fiscal_households と share_pensions_pct | corr=-0.697 | corr=-0.093 | magnitude_change |
| num_persons_fiscal_households と share_direct_taxes_pct | corr=-0.638 | corr=-0.104 | magnitude_change |
| median_living_standard_eur と d1_living_standard_eur | corr=0.548 | corr=0.788 | magnitude_change |
| share_pensions_pct と share_direct_taxes_pct | corr=0.629 | corr=0.249 | magnitude_change |
| num_households と d9_living_standard_eur | corr=0.577 | corr=0.063 | magnitude_change |
| num_households と interdecile_ratio_d9_d1 | corr=0.557 | corr=0.232 | magnitude_change |
| num_households と poverty_rate_pct_60med | corr=0.001 | corr=0.133 | magnitude_change |
| num_households と share_taxed_households_pct | corr=0.562 | corr=-0.011 | magnitude_change |
| num_households と share_activity_income_pct | corr=0.666 | corr=0.047 | magnitude_change |
| num_households と share_wages_pct | corr=0.648 | corr=0.035 | magnitude_change |
| num_households と share_pensions_pct | corr=-0.660 | corr=-0.071 | magnitude_change |
| num_households と share_direct_taxes_pct | corr=-0.660 | corr=-0.100 | magnitude_change |
| num_households と d1_living_standard_eur | corr=-0.041 | corr=-0.156 | magnitude_change |
| num_persons_fiscal_households と share_social_benefits_pct | corr=-0.066 | corr=0.113 | reversed |
| poverty_rate_pct_60med と share_pensions_pct | corr=-0.151 | corr=0.079 | reversed |
| d1_living_standard_eur と share_pensions_pct | corr=0.121 | corr=-0.230 | reversed |
| num_households と share_social_benefits_pct | corr=-0.104 | corr=0.100 | reversed |
| share_pensions_pct と share_social_benefits_pct | corr=-0.071 | corr=0.076 | reversed |

</details>
## 2026-07-20: オーストラリアの個人所得に関する2つの相関（id=12）

- **変数(a)**: 所得を得た人の数（earners、人口規模の目安） と 平均所得（mean income）の相関係数（2022-23年度）
- **州・準州単位（8件）**: 相関係数 +0.040（ほぼ無相関）
- **SA2単位（2,346件）**: 相関係数 +0.151（弱いプラスの相関）
- **分類**: 符号は同じ（プラス）だが、大きさが変化（+0.040 → +0.151）。ただしどちらも0に近い弱い相関である点に注意。

- **変数(b)**: 平均所得（mean income） と ジニ係数（Gini coefficient、所得格差の指標）の相関係数（2022-23年度）
- **州・準州単位（8件）**: 相関係数 -0.069（ごく弱いマイナスの相関）
- **SA2単位（2,346件）**: 相関係数 +0.377（弱〜中程度のプラスの相関）
- **分類**: 符号がマイナスからプラスへ逆転。州単位では「平均所得が高い州ほど格差がわずかに小さい」ように見えるが、SA2単位まで細かく見ると「平均所得が高い地区ほど格差も大きい」という関係が現れる。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-20（12回目：id=12 オーストラリア・個人所得）」の項、要約統計量は `results/summaries/id12_australia_personal_income_2022_23.csv` を参照。

---

## 2026-07-21: ドイツの総人口と男性割合の相関（id=13）

- **変数**: 総人口 と 男性の割合（％、男女別人口から算出した派生変数）の相関係数（2025年12月31日時点）
- **州(Bundesland)単位（16件）**: 相関係数 +0.357（弱いプラスの相関）
- **市町村(Gemeinde)単位（10,659件）**: 相関係数 -0.110（弱いマイナスの相関）
- **分類**: 符号がプラスからマイナスへ逆転。州単位では「人口の多い州ほど男性割合がわずかに高い」ように見えるが、市町村単位まで細かく見ると、人口が数人〜数十人しかない小さな村で男女比が偶然大きく偏る（最大86.7%〜最小32.6%）ため、逆に人口の少ない村ほど男性割合が極端になりやすく、関係が逆転する。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（13回目：id=13 ドイツ・人口（性別内訳））」の項、要約統計量は `results/summaries/id13_germany_population_sex.csv` を参照。

---

## 2026-07-21: ドイツの平均年齢のばらつき（id=14）

- **変数**: 平均年齢（歳、2025年12月31日時点）の地域ごとのばらつき（標準偏差・範囲）
- **州(Bundesland)単位（16件）**: 平均45.54歳、標準偏差2.01ポイント、範囲6.1ポイント（最小42.3歳ハンブルク〜最大48.4歳ザクセン・アンハルト）
- **市町村(Gemeinde)単位（10,659件）**: 平均46.55歳、標準偏差2.72ポイント、範囲28.0ポイント（最小33.4歳ラウツェンハウゼン〜最大61.4歳ヴェルシェンバッハ）
- **分類**: 相関の符号逆転ではなく、大きさの変化（magnitude_change）。範囲で見ると州単位の約4.6倍に広がる。州単位では多様な市町村の平均が取られるため極端な値が打ち消し合うが、市町村単位まで細かく見ると、人口が数十人〜数百人しかない小さな村（高齢化が進んだ農村や、大学・軍施設のある若い村など）の極端な平均年齢がそのまま表に出てくる。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（14回目：id=14 ドイツ・平均年齢）」の項、要約統計量は `results/summaries/id14_germany_average_age.csv` を参照。

---

## 2026-07-21: EUの人口と人口増加率の相関（id=15）

- **変数**: 2018年時点の人口 と 2018年→2023年の人口増加率（％）の相関係数
- **NUTS2単位（292地域）**: 相関係数 +0.101（ほぼ無相関〜ごく弱いプラス）
- **NUTS3単位（1,374地域）**: 相関係数 +0.195（弱いプラスの相関）
- **分類**: 符号は同じ（プラス）だが、大きさが約93%（ほぼ2倍近く）変化。どちらも絶対値0.3未満の弱い相関だが、サンプル数が多い（292件・1,374件）ため統計的にも有意（片側t検定、有意水準5%）。粗いNUTS2単位では「人口の多い地域も少ない地域も、その後の増加率にはあまり差がない」ように見える一方、細かいNUTS3単位まで見ると「人口の多い地域の方がその後さらに増えやすい」という緩やかな傾向がやや見えやすくなる。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（15回目：id=18のstatus訂正、およびid=15 EU・人口）」の項、要約統計量は `results/summaries/id15_eu_population_growth.csv` を参照。

---
## 2026-07-21: フランスの総人口と一時滞在者比率の相関（id=16）

- **変数**: 総人口（population totale） と 一時滞在者比率（%、(population totale − population municipale) / population totale ×100。学生寮・軍施設・刑務所などでその地域に一時的にいる人の割合）の相関係数
- **県(Département)単位（100件）**: 相関係数 -0.668（中程度〜やや強いマイナスの相関）
- **コミューン(Commune)単位（34,964件）**: 相関係数 -0.044（ほぼ無相関）
- **分類**: 符号はどちらもマイナスのままだが、絶対値でおよそ93%縮小し、実質的に関係が消えた。県単位では「人口の多い県ほど一時滞在者比率が低い」というはっきりした関係が見えるが、これは多様なコミューンが混ざり合って平均化された結果。コミューン単位まで見ると、人口の小さな村でも大学寮や軍施設・刑務所が1つあるだけで比率が跳ね上がる（最大45.7%）ため、人口の大小との関係がほとんど見えなくなる。統計的にはどちらも有意（n=100、n=34,964とも十分大きいため）だが、コミューン単位の効果量は非常に小さい。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（16回目：id=16 フランス・人口）」の項、要約統計量は `results/summaries/id16_france_population.csv` を参照。

---

## 2026-07-21: フランスの出生数（規模）と2008→2024年増減率の相関（id=17）

- **変数**: 2024年の出生数（地域の規模の目安） と 2008年→2024年の出生数増減率（％）の相関係数
- **県(Département)単位（100件）**: 相関係数 +0.5385（中程度のプラスの相関）
- **コミューン(Commune)単位（31,078件、2008年出生数0件の3,770件は除外）**: 相関係数 +0.0117（ほぼ無相関）
- **分類**: 符号はどちらもプラスのままだが、約98%縮小し、実質的に関係が消えた。県単位では「もともと出生数が多い県ほど、その後の減少幅が緩やかだった」というはっきりした関係が見えるが、コミューン単位まで見ると、小さな村では出生数が数人単位のため年ごとの偶然のばらつきが大きく、規模と増減率の関係がほとんど見えなくなる。統計的にはどちらも有意（県:p=2.5×10⁻¹⁰、コミューン:p=0.039）だが、コミューン単位が有意なのはサンプル数が3万件超と非常に多いためで、相関係数自体は実質ゼロに近い（サンプル数が多いほど小さな相関でも「有意」と出やすいことの好例）。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（17回目：id=17 フランス・出生数）」の項、要約統計量は `results/summaries/id17_france_births_growth.csv` を参照。

---

## 2026-07-21: アメリカの失業率のばらつき（id=19）

- **変数**: 失業率（%）1つ（相関ではなく、単一変数のばらつき＝標準偏差・範囲の比較）
- **州単位（51件、50州+DC）**: 平均4.067%、標準偏差0.858ポイント、範囲4.0ポイント（2.1%〜6.1%）
- **郡単位（サンプル95件、各州の郡コード001・003番の系統的サンプル。BLS APIの無登録時25系列/リクエスト制限のため全郡(3,000超)は取得していない）**: 平均3.959%、標準偏差1.408ポイント、範囲8.2ポイント（1.6%〜9.8%）
- **分類**: 符号の逆転ではなく「magnitude_change」。範囲が州単位の約2.05倍、標準偏差が約1.6倍に拡大。平均はほぼ変わらないが、地域ごとの差の大きさが集計単位を細かくすると大きく広がる、id=14（ドイツ・平均年齢）と同じパターン。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（18回目：id=19 アメリカ・失業率）」の項、要約統計量は `results/summaries/id19_usa_unemployment.csv` を参照。

---

---

## SSDSE total-combination analysis (Japan) - top statistically significant reversals

- 総人口（男） per1000pop(A110101_rate) vs 15～64歳人口（女） per1000pop(A130202_rate): todofuken(n=47) corr=0.292 -> shikuchoson(n=1740) corr=-0.09
- 総人口（男） per1000pop(A110101_rate) vs 死亡数 per1000pop(A4200_rate): todofuken(n=47) corr=-0.539 -> shikuchoson(n=1740) corr=0.178
- 総人口（男） per1000pop(A110101_rate) vs 小学校数 per1000pop(E2101_rate): todofuken(n=47) corr=-0.445 -> shikuchoson(n=1740) corr=0.171
- 総人口（男） per1000pop(A110101_rate) vs 小学校教員数 per1000pop(E2401_rate): todofuken(n=47) corr=-0.424 -> shikuchoson(n=1740) corr=0.19
- 総人口（男） per1000pop(A110101_rate) vs 中学校数 per1000pop(E3101_rate): todofuken(n=47) corr=-0.522 -> shikuchoson(n=1740) corr=0.22
- 総人口（男） per1000pop(A110101_rate) vs 中学校教員数 per1000pop(E3401_rate): todofuken(n=47) corr=-0.485 -> shikuchoson(n=1740) corr=0.221
- 総人口（男） per1000pop(A110101_rate) vs 高等学校数 per1000pop(E4101_rate): todofuken(n=47) corr=-0.467 -> shikuchoson(n=1740) corr=0.219
- 総人口（男） per1000pop(A110101_rate) vs 一般診療所数 per1000pop(I5102_rate): todofuken(n=47) corr=-0.524 -> shikuchoson(n=1740) corr=0.151
- 総人口（女） per1000pop(A110102_rate) vs 15～64歳人口（女） per1000pop(A130202_rate): todofuken(n=47) corr=-0.292 -> shikuchoson(n=1740) corr=0.09
- 総人口（女） per1000pop(A110102_rate) vs 死亡数 per1000pop(A4200_rate): todofuken(n=47) corr=0.543 -> shikuchoson(n=1740) corr=-0.178
- 総人口（女） per1000pop(A110102_rate) vs 小学校数 per1000pop(E2101_rate): todofuken(n=47) corr=0.445 -> shikuchoson(n=1740) corr=-0.171
- 総人口（女） per1000pop(A110102_rate) vs 小学校教員数 per1000pop(E2401_rate): todofuken(n=47) corr=0.411 -> shikuchoson(n=1740) corr=-0.19
- 総人口（女） per1000pop(A110102_rate) vs 中学校数 per1000pop(E3101_rate): todofuken(n=47) corr=0.528 -> shikuchoson(n=1740) corr=-0.22
- 総人口（女） per1000pop(A110102_rate) vs 中学校教員数 per1000pop(E3401_rate): todofuken(n=47) corr=0.483 -> shikuchoson(n=1740) corr=-0.221
- 総人口（女） per1000pop(A110102_rate) vs 高等学校数 per1000pop(E4101_rate): todofuken(n=47) corr=0.466 -> shikuchoson(n=1740) corr=-0.219
- 総人口（女） per1000pop(A110102_rate) vs 一般診療所数 per1000pop(I5102_rate): todofuken(n=47) corr=0.503 -> shikuchoson(n=1740) corr=-0.151
- 日本人人口（男） per1000pop(A110201_rate) vs 一般診療所数 per1000pop(I5102_rate): todofuken(n=47) corr=-0.601 -> shikuchoson(n=1740) corr=0.156
- 日本人人口（女） per1000pop(A110202_rate) vs 小学校数 per1000pop(E2101_rate): todofuken(n=47) corr=0.553 -> shikuchoson(n=1740) corr=-0.067
- 日本人人口（女） per1000pop(A110202_rate) vs 小学校教員数 per1000pop(E2401_rate): todofuken(n=47) corr=0.502 -> shikuchoson(n=1740) corr=-0.098
- 日本人人口（女） per1000pop(A110202_rate) vs 中学校数 per1000pop(E3101_rate): todofuken(n=47) corr=0.631 -> shikuchoson(n=1740) corr=-0.121

---

## 2026-07-21: アメリカのGDP水準とGDP増減率の相関（id=22、summary_table id=730）

- **変数**: 名目GDP（Current-dollar GDP、2024年） と 2014→2024年の増減率（%）の相関係数
- **州単位（51件、50州＋DC）**: 相関係数 +0.222（p=0.1175）。**有意水準5%では統計的に有意ではない**
- **郡単位（3,104件）**: 相関係数 +0.095（p=1.07×10⁻⁷）。こちらは極めて有意
- **分類**: 符号は同じ（プラス）で逆転はしていないが、大きさは+0.222→+0.095と相対的に約-57%縮小。加えて、粗い集計単位（州）の方がむしろ統計的に有意でなく、細かい集計単位（郡）だけがサンプル数の多さゆえに有意になるという、これまでの候補とは逆パターン（通常は粗い単位の方がはっきりした関係に見えがちだが、今回は違った）。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（22回目：id=22 アメリカ・GDP）」の項、要約統計量は `results/summaries/id22_usa_gdp_growth.csv` を参照。

---

## 2026-07-21: オーストラリアの失業率のばらつき（id=25、summary_table id=1178）

- **変数**: 失業率（Unemployment Rate、2026年3月分）の州・準州単位 vs SA4単位でのばらつき（標準偏差・範囲）
- **州・準州単位（8件）**: 平均4.39%、標準偏差0.35ポイント、範囲1.05ポイント（3.999%〜5.052%）
- **SA4単位（87件）**: 平均4.34%、標準偏差0.94ポイント、範囲4.30ポイント（2.675%〜6.970%）
- **分類**: 平均はほぼ同じだが、標準偏差は約2.71倍、範囲（レンジ）は約4.08倍に拡大。州単位だけを見ると失業率の地域差は小さく見えるが、SA4まで細分化すると地域間の差が大きく開いていることが分かる。id=19（アメリカの失業率、州vs郡）と同種のパターン。
- **注意点**: SA4データはABSのモデル推計値であり、州データ（労働力調査の原数値集計）とは算出方法が異なる。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（25回目：id=25 オーストラリア・失業率）」の項、要約統計量は `results/summaries/id25_australia_unemployment.csv` を参照。

---

## 2026-07-21: アメリカの教育水準（学士号以上の割合）の単純平均 vs 人口加重平均（id=26、summary_table id=2037）

- **変数**: 学士号以上の割合（ACS5・2022年、25歳以上人口比）の州単位 vs 郡単位でのばらつきと平均
- **州単位（51件、50州＋DC）**: 平均33.876%、標準偏差6.652ポイント、範囲39.925ポイント（22.711%〜62.636%）
- **郡単位（3,144件）**: 単純平均23.491%、標準偏差10.058ポイント（州単位の約1.51倍）、範囲78.871ポイント（州単位の約1.97倍）
- **注目点**: 郡データを人口で重み付けした平均は34.312%で、州データから計算した全国平均（34.312%）と完全に一致する。つまり郡の「単純平均」は実質的な全国水準より約10.4ポイントも低く出る。人口の少ない農村の郡が多数を占めるため、単純平均だと都市部の高い値が薄まってしまうことが原因。
- **分類**: 符号の逆転ではないが、集計方法（単純平均か人口加重平均か）によって数値の見え方が大きく変わる典型例のため、大きな注目点として記録。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（26回目：id=26 アメリカ・教育水準）」の項、要約統計量は `results/summaries/id26_usa_education_attainment.csv` を参照。

---

## 2026-07-21: アメリカの住宅価格中央値の単純平均 vs 人口加重平均（id=27、summary_table id=2038）

- **変数**: 住宅価格中央値（ACS5・2022年、B25077_001E）の州単位 vs 郡単位でのばらつきと平均
- **州単位（51件、50州＋DC）**: 平均299,520ドル、標準偏差134,855ドル、範囲619,000ドル（145,800ドル〜764,800ドル）
- **郡単位（3,141件）**: 単純平均195,752ドル（州単位より約10万ドル低い）、標準偏差124,295ドル（州単位よりやや小さい）、範囲1,400,800ドル（州単位の約2.26倍）、変動係数(CV)は0.450→0.635に拡大
- **注目点**: 郡データを人口で重み付けした平均は350,420ドルで、郡の単純平均（195,752ドル）より約1.8倍高い。id=26（教育水準）と同種の「単純平均が農村部に引きずられて低く出る」パターンだが、中央値は加算できない統計量のため、id=26のように全国平均と厳密には一致しない近似値である点に注意。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（27回目：id=27 アメリカ・住宅価格中央値）」の項、要約統計量は `results/summaries/id27_usa_home_value.csv` を参照。

---

## 2026-07-21: イギリスの住宅価格中央値のばらつき（id=28、summary_table id=2385）

- **変数**: 住宅価格中央値（ONS HPSSA dataset 9、Year ending Mar 2023）の地域(Region/Country)単位 vs 地方自治体(Local Authority)単位でのばらつき
- **地域単位（10件）**: 平均279,300ポンド、中央値237,750ポンド、標準偏差116,014ポンド、範囲382,500ポンド（152,500ポンド〜535,000ポンド）
- **地方自治体単位（331件）**: 平均318,815ポンド、中央値295,000ポンド、標準偏差148,285ポンド（地域単位の約1.28倍）、範囲1,241,500ポンド（116,000ポンド〜1,357,500ポンド、地域単位の約3.25倍）、CV 0.415→0.465
- **分類**: 符号の逆転ではないが、範囲が約3.25倍に拡大。ロンドン中心部など極端に高い地方自治体の価格が、地域単位（「ロンドン」1つにまとめた平均）では見えなくなってしまう典型例。
- **詳細・データ元**: `results/aggregation_effect_log.md` の「2026-07-21（28回目：id=28 イギリス・住宅価格中央値）」の項、要約統計量は `results/summaries/id28_uk_house_price.csv` を参照。

---

## 2026-07-21: カナダの教育水準と世帯所得の関係の逆転（summary_table id=3587）

- **変数**: 「証明書・免許・学位を持たない人の割合（人口1000人あたり）」 vs 「世帯所得（総所得）の中央値」
- **州・準州単位（13件）**: corr=0.547（正の相関、有意でない）
- **国勢調査区単位（293件）**: corr=-0.298（負の相関、有意）
- **意味**: 州・準州という13個しかない粗い単位で見ると、学歴が低い人が多い州ほど所得が高いという弱い（かつ統計的に有意ではない）正の関係に見えます。しかし293の国勢調査区まで細かく見ると、学歴が低い人が多い地域ほど所得が低いという、より直感に合う負の関係が統計的に有意な形ではっきり現れます。
- **詳細・データ元**: `results/aggregation_effect_log.md`の「2026-07-21（新規データ源：カナダ 2021年国勢調査プロファイル）」の項を参照。データ元はStatistics Canada 2021 Census Profile（表98-401-X2021、登録不要）。

## 2026-07-21: カナダの婚姻状況と失業率の関係の逆転（summary_table id=3471）

- **変数**: 「未婚・事実婚でない人の割合（人口1000人あたり）」 vs 「失業率」
- **州・準州単位（13件）**: corr=-0.505（負の相関、有意でない）
- **国勢調査区単位（293件）**: corr=0.331（正の相関、有意）
- **意味**: 13個の州・準州単位ではサンプル数が少なく統計的に有意な関係を検出できませんが、293の国勢調査区まで細分化すると、未婚者の割合が高い地域ほど失業率も高いという正の関係が有意になります。
- **詳細・データ元**: `results/aggregation_effect_log.md`の「2026-07-21（新規データ源：カナダ 2021年国勢調査プロファイル）」の項を参照。

## 2026-07-21: カナダ Census Profile 351組み合わせの内訳（reversed/magnitude_change/similarすべて記録）

- **reversed（符号逆転）**: 72件 / **magnitude_change（大きさが大きく変化）**: 171件 / **similar（ほぼ同様）**: 108件（合計351件）
- 逆転や大きな変化のあるものだけでなく、`similar`と判定された全件も`results/summary_table.csv`（id=3421〜3771）に記録済みです。

---

## 2026-07-21: フィンランドの一人暮らし世帯比率と職住自足度の関係の逆転（summary_table id=4027）

- **変数**: 「一人暮らし世帯の割合（%）」 vs 「職住自足度（Workplace self-sufficiency、地域内求人数÷地域内就業者数）」
- **広域圏(maakunta)単位（19件）**: corr=-0.529（負の相関、有意）
- **市町村(kunta)単位（308件）**: corr=0.545（正の相関、有意）
- **意味**: 19個の広域圏単位で見ると「一人暮らし世帯が多い地域ほど職住自足度が低い」という負の関係に見えますが、308市町村まで細かく見ると、正反対の正の関係が有意に現れます。都心（一人暮らし世帯も雇用も集中）とベッドタウン（一人暮らしは少なく雇用は都心依存）を広域圏という1つの単位にまとめてしまうことで生じる逆転と考えられます。
- **詳細・データ元**: `results/aggregation_effect_log.md`の「2026-07-21（新規データ源：フィンランド Statistics Finland StatFin）」の項を参照。データ元はStatistics Finland StatFin PxWeb API（表142h、登録不要）。

## 2026-07-21: フィンランドの就業率と職住自足度の関係の逆転（summary_table id=4126）

- **変数**: 「20〜64歳の就業率（%）」 vs 「職住自足度」
- **広域圏単位（19件）**: corr=0.527（正の相関、有意）
- **市町村単位（308件）**: corr=-0.429（負の相関、有意）
- **詳細・データ元**: 同上。

## 2026-07-21: フィンランドStatFin 378組み合わせの内訳（reversed/magnitude_change/similarすべて記録）

- **reversed（符号逆転）**: 54件 / **magnitude_change（大きさが大きく変化）**: 197件 / **similar（ほぼ同様）**: 127件（合計378件）
- `similar`と判定された全件も`results/summary_table.csv`（id=3772〜4149）に記録済みです。

---

## 2026-07-21: ノルウェーの女性割合と移民割合の関係の逆転（summary_table id=4160）

- **変数**: 「女性の割合（人口1000人あたり）」 vs 「移民数（人口1000人あたり）」
- **県(fylke)単位（19件）**: corr=0.697（正の相関、有意）
- **市町村(kommune)単位（386件）**: corr=-0.117（負の相関、有意）
- **意味**: 19の県単位では「女性の割合が高い県ほど移民の割合も高い」という比較的強い正の関係に見えますが、386の市町村まで細かく見ると、弱いながらも統計的に有意な逆の関係が現れます。
- **注意**: 男性割合と女性割合はほぼ相補的な変数のため、他の変数との相関は符号が反転して対になって現れます。
- **詳細・データ元**: `results/aggregation_effect_log.md`の「2026-07-21（新規データ源：ノルウェー Statistics Norway (SSB) StatBank）」の項を参照。データ元はStatistics Norway StatBank PxWeb v2-beta API（表11818/11820、登録不要）。

## 2026-07-21: ノルウェーSSB 171組み合わせの内訳（reversed/magnitude_change/similarすべて記録）

- **reversed（符号逆転）**: 31件 / **magnitude_change（大きさが大きく変化）**: 128件 / **similar（ほぼ同様）**: 12件（合計171件）
- `similar`と判定された全件も`results/summary_table.csv`（id=4150〜4320）に記録済みです。

## 2026-07-21: スウェーデンSCB 66組み合わせの内訳（reversed/magnitude_change/similarすべて記録）

- **reversed（符号逆転）**: 5件 / **magnitude_change（大きさが大きく変化）**: 42件 / **similar（ほぼ同様）**: 19件（合計66件）
- 目立った例: 「労働力率 vs 高等教育の割合」が県単位corr=-0.518(有意)→市町村単位corr=-0.040(有意でない)に消失(magnitude_change)。「女性人口比率 vs 基礎教育以下の割合」が県単位corr=0.128(有意でない)→市町村単位corr=-0.376(有意)に符号逆転(reversed)。
- `similar`と判定された全件も`results/summary_table.csv`（id=4321〜4386）に記録済みです。

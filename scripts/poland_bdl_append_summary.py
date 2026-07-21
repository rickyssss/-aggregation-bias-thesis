import csv

NOTE = (
    "ポーランド中央統計局(GUS)のBank Danych Lokalnych(BDL、地方データバンク)API"
    "(https://bdl.stat.gov.pl/api/v1/、登録不要・APIキー不要、HTTP GETでJSON形式が返る)を使用。"
    "同じvariableId(統計指標ID)に対して`unit-level`パラメータ(2=voivodeship県、5=powiat郡、6=gmina市町村)を変えるだけで"
    "同一指標を異なる集計単位で取得できる、非常に効率の良いAPI構造だった。"
    "県(voivodeship、16単位)と郡(powiat、380単位)を粗い/細かい集計単位として選んだ。"
    "年は2024年(全変数で共通、平均賃金指標のみ2024年が最新)。"
    "変数は、人口(population_total、人)、人口1000人あたり純移動数(net_migration_per1000)、"
    "人口1000人あたり出生数(live_births_per1000)、人口1000人あたり死亡数(deaths_per1000)、"
    "人口1000人あたり自然増減数(natural_increase_per1000)、人口1000人あたり離婚件数(divorces_per1000、"
    "元データは人口1万人あたりの値だったため10で割って人口1000人あたりに変換。ただし相関係数は線形変換で不変のため結果に影響なし)、"
    "老年従属人口指数(old_age_dependency_ratio)、都市化率(urbanization_rate_pct、%)、"
    "全国平均に対する平均賃金の相対水準(avg_wage_pct_of_national、%)、12月時点の登録失業率(unemployment_rate_dec_pct、%)、"
    "出生1000人あたり乳児死亡数(infant_deaths_per1000_livebirths、郡単位で303件と欠測がやや多いが公表データをそのまま使用)の11指標。"
    "人口以外はすべて公式統計として比率・指数の形ですでに公表されているため、追加の人口1000人あたり変換は離婚件数のみで済んだ。"
    "11変数の総当たり55組を計算し、reversed(符号逆転)2件・magnitude_change(大きさの変化)33件・similar(ほぼ同様)20件で、"
    "逆転・非逆転を問わず全55件を記録した。"
    "有意性検定(両側t検定、p<0.05、自由度に応じた臨界値表を使用)も実施した(coarse_significant_p05/fine_significant_p05列)。"
    "詳細は results/summaries/id4727_4781_poland_bdl_pairwise.csv を参照。"
)

with open("results/poland_bdl_pairwise.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

with open("results/summary_table.csv", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    existing = list(reader)

last_id = int(existing[-1][0])
start_id = last_id + 1

new_rows = []
for i, r in enumerate(rows):
    new_id = start_id + i
    new_rows.append([
        str(new_id),
        "Poland",
        r["variable"],
        r["coarse_level"],
        r["coarse_stat"],
        r["fine_level"],
        r["fine_stat"],
        r["diff_type"],
        NOTE,
        r["coarse_sig"],
        r["fine_sig"],
    ])

with open("results/summary_table.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(header)
    w.writerows(existing)
    w.writerows(new_rows)

print("appended", len(new_rows), "rows, id", start_id, "to", start_id + len(new_rows) - 1)

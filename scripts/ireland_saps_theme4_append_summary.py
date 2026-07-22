import csv

NOTE = (
    "アイルランド中央統計局(CSO)のCensus 2022 Small Area Population Statistics (SAPS)のダウンロード用CSV"
    "(登録不要・APIキー不要、`https://www.cso.ie/en/media/csoie/census/census2022/SAPS_2022_county_270923.csv`"
    "(county、31単位)・`https://www.cso.ie/en/media/csoie/census/census2022/SAPS_2022_CSOED3270923.csv`"
    "(Electoral Division、3420単位))から、これまで未使用だったTheme 13(職業の社会階層分類、Table 1)の"
    "9変数を新たに抽出した: 管理職・上級職員、専門職、准専門職・技術職、事務・秘書職、技能職、"
    "介護・レジャー・その他サービス職、販売・カスタマーサービス職、機械操作職、単純作業職"
    "(いずれも男女計(T)の人数を、同表の職業総数(Not stated含む)を分母として1000人あたり比率に変換)。"
    "地理単位はcounty(county and city、31単位)とElectoral Division(3420単位)。"
    "総当たり36組を計算し、reversed(符号逆転)1件・magnitude_change(大きさの変化)31件・"
    "similar(ほぼ同様)4件で、逆転の有無にかかわらず全36件を記録した。"
    "有意性検定(両側t検定、p<0.05、自由度に応じた臨界値表を使用)も実施した"
    "(coarse_significant_p05/fine_significant_p05列)。"
    "データはdata/Ireland/ireland_saps_theme4_coarse_county.csv・ireland_saps_theme4_fine_ed.csvに保存。"
    "詳細は results/summaries/id<start>_<end>_ireland_saps_theme4_pairwise.csv を参照。"
)

SC = "/tmp/claude-0/-home-user--aggregation-bias-thesis/1251f782-d08b-591c-844d-b115f02b9db8/scratchpad/ireland"

with open(f"{SC}/saps_theme4_pairwise.csv", encoding="utf-8") as f:
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
        "Ireland",
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

end_id = start_id + len(new_rows) - 1

with open("results/summary_table.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, quoting=csv.QUOTE_ALL)
    w.writerow(header)
    w.writerows(existing)
    w.writerows(new_rows)

import shutil
shutil.copy(f"{SC}/saps_theme4_pairwise.csv", f"results/summaries/id{start_id}_{end_id}_ireland_saps_theme4_pairwise.csv")

print("appended", len(new_rows), "rows, id", start_id, "to", end_id)

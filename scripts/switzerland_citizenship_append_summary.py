import csv

NOTE = (
    "スイス連邦統計局(FSO/BFS)のPxWeb API"
    "(https://www.pxweb.bfs.admin.ch/api/v1/en/px-x-0102010000_101/px-x-0102010000_101.px、"
    "登録不要・APIキー不要、HTTP POSTでJSON-stat2形式が返る。既存のスイス人口構成データ(id=5272〜5547)と"
    "同じ地理次元「Kanton (-) / Bezirk (>>) / Gemeinde (......)」を持つ別の表"
    "「Permanent and non permanent resident population by Year, Canton/District/Commune, "
    "Population type, Citizenship (category), Sex and Age」を新たに使用し、"
    "国籍構成(スイス国籍/外国籍)と滞在資格(定住人口/非定住人口)を追加した。"
    "2024年の値を使用し、常住人口(定住+非定住)を分母として、"
    "スイス国籍・外国籍・非定住人口・外国籍男性・外国籍女性・スイス国籍男性・スイス国籍女性の"
    "合計7変数を人口1000人あたり比率に変換した。総当たり21組を計算し、"
    "reversed(符号逆転)0件・magnitude_change(大きさの変化)6件・similar(ほぼ同様)15件で、"
    "逆転の有無にかかわらず全21件を記録した。"
    "有意性検定(両側t検定、p<0.05、自由度に応じた臨界値表を使用)も実施した"
    "(coarse_significant_p05/fine_significant_p05列)。"
    "詳細は results/summaries/id<start>_<end>_switzerland_citizenship_pairwise.csv を参照。"
)

SC = "/tmp/claude-0/-home-user--aggregation-bias-thesis/72307f0c-a761-5e3f-b3e3-fbcf0fa7d5a4/scratchpad/switzerland"

with open(f"{SC}/citizenship_pairwise.csv", encoding="utf-8") as f:
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
        "Switzerland",
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
shutil.copy(f"{SC}/citizenship_pairwise.csv", f"results/summaries/id{start_id}_{end_id}_switzerland_citizenship_pairwise.csv")

print("appended", len(new_rows), "rows, id", start_id, "to", end_id)

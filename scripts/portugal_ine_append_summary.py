import csv

NOTE = (
    "ポルトガル国家統計院(INE, Instituto Nacional de Estatistica)の指標API"
    "(json_indicador、https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0008273&Dim1=S7A<年>&lang=EN、"
    "登録不要・APIキー不要、HTTP GETでJSON形式が返る)を使用。"
    "指標0008273「居住人口(性別・年齢層別)」を2015年・2021年について取得した。"
    "この1つの指標データの中に、地域コード(geocod)の桁数によって複数の集計単位(国全体=1桁、NUTS1=1桁、"
    "NUTS2=2桁、NUTS3=3桁、市区町村(concelho)=7桁)が混在していることを確認し、"
    "粗い集計単位としてNUTS3地域(25単位、本土23地域+アソーレス諸島+マデイラ諸島)、"
    "細かい集計単位として市区町村(concelho、308単位)を選んだ。"
    "NUTS2(7地域)は既存のEurostat NUTS2 vs NUTS3データと重複するため今回は使わず、"
    "より粒度差の大きいNUTS3 vs 市区町村の組み合わせを新規に追加した。"
    "この指標は性別(男/女/計)×年齢層(5歳階級、0-4歳〜80-84歳、85歳以上の18区分)×計、の交差集計になっているため、"
    "各地域の総人口を分母として、性別・各年齢階級を人口1000人あたり比率に変換し、"
    "さらに老年化指数(65歳以上人口の0-14歳人口1000人あたり比率)、年少人口指数、老年人口指数、従属人口指数、"
    "男女比(女性1000人あたり男性数)、2015→2021年人口増減率(人口1000人あたり)を算出した。"
    "人口の生カウント(population_2021)自体は相関計算に使わず、必ず比率・指数化した25変数のみを用いた。"
    "25変数の総当たり300組を計算し、reversed(符号逆転)3件・magnitude_change(大きさの変化)39件・"
    "similar(ほぼ同様)258件で、逆転・非逆転を問わず全300件を記録した。"
    "有意性検定(両側t検定、p<0.05、自由度に応じた臨界値表を使用)も実施した"
    "(coarse_significant_p05/fine_significant_p05列)。"
    "詳細は results/summaries/id4782_5081_portugal_ine_pairwise.csv を参照。"
)

with open("results/summaries/portugal_ine_pairwise_tmp.csv", encoding="utf-8") as f:
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
        "Portugal",
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

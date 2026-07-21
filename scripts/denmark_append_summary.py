import csv

NOTE = (
    "デンマーク統計局(Statistics Denmark)のStatBank API"
    "(https://api.statbank.dk/v1/data/INDKP101/JSONSTAT、登録不要、HTTP GET、JSON-stat形式)を使用。"
    "「INDKP101」表(所得統計、People by region, unit, sex, type of income)の1つの地理区分変数(OMRÅDE、110件)の中に、"
    "全国計(000)・県に相当する「province」11単位(粗い集計単位、コード01〜11)・"
    "市町村に相当する「kommune」98単位(細かい集計単位、3桁コード)が混在しているため、コードの桁数で振り分けた。"
    "年は2024年(両単位で最新かつ共通のデータ年)。"
    "1人あたり平均額(ENHED=116、'Average income for all people')の16指標(可処分所得・税引前所得・賃金所得・"
    "事業所得・公的移転所得・失業給付・生活保護・教育奨学金・児童手当・公的年金・障害老齢年金・私的年金・"
    "資本所得・受取利子・所得税・課税所得)はすでに1人あたり平均値として公表されているためそのまま使用し、"
    "各種所得受給者数(ENHED=101、'People with type of income'、人数)の10指標(事業所得・失業給付・生活保護・"
    "教育奨学金・児童手当・障害老齢年金・公務員年金・私的/労働市場年金・資本所得・住宅所有者向け土地税の各受給者数)は、"
    "同じ表内の可処分所得受給者数(ENHED=101、INDKOMSTTYPE=100、2024年全国計=4,951,378人)を人口の代理指標として、"
    "人口1000人あたり比率に変換してから相関を計算した"
    "(過去の教訓通り、人数カウントをそのまま使うと地域の大きさで自明にほぼ1.0の相関になってしまうため)。"
    "26変数の総当たり325組を計算し、reversed(符号逆転)27件・magnitude_change(大きさの変化)166件・"
    "similar(ほぼ同様)132件で、逆転や大幅変化の有無にかかわらず全325件を記録した。"
    "有意性検定(両側t検定、p<0.05、自由度に応じた臨界値表を使用)も実施した(coarse_significant_p05/fine_significant_p05列)。"
    "詳細は results/summaries/id4402_4726_denmark_statbank_pairwise.csv を参照。"
)

with open("results/denmark_statbank_pairwise.csv", encoding="utf-8") as f:
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
        "Denmark",
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

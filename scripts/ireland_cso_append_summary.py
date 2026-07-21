import csv

NOTE = (
    "アイルランド中央統計局(CSO)のPxStat JSON-RPC API"
    "(https://ws.cso.ie/public/api.jsonrpc/PxStat.Data.Cube_API.ReadDataset、"
    "登録不要・APIキー不要、HTTP POSTでJSON-stat2形式が返る。"
    "従来試していたREST版ReadCollection(/public/api.restful/...)は継続してHTTP 500だったが、"
    "個別表を直接指定するJSON-RPC版ReadDatasetは正常に応答することを新たに確認した)を使用。"
    "Census of Population 2022(2022年国勢調査)のProfile 2「住宅」テーマから、"
    "同一の住宅ストック区分(総住宅数/常住者が居住/来訪者のみ居住/一時不在(空き家)/"
    "空き家(住宅・アパート)/別荘・セカンドハウス/空き家率)を、"
    "粗い集計単位として県・市(County and City、表F2015、31単位のうち「State」全国計を除いた30単位、"
    "2022年・全世帯タイプ計)、細かい集計単位としてElectoral Division(選挙区、表F2095、3421単位)の"
    "両方で報告している珍しいペアを発見して使用した。"
    "総住宅数を分母として、常住者居住・来訪者のみ居住・一時不在・空き家(住宅)・別荘の5区分を"
    "人口1000戸あたり(正確には住宅1000戸あたり)比率に変換し、CSOが公表する空き家率(%)を"
    "そのまま加えた合計6変数を作成した。総当たり15組を計算し、"
    "reversed(符号逆転)0件・magnitude_change(大きさの変化)13件・similar(ほぼ同様)2件で、"
    "逆転の有無にかかわらず全15件を記録した。"
    "有意性検定(両側t検定、p<0.05、自由度に応じた臨界値表を使用)も実施した"
    "(coarse_significant_p05/fine_significant_p05列)。"
    "詳細は results/summaries/id<start>_<end>_ireland_cso_pairwise.csv を参照。"
)

SC = "/tmp/claude-0/-home-user--aggregation-bias-thesis/7cc672da-0a69-5dad-8b65-e6da035ec36a/scratchpad/ireland"

with open(f"{SC}/ireland_pairwise.csv", encoding="utf-8") as f:
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
shutil.copy(f"{SC}/ireland_pairwise.csv", f"results/summaries/id{start_id}_{end_id}_ireland_cso_pairwise.csv")

print("appended", len(new_rows), "rows, id", start_id, "to", end_id)

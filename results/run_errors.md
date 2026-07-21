
## 2026-07-21: スペインINE Atlas de distribución de renta、県表1件(table_id=30824)が取得失敗

- **状況**: 「最優先で試してほしい新しいデータ源」候補6（スペインINEbase）に着手。INEのwstempus JSON API（`https://servicios.ine.es/wstempus/js/EN/DATOS_TABLA/<table_id>`）で「Atlas de distribución de renta de los hogares」の県別municipio内訳表（53県表、table_id=30656〜31295）を順に取得中、`table_id=30824`（県順で2番目、Albacete=30656の次に位置する県）のみHTTP 200だが本文が`{"status" : "No puede mostrarse por restricciones de volumen"}`（データ量制限のため表示不可）というエラー応答だった。
- **試したこと**: `?date=20230101:20231231`パラメータを付けて再試行したが同じエラー。`TABLA/<id>`メタデータエンドポイントも空応答。
- **対応**: 残り52県表はすべて正常に取得できたため、この1県分のmunicipioデータを欠いたまま処理を続行した（自治州レベルには影響なし。全国8,131市区町村中、約数十〜百程度が欠落と推定されるが、fine側データ数は8,059〜8,137件で確保できているため統計的な影響は軽微と判断）。国名Spain、summary_table id=4387〜4401に記録済み。
- **今後の課題**: この県（おそらく人口の多い県）を後日、GRUPOS_TABLA/VALORES_GRUPOSTABLAメタデータAPIで地理階層（municipio/district/section）を先にフィルタしてから取得するなど、より細かいクエリで再取得できないか検討する。

## 2026-07-21: イタリアIstatData（候補5）は今回スキップ、接続不可

- **状況**: 「最優先で試してほしい新しいデータ源」候補5（イタリアIstatData/Istat SDMX API）を先に試したが、以下の通り接続できなかった。
  - `https://esploradati.istat.it/SDMXWS/rest/dataflow/IT1` および `.../IT1/all/latest`: タイムアウト（15〜20秒で応答なし）。
  - `https://sdmx.istat.it/SDMXWS/rest/dataflow/IT1`: HTTP 302リダイレクトの末、プレーンHTTPの`http://avvisi.istat.it/`（お知らせページ、おそらくメンテナンス通知）に転送され、プロキシがHTTPS以外のCONNECTトンネルを許可しないため取得不可（405エラー）。
  - `https://servizi.istat.it/SDMXWS/rest/dataflow`: プロキシのCONNECTトンネルが502で失敗。
- **対応**: 候補5は今回見送り、候補6（スペインINEbase）に進んだ。スペインのwstempus API（`servicios.ine.es`）は正常に接続できたため、そちらを優先して処理した。イタリアは次回以降、別のドメイン（`sdmx.istat.it`のリダイレクト解消待ちや、Eurostat経由でイタリアのNUTS3データを取得する代替案）を試すこと。

## 2026-07-21: アイルランドCSO・ドイツregionalstatistik・チェコČSÚを試したが接続失敗、ポルトガルINEに切り替えて成功

- **状況**: 候補1〜6(カナダ・フィンランド・ノルウェー・スウェーデン・イタリア・スペイン)がすべて処理済みだったため、候補7「新しい国・データ源を自分で探す」として、まずアイルランド・ドイツ・チェコを試した。
  - アイルランドCSO PxStat API（`https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadCollection/en`）: HTTP 500「InternalServerError」。`Accept: application/json`ヘッダを付けても同じ。
  - ドイツ regionalstatistik.de GENESIS-Online API（`https://www.regionalstatistik.de/genesisws/rest/2020/helloworld/logincheck?username=GAST&password=GAST`、ゲストアカウント）: HTTP 405 Method Not Allowed（GETでは呼べない可能性、POST等の別方式が必要と思われる）。
  - チェコ ČSÚ VDB API（`https://vdb.czso.cz/pll/eweb/package_show?id=130141-24`）: HTTP 200だが`{"success": false, "error": {"message": "Dataset Not Found"}}`（データセットIDが不正または存在しない）。
- **対応**: 3つとも今回は見送り、代わりにポルトガル国家統計院(INE)の指標API（`https://www.ine.pt/ine/json_indicador/pindica.jsp`）を試したところ正常に応答したため、そちらを採用した（NUTS3 vs 市区町村、詳細は`results/aggregation_effect_log.md`参照）。
- **今後の課題**: アイルランドは時間を置いて再試行（一時的なサーバー障害の可能性）、ドイツはGENESIS-OnlineのREST APIドキュメントを確認しPOSTリクエストや別のログイン方式を試す、チェコは正しいデータセットID(パッケージ名)をVDBのカタログ検索エンドポイントから探すこと。

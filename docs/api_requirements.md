# このリポジトリで使える外部APIについて（自動実行タスク向けメモ）

このファイルは、今後の自動実行（スケジュールされたタスク）がデータ取得の際に参考にするためのメモです。**APIキーやアプリケーションIDの値そのものはセキュリティ上の理由でこのリポジトリには一切記載しません。**

## e-Stat API（政府統計の総合窓口）

- 日本政府の統計データ（人口動態調査、社会・人口統計体系など）をJSON/XML/CSV形式で取得できる公式API（`https://api.e-stat.go.jp/rest/3.0/...`）です。
- 利用には無料のアプリケーションID（`appId`）の登録が必要ですが、**このリポジトリを運用しているルーティン（自動実行タスク）の指示文の中に、登録済みのアプリケーションIDが含まれています**。今後e-Stat由来のデータ（`queue/candidate_pairs.csv`内の`e-Stat`と書かれた候補など）を扱う自動実行タスクは、そのルーティンの指示文に記載されたappIdを使ってAPIを呼び出せます。
- このファイル自体にはID の値は書きません。値が必要な場合は、ルーティンの設定（スケジュールされたタスクの指示文）を参照してください。

### 使い方の要点（2026-07-21時点で確認済み）

- エンドポイント（JSON形式）: `https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData?appId=<ID>&statsDataId=<統計表ID>&metaGetFlg=Y`
- 公式マニュアル: `https://www.e-stat.go.jp/api/api-info/e-stat-manual3-0`
- e-Statの一般公開ページ（`https://www.e-stat.go.jp/dbview?sid=XXXXXXXXXX`）はJavaScriptで数値を描画するSPA形式のため、WebFetchやヘッドレスブラウザでは中身の数値を取得できないことがあります。その場合、**URLの`sid=`の値がそのままAPIの`statsDataId`として使える**ことを確認済みです（例: id=2・id=3の日本の出生数・課税対象所得データで実際に成功）。
- 都道府県別・市区町村別など、集計単位（地域階層）の違いは`metaGetFlg=Y`で取得できるメタ情報（`CLASS_INF`内の`area`クラスの`@level`）で判別できます。政令指定都市は表によって「区ごとに分割」されている場合と「市全体で1件」の場合があるため、地域コードの意味を必ず確認してから使うこと。
- 未登録の一般的なAPI利用制限（1日あたりのリクエスト数など）については公式マニュアルを参照してください。

## その他、これまでの自動実行タスクで確認済みの登録不要API

- Eurostat API（EU、`https://ec.europa.eu/eurostat/api/dissemination/...`）: 登録不要。
- BLS Public Data API v2（アメリカ、`https://api.bls.gov/publicAPI/v2/...`）: 登録不要だが、未登録時は1日25クエリ・1クエリ25系列までの制限あり。

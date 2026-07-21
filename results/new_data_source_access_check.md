# 新規データ源アクセス確認メモ

確認日: 2026-07-21 JST

このセッションでは公式ページへのWebアクセスで、無料・登録不要で使える見込みのデータ源を優先確認した。一方、ローカル実行環境からの `Invoke-WebRequest` / `curl.exe` / Node `fetch` は sandbox 側で拒否されたため、実データを保存して `summary_table.csv` に新規行として追記するところまでは完了できなかった。既存の生データ丸ごと追加はしていない。

## 優先候補

| データ源 | 確認結果 | 次に使うURL・メモ |
|---|---|---|
| CDC PLACES | 高優先。Data.CDC.gov/Socrataでcounty/place/tract/ZCTAのOpen Data/GIS-friendly形式を確認。登録不要のCSV/JSON exportとAPIがある。 | County GIS 2025: `https://data.cdc.gov/api/views/i46a-9kgh/rows.csv?accessType=DOWNLOAD`、Place GIS 2025: `https://data.cdc.gov/api/views/vgc8-iyc4/rows.csv?accessType=DOWNLOAD`、Tract GIS 2025: `https://data.cdc.gov/resource/yjkw-uj5s.csv`。粗い=county、細かい=placeまたはtractで、`totalpopulation` と `obesity_crudeprev` / `diabetes_crudeprev` / `csmoking_crudeprev` などの相関を作れる。 |
| EPA AirData | 高優先。annual AQIのcounty/CBSA ZIPが小さく、登録不要で直接ダウンロードできる。 | 2024 CBSA: `https://aqs.epa.gov/aqsweb/airdata/annual_aqi_by_cbsa_2024.zip`、2024 County: `https://aqs.epa.gov/aqsweb/airdata/annual_aqi_by_county_2024.zip`。粗い=CBSA、細かい=countyで `Median AQI`、`90th Percentile AQI`、`Max AQI` などを比較候補にする。 |
| BLS QCEW | 高優先。Open Data AccessでCSV slicesが公開され、最近5年分はAPI風URLで直接取得可能。 | 例: `https://data.bls.gov/cew/data/api/2024/a/industry/10.csv`。`own_code=0`、`industry_code=10`、州/郡の `annual_avg_emplvl`、`annual_avg_wkly_wage`、`avg_annual_pay` を使う。 |
| Eurostat City Statistics (`urb_`) | 利用候補。City statisticsのメタデータと `urb_cpop1` 等のテーブルを確認。無料オンライン公開。 | まず `urb_cpop1`、`urb_clma`、`urb_cenv` をSDMX/Eurostat APIで小さく取得し、都市/greater city/FUAの地理コード整理が必要。NUTS系よりコード体系の前処理が重いので、発表前の短時間作業ではCDC/EPA/BLSより後回し。 |
| GISCO LAU boundaries | 取得可能だが境界データなので単独では相関表に入らない。統計表とのjoin用。 | LAU 2024 file list: `https://gisco-services.ec.europa.eu/distribution/v2/lau/lau-2024-files.html`。GeoJSON/CSV/GPKG/SHP等がある。 |

## 後回し・注意

| データ源 | 判断 |
|---|---|
| BEA Regional API | API登録ページを確認。Regional datasetには州・郡GDP/所得/雇用があるが、APIキー登録フローがあるため、今回の新規取得優先度はBLS QCEWより下げた。なお既存repoにはBEA由来と見られる米国州/郡GDPデータが既に入っている。 |
| ブラジルFINBRA/DATASUS、メキシコCONEVAL、韓国KOSIS、ニュージーランドStats NZ、ドイツGENESIS | ユーザー指定どおり登録・手続きが重い候補として後回し。 |

## 次の最短手順

1. ネットワーク取得できる環境でCDC PLACES county/placeのGIS-friendly CSVを保存する。
2. `totalpopulation` と主要な健康指標のpairwise correlationをcounty vs placeで作る。
3. EPA AirData 2024 county/CBSA ZIPを展開し、AQI指標のpairwise correlationをcounty vs CBSAで作る。
4. 追加後に `scripts/multiple_testing_correction.ps1` を再実行し、BH補正件数を更新する。

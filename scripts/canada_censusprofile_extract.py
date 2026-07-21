import csv, json

COUNT_IDS = {
    "59": "married_or_commonlaw",
    "66": "not_married_not_commonlaw",
    "110": "one_person_households",
    "1415": "owner_households",
    "1416": "renter_households",
    "1529": "immigrants",
    "1528": "non_immigrants",
    "1999": "no_certificate_15plus",
    "2001": "postsecondary_cert_15plus",
    "2008": "bachelor_or_higher_15plus",
}
RATE_IDS = {
    "40": "median_age",
    "113": "median_total_income_recipients_2020",
    "115": "median_aftertax_income_recipients_2020",
    "243": "median_hh_total_income_2020",
    "244": "median_hh_aftertax_income_2020",
    "345": "lim_at_low_income_rate_pct",
    "360": "lico_at_low_income_rate_pct",
    "381": "gini_aftertax",
    "382": "p90_p10_ratio_aftertax",
    "1483": "owner_pct_with_mortgage",
    "1484": "owner_pct_30plus_shelter",
    "1486": "median_shelter_cost_owned",
    "1492": "tenant_pct_30plus_shelter",
    "1494": "median_shelter_cost_rented",
    "2228": "participation_rate",
    "2229": "employment_rate",
    "2230": "unemployment_rate",
}
POP_ID = "1"

ALL_IDS = set(COUNT_IDS) | set(RATE_IDS) | {POP_ID}

def extract(path, levels, outpath):
    data = {}  # dguid -> {geo_name, values: {id: val}}
    with open(path, encoding='latin-1') as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            if row[3] not in levels:
                continue
            cid = row[8]
            if cid not in ALL_IDS:
                continue
            dguid = row[1]
            geo_name = row[4]
            val_raw = row[11]
            try:
                val = float(val_raw)
            except ValueError:
                val = None
            if dguid not in data:
                data[dguid] = {"geo_name": geo_name, "values": {}}
            data[dguid]["values"][cid] = val
    with open(outpath, "w") as f:
        json.dump(data, f)
    print(path, "->", len(data), "geos")

extract("coarse_extract/98-401-X2021001_English_CSV_data.csv", {"Province","Territory"}, "coarse.json")
extract("fine_extract/98-401-X2021004_English_CSV_data.csv", {"Census division"}, "fine.json")

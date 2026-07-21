"""Fetch INE Portugal indicator 0008273 (resident population by NUTS/municipality,
sex, age group) for 2015 and 2021, and build coarse (NUTS3) / fine (municipality)
tables of population-structure ratios (per-1000 population) plus a 2015->2021
growth rate. No API key required; INE's json_indicador endpoint is public.
"""
import json
import urllib.request
import csv
import os

BASE = "https://www.ine.pt/ine/json_indicador/pindica.jsp"
VARCD = "0008273"
YEARS = ["2015", "2021"]

AGE_BANDS = [
    ("11", "0_4"), ("12", "5_9"), ("21", "10_14"), ("22", "15_19"),
    ("31", "20_24"), ("32", "25_29"), ("41", "30_34"), ("42", "35_39"),
    ("51", "40_44"), ("52", "45_49"), ("61", "50_54"), ("62", "55_59"),
    ("71", "60_64"), ("72", "65_69"), ("81", "70_74"), ("82", "75_79"),
    ("91", "80_84"), ("92", "85_plus"),
]

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "data", "Portugal")
os.makedirs(OUT_DIR, exist_ok=True)


def fetch_year(year):
    url = f"{BASE}?op=2&varcd={VARCD}&Dim1=S7A{year}&lang=EN"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    rows = data[0]["Dados"][year]
    return rows


def build_index(rows):
    # idx[geocod][sex][age] = int(valor)
    idx = {}
    names = {}
    for r in rows:
        g = r["geocod"]
        names[g] = r["geodsg"]
        idx.setdefault(g, {}).setdefault(r["dim_3"], {})[r["dim_4"]] = int(r["valor"])
    return idx, names


def main():
    rows_by_year = {y: fetch_year(y) for y in YEARS}
    idx2015, names2015 = build_index(rows_by_year["2015"])
    idx2021, names2021 = build_index(rows_by_year["2021"])

    for level_name, code_len, out_file in [
        ("NUTS3 (coarse)", 3, "coarse_nuts3.csv"),
        ("municipality (fine)", 7, "fine_municipality.csv"),
    ]:
        geos = sorted(g for g in names2021 if len(g) == code_len)
        out_rows = []
        for g in geos:
            d21 = idx2021.get(g, {})
            d15 = idx2015.get(g, {})
            total21 = d21.get("T", {}).get("T")
            total15 = d15.get("T", {}).get("T")
            male21 = d21.get("1", {}).get("T")
            female21 = d21.get("2", {}).get("T")
            if not total21 or total21 == 0 or not total15 or total15 == 0:
                continue
            if male21 is None or female21 is None:
                continue
            row = {
                "geocod": g,
                "geoname": names2021[g],
                "population_2021": total21,
                "sex_ratio_males_per_1000_females": round(male21 / female21 * 1000, 3) if female21 else "",
                "pct_female_per_1000": round(female21 / total21 * 1000, 3),
                "pop_growth_2015_2021_per_1000": round((total21 - total15) / total15 * 1000, 3),
            }
            age_vals = {}
            for code, label in AGE_BANDS:
                v = d21.get("T", {}).get(code)
                if v is None:
                    row = None
                    break
                age_vals[label] = v
                row[f"age_{label}_per_1000"] = round(v / total21 * 1000, 3)
            if row is None:
                continue
            pop0_14 = age_vals["0_4"] + age_vals["5_9"] + age_vals["10_14"]
            pop15_64 = (age_vals["15_19"] + age_vals["20_24"] + age_vals["25_29"] +
                        age_vals["30_34"] + age_vals["35_39"] + age_vals["40_44"] +
                        age_vals["45_49"] + age_vals["50_54"] + age_vals["55_59"] +
                        age_vals["60_64"])
            pop65_plus = (age_vals["65_69"] + age_vals["70_74"] + age_vals["75_79"] +
                          age_vals["80_84"] + age_vals["85_plus"])
            row["aging_index_65plus_per_1000_of_0to14"] = round(pop65_plus / pop0_14 * 1000, 3) if pop0_14 else ""
            row["youth_dependency_ratio_per_1000"] = round(pop0_14 / pop15_64 * 1000, 3) if pop15_64 else ""
            row["old_age_dependency_ratio_per_1000"] = round(pop65_plus / pop15_64 * 1000, 3) if pop15_64 else ""
            row["total_dependency_ratio_per_1000"] = round((pop0_14 + pop65_plus) / pop15_64 * 1000, 3) if pop15_64 else ""
            out_rows.append(row)

        out_path = os.path.join(OUT_DIR, out_file)
        if os.path.exists(out_path):
            raise SystemExit(f"refusing to overwrite existing file: {out_path}")
        fieldnames = list(out_rows[0].keys())
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(out_rows)
        print(f"{level_name}: wrote {len(out_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()

import csv, math, itertools
from collections import Counter

SC = "/tmp/claude-0/-home-user--aggregation-bias-thesis/0826eed1-4efb-5c04-a567-a5c7aebe7fcd/scratchpad/ireland"

# variable definitions: (output_name, numerator_cols(list, summed), denominator_col)
VARS = [
    ("one_person_household_per1000", ["T5_1OP_P"], "T5_1T_P"),
    ("one_parent_family_per1000", ["T5_1OPFC_P", "T5_1OPMC_P"], "T5_1T_P"),
    ("married_couple_with_children_per1000", ["T5_1MCC_P"], "T5_1T_P"),
    ("cohabiting_couple_with_children_per1000", ["T5_1CCC_P"], "T5_1T_P"),
    ("owned_outright_per1000", ["T6_3_OOP"], "T6_3_TP"),
    ("owned_with_mortgage_per1000", ["T6_3_OMLP"], "T6_3_TP"),
    ("rented_private_landlord_per1000", ["T6_3_RPLP"], "T6_3_TP"),
    ("rented_local_authority_per1000", ["T6_3_RLAP"], "T6_3_TP"),
    ("no_central_heating_per1000", ["T6_5_NCH"], "T6_5_T"),
    ("oil_heating_per1000", ["T6_5_OCH"], "T6_5_T"),
    ("natural_gas_heating_per1000", ["T6_5_NGCH"], "T6_5_T"),
    ("private_water_source_per1000", ["T6_6_GSP", "T6_6_OP"], "T6_6_T"),
    ("septic_tank_per1000", ["T6_7_IST"], "T6_7_T"),
    ("at_work_per1000", ["T8_1_WT"], "T8_1_TT"),
    ("unemployed_per1000", ["T8_1_STUT", "T8_1_LTUT"], "T8_1_TT"),
    ("retired_per1000", ["T8_1_RT"], "T8_1_TT"),
    ("looking_after_home_family_per1000", ["T8_1_LAHFT"], "T8_1_TT"),
    ("unable_to_work_disability_per1000", ["T8_1_UTWSDT"], "T8_1_TT"),
    ("professional_workers_per1000", ["T9_1_PWT"], "T9_1_TT"),
    ("unskilled_workers_per1000", ["T9_1_UST"], "T9_1_TT"),
    ("no_formal_education_per1000", ["T10_4_NFT"], "T10_4_TT"),
    ("upper_secondary_per1000", ["T10_4_UST"], "T10_4_TT"),
    ("bachelor_or_higher_per1000", ["T10_4_ODNDT", "T10_4_HDPQT", "T10_4_PDT", "T10_4_DT"], "T10_4_TT"),
]
VAR_NAMES = [v[0] for v in VARS]


COUNTY_NAMES = {
    "CW": "Carlow", "CN": "Cavan", "CE": "Clare", "CC": "Cork City", "CK": "Cork County",
    "DL": "Donegal", "DC": "Dublin City", "DR": "Dun Laoghaire-Rathdown", "FL": "Fingal",
    "GC": "Galway City", "GY": "Galway County", "KY": "Kerry", "KE": "Kildare",
    "KK": "Kilkenny", "LS": "Laois", "LM": "Leitrim", "LK": "Limerick", "LD": "Longford",
    "LH": "Louth", "MO": "Mayo", "MH": "Meath", "MN": "Monaghan", "OY": "Offaly",
    "RN": "Roscommon", "SO": "Sligo", "SD": "South Dublin", "TY": "Tipperary",
    "WD": "Waterford", "WH": "Westmeath", "WX": "Wexford", "WW": "Wicklow",
}


def load(path, exclude_geogid):
    rows = []
    with open(path, encoding="latin-1") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["GUID"] == exclude_geogid:
                continue
            geo_name = COUNTY_NAMES.get(row["GEOGID"], row["GEOGDESC"])
            rec = {"geo_code": row["GEOGID"], "geo_name": geo_name}
            ok = True
            for name, nums, den in VARS:
                try:
                    n = sum(float(row[c]) for c in nums)
                    d = float(row[den])
                except (ValueError, KeyError):
                    ok = False
                    break
                rec[name] = (n / d * 1000.0) if d > 0 else None
            if ok:
                rows.append(rec)
    return rows


coarse = load(f"{SC}/saps_county.csv", "IE0")
fine = load(f"{SC}/saps_ed.csv", "IE0")
assert len(coarse) not in (0,), "coarse empty"
print("coarse", len(coarse), "fine", len(fine))


def write_csv(rows, path):
    fields = ["geo_code", "geo_name"] + VAR_NAMES
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


write_csv(coarse, "/home/user/-aggregation-bias-thesis/data/Ireland/ireland_saps_theme2_coarse_county.csv")
write_csv(fine, "/home/user/-aggregation-bias-thesis/data/Ireland/ireland_saps_theme2_fine_ed.csv")


def correlation(xs, ys):
    n = len(xs)
    if n < 4:
        return None, n
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sx2 = sy2 = 0.0
    for x, y in zip(xs, ys):
        dx = x - mx
        dy = y - my
        sxy += dx * dy
        sx2 += dx * dx
        sy2 += dy * dy
    if sx2 == 0 or sy2 == 0:
        return None, n
    return sxy / math.sqrt(sx2 * sy2), n


T_TABLE = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306,
           9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
           16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074,
           23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045,
           30: 2.042}


def crit_t(df):
    if df <= 30:
        return T_TABLE[df]
    return 1.96 + (2.042 - 1.96) * max(0, (30.0 / df))


def test_sig(r, n):
    if r is None or n < 4:
        return "n/a"
    df = n - 2
    ar = abs(r)
    if ar >= 0.999999:
        return "yes"
    t = ar * math.sqrt(df / (1 - ar * ar))
    return "yes" if t >= crit_t(df) else "no"


def get_pairs(rows, v1, v2):
    xs, ys = [], []
    for r in rows:
        a, b = r[v1], r[v2]
        if a is None or b is None:
            continue
        xs.append(a)
        ys.append(b)
    return xs, ys


results = []
for v1, v2 in itertools.combinations(VAR_NAMES, 2):
    cx, cy = get_pairs(coarse, v1, v2)
    rC, nC = correlation(cx, cy)
    fx, fy = get_pairs(fine, v1, v2)
    rF, nF = correlation(fx, fy)
    if rC is None or rF is None:
        continue
    diff_type = "similar"
    if (rC > 0) != (rF > 0) and abs(rC) > 0.05 and abs(rF) > 0.05:
        diff_type = "reversed"
    elif abs(rC) > 0.001:
        rel = abs(abs(rC) - abs(rF)) / abs(rC)
        if rel > 0.3:
            diff_type = "magnitude_change"
    results.append({
        "variable": f"{v1} vs {v2}",
        "coarse_level": f"county(n={nC})",
        "coarse_stat": f"corr={round(rC, 3)}",
        "fine_level": f"electoral_division(n={nF})",
        "fine_stat": f"corr={round(rF, 3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC, nC),
        "fine_sig": test_sig(rF, nF),
    })

with open(f"{SC}/saps_theme2_pairwise.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["variable", "coarse_level", "coarse_stat", "fine_level",
                                       "fine_stat", "diff_type", "coarse_sig", "fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
print(Counter(r["diff_type"] for r in results))
for r in results:
    if r["diff_type"] == "reversed":
        print("REVERSED:", r)

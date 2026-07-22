import csv, math, itertools
from collections import Counter

SC = "/tmp/claude-0/-home-user--aggregation-bias-thesis/0826eed1-4efb-5c04-a567-a5c7aebe7fcd/scratchpad/ireland"

# variable definitions: (output_name, numerator_cols(list, summed), denominator_col)
VARS = [
    ("car_driver_to_work_per1000", ["T11_1_CDT"], "T11_1_TT"),
    ("work_from_home_per1000", ["T11_1_WMFHT"], "T11_1_TT"),
    ("public_transport_to_work_per1000", ["T11_1_BUT", "T11_1_TDLT"], "T11_1_TT"),
    ("walk_or_bike_to_work_per1000", ["T11_1_FT", "T11_1_BIT"], "T11_1_TT"),
    ("commute_over_1hr_per1000", ["T11_3_D5", "T11_3_D6"], "T11_3_T"),
    ("commute_under_15min_per1000", ["T11_3_D1"], "T11_3_T"),
    ("disability_per1000", ["T12_1_T"], "T12_3_TT"),
    ("carer_per1000", ["T12_2_T"], "T12_3_TT"),
    ("very_good_health_per1000", ["T12_3_VGT"], "T12_3_TT"),
    ("bad_or_very_bad_health_per1000", ["T12_3_BT", "T12_3_VBT"], "T12_3_TT"),
    ("smoker_per1000", ["T12_4_YES"], "T12_4_T"),
    ("agriculture_forestry_fishing_per1000", ["T14_1_AFFT"], "T14_1_TT"),
    ("building_construction_per1000", ["T14_1_BCT"], "T14_1_TT"),
    ("manufacturing_per1000", ["T14_1_MIT"], "T14_1_TT"),
    ("commerce_trade_per1000", ["T14_1_CTT"], "T14_1_TT"),
    ("public_administration_per1000", ["T14_1_PAT"], "T14_1_TT"),
    ("professional_services_per1000", ["T14_1_PST"], "T14_1_TT"),
    ("no_car_household_per1000", ["T15_1_NC"], "T15_1_TC"),
    ("multiple_car_household_per1000", ["T15_1_2C", "T15_1_3C", "T15_1_GE4C"], "T15_1_TC"),
    ("no_internet_per1000", ["T15_2_NO"], "T15_2_T"),
    ("broadband_per1000", ["T15_2_BB"], "T15_2_T"),
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


def load(path, exclude_guid):
    rows = []
    with open(path, encoding="latin-1") as f:
        r = csv.DictReader(f)
        for row in r:
            if row["GUID"] == exclude_guid:
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


write_csv(coarse, "/home/user/-aggregation-bias-thesis/data/Ireland/ireland_saps_theme3_coarse_county.csv")
write_csv(fine, "/home/user/-aggregation-bias-thesis/data/Ireland/ireland_saps_theme3_fine_ed.csv")


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

with open(f"{SC}/saps_theme3_pairwise.csv", "w", newline="", encoding="utf-8") as f:
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

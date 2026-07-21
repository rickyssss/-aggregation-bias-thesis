import csv
import math
import itertools
from collections import Counter

VAR_NAMES = [
    "sex_ratio_males_per_1000_females",
    "pct_female_per_1000",
    "pop_growth_2015_2021_per_1000",
    "age_0_4_per_1000", "age_5_9_per_1000", "age_10_14_per_1000",
    "age_15_19_per_1000", "age_20_24_per_1000", "age_25_29_per_1000",
    "age_30_34_per_1000", "age_35_39_per_1000", "age_40_44_per_1000",
    "age_45_49_per_1000", "age_50_54_per_1000", "age_55_59_per_1000",
    "age_60_64_per_1000", "age_65_69_per_1000", "age_70_74_per_1000",
    "age_75_79_per_1000", "age_80_84_per_1000", "age_85_plus_per_1000",
    "aging_index_65plus_per_1000_of_0to14",
    "youth_dependency_ratio_per_1000",
    "old_age_dependency_ratio_per_1000",
    "total_dependency_ratio_per_1000",
]


def load(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        rec = {"geo_code": r["geocod"], "geo_name": r["geoname"]}
        for v in VAR_NAMES:
            val = r.get(v)
            rec[v] = float(val) if val not in (None, "") else None
        out.append(rec)
    return out


coarse = load("data/Portugal/coarse_nuts3.csv")
fine = load("data/Portugal/fine_municipality.csv")


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


T_TABLE = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
           11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
           21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}


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
    xs = []
    ys = []
    for r in rows:
        a = r.get(v1)
        b = r.get(v2)
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
        "coarse_level": f"NUTS3(n={nC})",
        "coarse_stat": f"corr={round(rC, 3)}",
        "fine_level": f"municipality(n={nF})",
        "fine_stat": f"corr={round(rF, 3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC, nC),
        "fine_sig": test_sig(rF, nF),
    })

with open("results/summaries/portugal_ine_pairwise_tmp.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["variable", "coarse_level", "coarse_stat", "fine_level", "fine_stat", "diff_type", "coarse_sig", "fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
print(Counter(r["diff_type"] for r in results))

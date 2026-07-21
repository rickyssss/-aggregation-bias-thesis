import csv, math, itertools
from collections import Counter

VAR_NAMES = [
    "pct_married", "pct_single", "pct_widowed", "pct_divorced", "women_per1000",
    "mean_income_ksek", "median_income_ksek",
    "unemployment_rate", "labour_force_participation_rate", "employment_rate",
    "pct_tertiary_edu", "pct_basic_edu",
]

def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = []
        for row in r:
            o = {"geo_code": row["geo_code"], "geo_name": row["geo_name"]}
            for v in VAR_NAMES:
                val = row[v]
                o[v] = float(val) if val not in (None, "") else None
            rows.append(o)
        return rows

coarse = read_csv("sweden_scb_coarse_lan.csv")
fine = read_csv("sweden_scb_fine_kommun.csv")

def correlation(xs, ys):
    n = len(xs)
    if n < 4: return None, n
    mx = sum(xs)/n; my = sum(ys)/n
    sxy = sx2 = sy2 = 0.0
    for x, y in zip(xs, ys):
        dx = x-mx; dy = y-my
        sxy += dx*dy; sx2 += dx*dx; sy2 += dy*dy
    if sx2 == 0 or sy2 == 0: return None, n
    return sxy/math.sqrt(sx2*sy2), n

T_TABLE = {1:12.706,2:4.303,3:3.182,4:2.776,5:2.571,6:2.447,7:2.365,8:2.306,9:2.262,10:2.228,
11:2.201,12:2.179,13:2.160,14:2.145,15:2.131,16:2.120,17:2.110,18:2.101,19:2.093,20:2.086,
21:2.080,22:2.074,23:2.069,24:2.064,25:2.060,26:2.056,27:2.052,28:2.048,29:2.045,30:2.042}

def crit_t(df):
    if df <= 30: return T_TABLE[df]
    return 1.96 + (2.042-1.96)*max(0, (30.0/df))

def test_sig(r, n):
    if r is None or n < 4: return "n/a"
    df = n-2; ar = abs(r)
    if ar >= 0.999999: return "yes"
    t = ar*math.sqrt(df/(1-ar*ar))
    return "yes" if t >= crit_t(df) else "no"

def get_pairs(rows, v1, v2):
    xs = []; ys = []
    for r in rows:
        a = r[v1]; b = r[v2]
        if a is None or b is None: continue
        xs.append(a); ys.append(b)
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
        rel = abs(abs(rC)-abs(rF))/abs(rC)
        if rel > 0.3:
            diff_type = "magnitude_change"
    results.append({
        "variable": f"{v1} vs {v2}",
        "coarse_level": f"lan(n={nC})",
        "coarse_stat": f"corr={round(rC,3)}",
        "fine_level": f"kommun(n={nF})",
        "fine_stat": f"corr={round(rF,3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC, nC),
        "fine_sig": test_sig(rF, nF),
    })

with open("sweden_scb_pairwise.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["variable","coarse_level","coarse_stat","fine_level","fine_stat","diff_type","coarse_sig","fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
print(Counter(r["diff_type"] for r in results))

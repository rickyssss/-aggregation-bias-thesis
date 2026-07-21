import json, math, csv, itertools
from collections import Counter

SC = "/tmp/claude-0/-home-user--aggregation-bias-thesis/7cc672da-0a69-5dad-8b65-e6da035ec36a/scratchpad/ireland"

STOCK_CATS = [
    ("occupied_residents_per1000", "10"),
    ("occupied_visitors_per1000", "20"),
    ("vacant_temp_absent_per1000", "30"),
    ("vacant_house_apt_per1000", "400"),
    ("vacant_holiday_home_per1000", "60"),
]
VAR_NAMES = [n for n, _ in STOCK_CATS] + ["vacancy_rate_pct"]


def strides(sizes):
    s = [1] * len(sizes)
    for i in range(len(sizes) - 2, -1, -1):
        s[i] = s[i + 1] * sizes[i + 1]
    return s


def load(path):
    d = json.load(open(path))
    res = d["result"]
    dims = res["id"]
    idx = {}
    for dim in dims:
        raw = res["dimension"][dim]["category"]["index"]
        if isinstance(raw, list):
            idx[dim] = {code: i for i, code in enumerate(raw)}
        else:
            idx[dim] = raw
    labels = {dim: res["dimension"][dim]["category"]["label"] for dim in dims}
    sizes = res["size"]
    values = res["value"]
    strd = dict(zip(dims, strides(sizes)))
    return dims, idx, labels, values, strd


# --- County level: F2015 ---
dimsC, idxC, labelsC, valuesC, strdC = load(f"{SC}/F2015.json")
county_labels = labelsC["C04104V04868"]
year_idx = idxC["TLIST(A1)"]["2022"]
hh_idx = idxC["C02010V02440"]["-"]
stat_idx = idxC["STATISTIC"][list(idxC["STATISTIC"].keys())[0]]


def get_county(county_code, stock_code):
    pos = (
        stat_idx * strdC["STATISTIC"]
        + year_idx * strdC["TLIST(A1)"]
        + idxC["C04104V04868"][county_code] * strdC["C04104V04868"]
        + hh_idx * strdC["C02010V02440"]
        + idxC["C02758V03328"][stock_code] * strdC["C02758V03328"]
    )
    return valuesC[pos]


coarse = []
for code, name in county_labels.items():
    if code == "IE0":
        continue  # State total, not a county
    total = get_county(code, "-")
    if not total:
        continue
    rec = {"geo_code": code, "geo_name": name, "total_housing_stock": total}
    for varname, catcode in STOCK_CATS:
        v = get_county(code, catcode)
        rec[varname] = v / total * 1000.0 if v is not None else None
    rate = get_county(code, "70")
    rec["vacancy_rate_pct"] = rate
    coarse.append(rec)

# --- Electoral Division level: F2095 ---
dimsF, idxF, labelsF, valuesF, strdF = load(f"{SC}/F2095.json")
ed_labels = labelsF["C04167V04938"]
stat_idxF = idxF["STATISTIC"][list(idxF["STATISTIC"].keys())[0]]
year_idxF = list(idxF["TLIST(A1)"].values())[0]


def get_ed(ed_code, stock_code):
    pos = (
        stat_idxF * strdF["STATISTIC"]
        + year_idxF * strdF["TLIST(A1)"]
        + idxF["C02758V03328"][stock_code] * strdF["C02758V03328"]
        + idxF["C04167V04938"][ed_code] * strdF["C04167V04938"]
    )
    return valuesF[pos]


fine = []
for code, name in ed_labels.items():
    total = get_ed(code, "-")
    if not total:
        continue
    rec = {"geo_code": code, "geo_name": name, "total_housing_stock": total}
    for varname, catcode in STOCK_CATS:
        v = get_ed(code, catcode)
        rec[varname] = v / total * 1000.0 if v is not None else None
    rate = get_ed(code, "70")
    rec["vacancy_rate_pct"] = rate
    fine.append(rec)

print("coarse (county)", len(coarse), "fine (ED)", len(fine))


def write_csv(rows, path):
    fields = ["geo_code", "geo_name", "total_housing_stock"] + VAR_NAMES
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


write_csv(coarse, "data/Ireland/ireland_cso_coarse_county.csv")
write_csv(fine, "data/Ireland/ireland_cso_fine_electoraldivision.csv")


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

with open(f"{SC}/ireland_pairwise.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["variable", "coarse_level", "coarse_stat", "fine_level",
                                       "fine_stat", "diff_type", "coarse_sig", "fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
print(Counter(r["diff_type"] for r in results))

import json, math, csv, itertools
from collections import Counter

SC = "/tmp/claude-0/-home-user--aggregation-bias-thesis/af856f1c-ebda-556e-89ed-5c421996b0e2/scratchpad"

# 5-year-ish age bins built from single-year ages (0-109, "-1"=total/all ages)
AGE_BINS = [
    ("0_14", range(0, 15)),
    ("15_64", range(15, 65)),
    ("65plus", range(65, 110)),
    ("0_4", range(0, 5)),
    ("5_9", range(5, 10)),
    ("10_14", range(10, 15)),
    ("15_19", range(15, 20)),
    ("20_29", range(20, 30)),
    ("30_44", range(30, 45)),
    ("45_64", range(45, 65)),
    ("65_74", range(65, 75)),
    ("75_84", range(75, 85)),
    ("85plus", range(85, 110)),
]


def load_jsonstat(path):
    d = json.load(open(path))
    dims = d["id"]
    idx = {dim: d["dimension"][dim]["category"]["index"] for dim in dims}
    labels = {dim: d["dimension"][dim]["category"]["label"] for dim in dims}
    sizes = d["size"]
    values = d["value"]

    def strides(sizes):
        s = [1] * len(sizes)
        for i in range(len(sizes) - 2, -1, -1):
            s[i] = s[i + 1] * sizes[i + 1]
        return s

    strd = strides(sizes)

    def get(geo, age, year, kyn):
        gi = idx["Landshlutar" if "Landshlutar" in idx else "Sveitarfélag"][geo]
        ai = idx["Aldur"][age]
        yi = idx["Ár"][year]
        ki = idx["Kyn"][kyn]
        pos = gi * strd[0] + ai * strd[1] + yi * strd[2] + ki * strd[3]
        return values[pos]

    geo_dim = "Landshlutar" if "Landshlutar" in idx else "Sveitarfélag"
    geo_codes = [c for c in idx[geo_dim].keys()]
    year = list(idx["Ár"].keys())[0]
    return idx, labels, get, geo_dim, geo_codes, year


def build_table(path):
    idx, labels, get, geo_dim, geo_codes, year = load_jsonstat(path)
    rows = []
    for gcode in geo_codes:
        total = get(gcode, "-1", year, "0")
        if total is None or total <= 0:
            continue
        male = get(gcode, "-1", year, "1")
        female = get(gcode, "-1", year, "2")
        rec = {
            "geo_code": gcode,
            "geo_name": labels[geo_dim][gcode],
            "population": total,
        }
        bin_counts = {}
        for name, ages in AGE_BINS:
            s = 0
            for a in ages:
                v = get(gcode, str(a), year, "0")
                if v is not None:
                    s += v
            bin_counts[name] = s
            rec[f"{name}_per1000"] = s / total * 1000.0
        rec["male_per1000"] = male / total * 1000.0 if male is not None else None
        rec["female_per1000"] = female / total * 1000.0 if female is not None else None
        rec["sex_ratio_males_per1000_females"] = (
            male / female * 1000.0 if male is not None and female else None
        )
        p15_64 = bin_counts["15_64"]
        p0_14 = bin_counts["0_14"]
        p65plus = bin_counts["65plus"]
        if p15_64 > 0:
            rec["youth_dependency_ratio_per_1000"] = p0_14 / p15_64 * 1000.0
            rec["old_age_dependency_ratio_per_1000"] = p65plus / p15_64 * 1000.0
            rec["total_dependency_ratio_per_1000"] = (p0_14 + p65plus) / p15_64 * 1000.0
        else:
            rec["youth_dependency_ratio_per_1000"] = None
            rec["old_age_dependency_ratio_per_1000"] = None
            rec["total_dependency_ratio_per_1000"] = None
        rec["aging_index_65plus_per_1000_of_0to14"] = (
            p65plus / p0_14 * 1000.0 if p0_14 > 0 else None
        )
        rows.append(rec)
    return rows


VAR_NAMES = (
    [f"{name}_per1000" for name, _ in AGE_BINS]
    + [
        "male_per1000",
        "female_per1000",
        "sex_ratio_males_per1000_females",
        "youth_dependency_ratio_per_1000",
        "old_age_dependency_ratio_per_1000",
        "total_dependency_ratio_per_1000",
        "aging_index_65plus_per_1000_of_0to14",
    ]
)

coarse = build_table(f"{SC}/region_data.json")
fine = build_table(f"{SC}/muni_data.json")
print("coarse", len(coarse), "fine", len(fine))


def write_csv(rows, path):
    fields = ["geo_code", "geo_name", "population"] + VAR_NAMES
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


write_csv(coarse, "data/Iceland/iceland_hagstofa_coarse_landshluti.csv")
write_csv(fine, "data/Iceland/iceland_hagstofa_fine_sveitarfelag.csv")


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
    xs = []
    ys = []
    for r in rows:
        a = r[v1]
        b = r[v2]
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
        "coarse_level": f"landshluti(n={nC})",
        "coarse_stat": f"corr={round(rC, 3)}",
        "fine_level": f"sveitarfelag(n={nF})",
        "fine_stat": f"corr={round(rF, 3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC, nC),
        "fine_sig": test_sig(rF, nF),
    })

with open(f"{SC}/iceland_pairwise.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["variable", "coarse_level", "coarse_stat", "fine_level",
                                       "fine_stat", "diff_type", "coarse_sig", "fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
print(Counter(r["diff_type"] for r in results))

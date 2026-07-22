import json, math, csv, itertools
from collections import Counter

SC = "/tmp/claude-0/-home-user--aggregation-bias-thesis/77038021-8067-5230-9801-39ea9cdbb3fa/scratchpad/switzerland"

GEO_CODE = "Kanton (-) / Bezirk (>>) / Gemeinde (......)"


def strides(sizes):
    s = [1] * len(sizes)
    for i in range(len(sizes) - 2, -1, -1):
        s[i] = s[i + 1] * sizes[i + 1]
    return s


def load_jsonstat(path):
    d = json.load(open(path))
    dims = d["id"]
    idx = {dim: d["dimension"][dim]["category"]["index"] for dim in dims}
    labels = {dim: d["dimension"][dim]["category"]["label"] for dim in dims}
    sizes = d["size"]
    values = d["value"]
    strd = strides(sizes)

    def get(geo, birthplace="-99999", sex="-99999"):
        yi = 0
        gi = idx[GEO_CODE][geo]
        bti = 0  # Bevölkerungstyp fixed to '1' (permanent resident population), only value queried
        bpi = idx["Geburtsort"][birthplace]
        si = idx["Geschlecht"][sex]
        zi = 0  # Zivilstand fixed to '-99999' (total), only value queried
        pos = yi * strd[0] + gi * strd[1] + bti * strd[2] + bpi * strd[3] + si * strd[4] + zi * strd[5]
        return values[pos]

    geo_codes = list(idx[GEO_CODE].keys())
    return idx, labels, get, geo_codes


geo_meta = json.load(open(f"{SC}/geo_codes_birthplace.json"))
cantons = set(geo_meta["cantons"])
communes = set(geo_meta["communes"])

idxA, labelsA, getA, geo_codes = load_jsonstat(f"{SC}/result_birthplace.json")

VAR_NAMES = [
    "born_switzerland_per1000",
    "born_abroad_per1000",
    "born_switzerland_male_per1000",
    "born_switzerland_female_per1000",
    "born_abroad_male_per1000",
    "born_abroad_female_per1000",
]


def build_table(geo_set):
    rows = []
    for gcode in geo_codes:
        if gcode not in geo_set:
            continue
        total = getA(gcode)
        if total is None or total <= 0:
            continue
        rec = {
            "geo_code": gcode,
            "geo_name": labelsA[GEO_CODE][gcode],
            "population": total,
        }
        born_ch = getA(gcode, birthplace="1")
        born_ab = getA(gcode, birthplace="2")
        born_ch_m = getA(gcode, birthplace="1", sex="1")
        born_ch_f = getA(gcode, birthplace="1", sex="2")
        born_ab_m = getA(gcode, birthplace="2", sex="1")
        born_ab_f = getA(gcode, birthplace="2", sex="2")
        rec["born_switzerland_per1000"] = born_ch / total * 1000.0 if born_ch is not None else None
        rec["born_abroad_per1000"] = born_ab / total * 1000.0 if born_ab is not None else None
        rec["born_switzerland_male_per1000"] = born_ch_m / total * 1000.0 if born_ch_m is not None else None
        rec["born_switzerland_female_per1000"] = born_ch_f / total * 1000.0 if born_ch_f is not None else None
        rec["born_abroad_male_per1000"] = born_ab_m / total * 1000.0 if born_ab_m is not None else None
        rec["born_abroad_female_per1000"] = born_ab_f / total * 1000.0 if born_ab_f is not None else None
        rows.append(rec)
    return rows


coarse = build_table(cantons)
fine = build_table(communes)
print("coarse", len(coarse), "fine", len(fine))


def write_csv(rows, path):
    fields = ["geo_code", "geo_name", "population"] + VAR_NAMES
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


write_csv(coarse, "data/Switzerland/switzerland_bfs_birthplace_coarse_canton.csv")
write_csv(fine, "data/Switzerland/switzerland_bfs_birthplace_fine_commune.csv")


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
        "coarse_level": f"canton(n={nC})",
        "coarse_stat": f"corr={round(rC, 3)}",
        "fine_level": f"commune(n={nF})",
        "fine_stat": f"corr={round(rF, 3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC, nC),
        "fine_sig": test_sig(rF, nF),
    })

with open(f"{SC}/birthplace_pairwise.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["variable", "coarse_level", "coarse_stat", "fine_level",
                                       "fine_stat", "diff_type", "coarse_sig", "fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
print(Counter(r["diff_type"] for r in results))

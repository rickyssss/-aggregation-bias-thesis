import csv, math, itertools, json, os
from collections import defaultdict, Counter

RAW = "/tmp/claude-0/-home-user--aggregation-bias-thesis/98889ef9-74db-5de1-a5b9-f63f6e587bbd/scratchpad/eurostat_pjanind3_raw.csv"
REPO = "/home/user/-aggregation-bias-thesis"
OUT = "/tmp/claude-0/-home-user--aggregation-bias-thesis/98889ef9-74db-5de1-a5b9-f63f6e587bbd/scratchpad/out"
os.makedirs(OUT, exist_ok=True)

INDICATORS = ["DEPRATIO1", "OLDDEP1", "YOUNGDEP1", "MEDAGEPOP", "PC_FM", "PC_Y0_14", "PC_Y65_MAX", "PC_Y80_MAX"]
VAR_NAMES = {
    "DEPRATIO1": "total_dependency_ratio_per1000",
    "OLDDEP1": "old_age_dependency_ratio_per1000",
    "YOUNGDEP1": "youth_dependency_ratio_per1000",
    "MEDAGEPOP": "median_age_years",
    "PC_FM": "females_per1000_males",
    "PC_Y0_14": "young_0_14_per1000",
    "PC_Y65_MAX": "elderly_65plus_per1000",
    "PC_Y80_MAX": "oldest_80plus_per1000",
}
VARS = list(VAR_NAMES.values())

COUNTRIES = {
    "AT": ("Austria", "2025"),
    "BE": ("Belgium", "2025"),
    "BG": ("Bulgaria", "2025"),
    "CZ": ("Czechia", "2025"),
    "DE": ("Germany", "2025"),
    "EL": ("Greece", "2025"),
    "HR": ("Croatia", "2025"),
    "HU": ("Hungary", "2025"),
    "RO": ("Romania", "2025"),
    "RS": ("Serbia", "2025"),
    "SK": ("Slovakia", "2025"),
    "TR": ("Turkey", "2025"),
    "ES": ("Spain", "2025"),
}

# geo -> country -> year -> glen -> indic -> value
data = defaultdict(lambda: defaultdict(dict))  # key (country,year,glen) -> geo -> {indic: val}

with open(RAW, newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        geo = row["geo"]
        country = geo[:2]
        if country not in COUNTRIES:
            continue
        indic = row["indic_de"]
        if indic not in INDICATORS:
            continue
        if row["TIME_PERIOD"] != COUNTRIES[country][1]:
            continue
        glen = len(geo)
        if glen not in (4, 5):
            continue
        if row["OBS_VALUE"] == "":
            continue
        try:
            v = float(row["OBS_VALUE"])
        except ValueError:
            continue
        data[(country, glen)].setdefault(geo, {})[indic] = v

def build_table(country, glen):
    rows = []
    for geo, vals in data.get((country, glen), {}).items():
        if len(vals) < len(INDICATORS):
            continue
        rec = {"geo": geo}
        for indic in INDICATORS:
            raw = vals[indic]
            name = VAR_NAMES[indic]
            rec[name] = raw if indic == "MEDAGEPOP" else raw * 10.0
        rows.append(rec)
    return rows

def correlation(xs, ys):
    n = len(xs)
    if n < 4:
        return None, n
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sx2 = sy2 = 0.0
    for x, y in zip(xs, ys):
        dx = x - mx; dy = y - my
        sxy += dx * dy; sx2 += dx * dx; sy2 += dy * dy
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
        xs.append(a); ys.append(b)
    return xs, ys

FIELDS = ["geo"] + VARS

def write_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for rr in rows:
            w.writerow(rr)

summary = {}
for cc, (name, year) in COUNTRIES.items():
    coarse = build_table(cc, 4)
    fine = build_table(cc, 5)
    if len(coarse) < 4 or len(fine) < 4:
        print(cc, name, "SKIP insufficient units", len(coarse), len(fine))
        continue
    write_csv(coarse, f"{OUT}/{name.lower()}_eurostat_demography_coarse_nuts2.csv")
    write_csv(fine, f"{OUT}/{name.lower()}_eurostat_demography_fine_nuts3.csv")

    results = []
    for v1, v2 in itertools.combinations(VARS, 2):
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
            "coarse_level": f"nuts2(n={nC})",
            "coarse_stat": f"corr={round(rC,3)}",
            "fine_level": f"nuts3(n={nF})",
            "fine_stat": f"corr={round(rF,3)}",
            "diff_type": diff_type,
            "coarse_sig": test_sig(rC, nC),
            "fine_sig": test_sig(rF, nF),
        })
    summary[cc] = {"name": name, "year": year, "n_coarse": len(coarse), "n_fine": len(fine), "results": results}
    print(cc, name, "coarse:", len(coarse), "fine:", len(fine), "pairs:", len(results), Counter(x["diff_type"] for x in results))

with open(f"{OUT}/summary.json", "w") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print("DONE")

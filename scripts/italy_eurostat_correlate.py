import csv, math, itertools
from collections import Counter

REPO = "/home/user/-aggregation-bias-thesis"
RAW = f"{REPO}/data/Italy/italy_eurostat_demo_r_pjanind3_raw.csv"

# Eurostat demo_r_pjanind3: NUTS2/NUTS3 population structure indicators.
# Indicators picked (all already ratios/rates/medians, not raw counts):
#   DEPRATIO1  = total age-dependency ratio ((0-14 + 65+) / 15-64), %
#   OLDDEP1    = old-age dependency ratio (65+ / 15-64), %
#   YOUNGDEP1  = young-age dependency ratio (0-14 / 15-64), %
#   MEDAGEPOP  = median age of population, years
#   PC_FM      = females per 100 males
#   PC_Y0_14   = share of population aged 0-14, %
#   PC_Y65_MAX = share of population aged 65+, %
#   PC_Y80_MAX = share of population aged 80+, %
INDICATORS = ["DEPRATIO1", "OLDDEP1", "YOUNGDEP1", "MEDAGEPOP", "PC_FM", "PC_Y0_14", "PC_Y65_MAX", "PC_Y80_MAX"]

# Rename to *_per1000 for the percent-based ones (x10), keep median age and PC_FM(per1000 males) explicit.
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
YEAR = "2025"

data = {}  # geo -> {indic: value}
with open(RAW, newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        geo = row["geo"]
        if not geo.startswith("IT"):
            continue
        if row["TIME_PERIOD"] != YEAR:
            continue
        indic = row["indic_de"]
        if indic not in INDICATORS:
            continue
        try:
            v = float(row["OBS_VALUE"])
        except ValueError:
            continue
        data.setdefault(geo, {})[indic] = v


def build_table(geo_len):
    rows = []
    for geo, vals in data.items():
        if len(geo) != geo_len:
            continue
        if len(vals) < len(INDICATORS):
            continue
        rec = {"geo": geo}
        for indic in INDICATORS:
            raw = vals[indic]
            name = VAR_NAMES[indic]
            if indic == "MEDAGEPOP":
                rec[name] = raw
            else:
                rec[name] = raw * 10.0  # percent -> per-1000
        rows.append(rec)
    return rows


coarse = build_table(4)  # NUTS2 = regione
fine = build_table(5)    # NUTS3 = provincia
print("coarse (NUTS2/regione):", len(coarse))
print("fine (NUTS3/provincia):", len(fine))

FIELDS = ["geo"] + list(VAR_NAMES.values())


def write_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


write_csv(coarse, f"{REPO}/data/Italy/italy_eurostat_demography_coarse_nuts2.csv")
write_csv(fine, f"{REPO}/data/Italy/italy_eurostat_demography_fine_nuts3.csv")


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


VARS = list(VAR_NAMES.values())
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
        "coarse_level": f"regione_nuts2(n={nC})",
        "coarse_stat": f"corr={round(rC, 3)}",
        "fine_level": f"provincia_nuts3(n={nF})",
        "fine_stat": f"corr={round(rF, 3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC, nC),
        "fine_sig": test_sig(rF, nF),
    })

SUMMARY_PATH = f"{REPO}/results/summaries/italy_eurostat_demography_pairwise_TMP.csv"
with open(SUMMARY_PATH, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["variable", "coarse_level", "coarse_stat", "fine_level",
                                       "fine_stat", "diff_type", "coarse_sig", "fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
print(Counter(r["diff_type"] for r in results))
for row in results:
    print(row["variable"], "|", row["coarse_stat"], row["coarse_sig"], "|", row["fine_stat"], row["fine_sig"], "|", row["diff_type"])

import json, math, csv, itertools

AVG_TYPES = {
    "100": "avg_disposable_income",
    "105": "avg_pretax_income",
    "115": "avg_wage_income",
    "120": "avg_entrepreneurial_income",
    "130": "avg_public_transfer_income",
    "140": "avg_unemployment_benefits",
    "150": "avg_cash_benefits",
    "170": "avg_educational_grants",
    "180": "avg_child_benefits",
    "190": "avg_public_pension",
    "200": "avg_disability_oldage_pension",
    "205": "avg_private_pension",
    "225": "avg_capital_income",
    "230": "avg_interest_received",
    "260": "avg_income_tax",
    "290": "avg_taxable_income",
}
COUNT_TYPES = {
    "120": "entrepreneurial_income_recipients_per1000",
    "140": "unemployment_benefit_recipients_per1000",
    "150": "cash_benefit_recipients_per1000",
    "170": "educational_grant_recipients_per1000",
    "180": "child_benefit_recipients_per1000",
    "200": "disability_oldage_pension_recipients_per1000",
    "210": "public_servants_pension_recipients_per1000",
    "220": "private_pension_recipients_per1000",
    "225": "capital_income_recipients_per1000",
    "280": "land_tax_homeowner_recipients_per1000",
}
POP_TYPE = "100"  # people with disposable income, used as population denominator

VAR_NAMES = list(AVG_TYPES.values()) + list(COUNT_TYPES.values())


def load_jsonstat(path):
    with open(path) as f:
        d = json.load(f)
    ds = d["dataset"]
    geo_dim = ds["dimension"]["OMRÅDE"]["category"]
    type_dim = ds["dimension"]["INDKOMSTTYPE"]["category"]
    geo_codes = sorted(geo_dim["index"], key=lambda k: geo_dim["index"][k])
    type_codes = sorted(type_dim["index"], key=lambda k: type_dim["index"][k])
    geo_labels = geo_dim["label"]
    n_geo = len(geo_codes)
    n_type = len(type_codes)
    values = ds["value"]
    rows = {}
    for gi, gcode in enumerate(geo_codes):
        rec = {}
        for ti, tcode in enumerate(type_codes):
            rec[tcode] = values[gi * n_type + ti]
        rows[gcode] = {"geo_name": geo_labels[gcode], "types": rec}
    return rows


avg_rows = load_jsonstat("/tmp/dk_raw/avg.json")
count_rows = load_jsonstat("/tmp/dk_raw/counts.json")

# geography split: "000" = all Denmark (excluded), 2-digit codes = province (coarse),
# 3-digit codes = municipality/kommune (fine)
all_codes = set(avg_rows.keys()) | set(count_rows.keys())


def classify(code):
    if code == "000":
        return None
    if len(code) == 2:
        return "coarse"
    if len(code) == 3:
        return "fine"
    return None


def build_table(level):
    out = []
    for code in all_codes:
        if classify(code) != level:
            continue
        avg_types = avg_rows.get(code, {}).get("types", {})
        cnt_types = count_rows.get(code, {}).get("types", {})
        pop = cnt_types.get(POP_TYPE)
        if pop is None or pop <= 0:
            continue
        name = avg_rows.get(code, count_rows.get(code, {})).get("geo_name", code)
        o = {"geo_code": code, "geo_name": name}
        for tcode, varname in AVG_TYPES.items():
            o[varname] = avg_types.get(tcode)
        for tcode, varname in COUNT_TYPES.items():
            v = cnt_types.get(tcode)
            o[varname] = (v / pop * 1000.0) if v is not None else None
        out.append(o)
    return out


coarse = build_table("coarse")
fine = build_table("fine")
print("coarse", len(coarse), "fine", len(fine))


def write_csv(rows, path):
    fields = ["geo_code", "geo_name"] + VAR_NAMES
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)


write_csv(coarse, "data/Denmark/denmark_statbank_coarse_province.csv")
write_csv(fine, "data/Denmark/denmark_statbank_fine_kommune.csv")


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
        "coarse_level": f"province(n={nC})",
        "coarse_stat": f"corr={round(rC,3)}",
        "fine_level": f"kommune(n={nF})",
        "fine_stat": f"corr={round(rF,3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC, nC),
        "fine_sig": test_sig(rF, nF),
    })

with open("results/denmark_statbank_pairwise.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["variable", "coarse_level", "coarse_stat", "fine_level", "fine_stat", "diff_type", "coarse_sig", "fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
from collections import Counter
print(Counter(r["diff_type"] for r in results))

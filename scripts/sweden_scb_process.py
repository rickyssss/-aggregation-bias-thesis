import json, itertools, math, csv

def load(path):
    d = json.load(open(path))
    ids = d["id"]
    sizes = d["size"]
    dims = {}
    for did in ids:
        cat = d["dimension"][did]["category"]
        codes = sorted(cat["index"], key=lambda k: cat["index"][k])
        dims[did] = codes
    values = d["value"]
    records = []
    ranges = [range(s) for s in sizes]
    for idx_tuple in itertools.product(*ranges):
        flat = 0
        for i, sz in zip(idx_tuple, sizes):
            flat = flat * sz + i
        # recompute properly below
    # proper flatten: row-major with ids order, first dim slowest
    n = len(ids)
    total = 1
    for s in sizes:
        total *= s
    for flat_idx in range(total):
        rem = flat_idx
        idx = [0]*n
        for pos in range(n-1, -1, -1):
            idx[pos] = rem % sizes[pos]
            rem //= sizes[pos]
        rec = {}
        for pos, did in enumerate(ids):
            rec[did] = dims[did][idx[pos]]
        rec["value"] = values[flat_idx]
        records.append(rec)
    return records

def region_name_map(path):
    d = json.load(open(path))
    cat = d["dimension"]["Region"]["category"]
    return cat["label"]

# ---- Marital status -> pct_married, pct_single, pct_widowed, pct_divorced, women_per1000 ----
def build_marital(path):
    recs = load(path)
    names = region_name_map(path)
    agg = {}
    for r in recs:
        reg = r["Region"]
        civ = r["Civilstand"]
        v = r["value"]
        if v is None:
            continue
        agg.setdefault(reg, {}).setdefault(civ, 0)
        agg[reg][civ] += v
    out = {}
    for reg, civs in agg.items():
        total = sum(civs.values())
        if total <= 0:
            continue
        out[reg] = {
            "geo_name": names.get(reg, reg),
            "pct_married": civs.get("G", 0) / total * 100,
            "pct_single": civs.get("OG", 0) / total * 100,
            "pct_widowed": civs.get("ÄNKL", 0) / total * 100,
            "pct_divorced": civs.get("SK", 0) / total * 100,
            "population_total": total,
        }
    return out

def build_marital_sex(path):
    # separately compute women_per1000 using sex dimension
    recs = load(path)
    agg = {}
    for r in recs:
        reg = r["Region"]; sex = r["Kon"]; v = r["value"]
        if v is None: continue
        agg.setdefault(reg, {}).setdefault(sex, 0)
        agg[reg][sex] += v
    out = {}
    for reg, sx in agg.items():
        total = sx.get("1", 0) + sx.get("2", 0)
        if total <= 0: continue
        out[reg] = sx.get("2", 0) / total * 1000.0
    return out

# ---- Income ----
def build_income(path):
    recs = load(path)
    out = {}
    for r in recs:
        reg = r["Region"]
        cc = r["ContentsCode"]
        v = r["value"]
        out.setdefault(reg, {})
        if cc == "000001OR":
            out[reg]["mean_income_ksek"] = v
        elif cc == "000001ON":
            out[reg]["median_income_ksek"] = v
    return out

# ---- Labour market ----
def build_labour(path):
    recs = load(path)
    out = {}
    for r in recs:
        reg = r["Region"]
        cc = r["ContentsCode"]
        v = r["value"]
        out.setdefault(reg, {})
        if cc == "000002NN":
            out[reg]["unemployment_rate"] = v
        elif cc == "000002NK":
            out[reg]["labour_force_participation_rate"] = v
        elif cc == "000002NS":
            out[reg]["employment_rate"] = v
    return out

# ---- Education ----
def build_edu(path):
    recs = load(path)
    agg = {}
    for r in recs:
        reg = r["Region"]
        lvl = r["UtbildningsNiva"]
        v = r["value"]
        if v is None:
            continue
        agg.setdefault(reg, {}).setdefault(lvl, 0)
        agg[reg][lvl] += v
    out = {}
    for reg, lv in agg.items():
        total = sum(lv.values())
        if total <= 0:
            continue
        tertiary = lv.get("5", 0) + lv.get("6", 0) + lv.get("7", 0)
        basic = lv.get("1", 0) + lv.get("2", 0)
        out[reg] = {
            "pct_tertiary_edu": tertiary / total * 100,
            "pct_basic_edu": basic / total * 100,
        }
    return out

VAR_NAMES = [
    "pct_married", "pct_single", "pct_widowed", "pct_divorced", "women_per1000",
    "mean_income_ksek", "median_income_ksek",
    "unemployment_rate", "labour_force_participation_rate", "employment_rate",
    "pct_tertiary_edu", "pct_basic_edu",
]

def build_level(prefix):
    marital = build_marital(f"raw_pop_{prefix}.json")
    women = build_marital_sex(f"raw_pop_{prefix}.json")
    income = build_income(f"raw_inc_{prefix}.json")
    labour = build_labour(f"raw_lab_{prefix}.json")
    edu = build_edu(f"raw_edu_{prefix}.json")
    all_regions = set(marital) | set(income) | set(labour) | set(edu)
    rows = []
    for reg in sorted(all_regions):
        row = {"geo_code": reg, "geo_name": marital.get(reg, {}).get("geo_name", reg)}
        row["pct_married"] = marital.get(reg, {}).get("pct_married")
        row["pct_single"] = marital.get(reg, {}).get("pct_single")
        row["pct_widowed"] = marital.get(reg, {}).get("pct_widowed")
        row["pct_divorced"] = marital.get(reg, {}).get("pct_divorced")
        row["women_per1000"] = women.get(reg)
        row["mean_income_ksek"] = income.get(reg, {}).get("mean_income_ksek")
        row["median_income_ksek"] = income.get(reg, {}).get("median_income_ksek")
        row["unemployment_rate"] = labour.get(reg, {}).get("unemployment_rate")
        row["labour_force_participation_rate"] = labour.get(reg, {}).get("labour_force_participation_rate")
        row["employment_rate"] = labour.get(reg, {}).get("employment_rate")
        row["pct_tertiary_edu"] = edu.get(reg, {}).get("pct_tertiary_edu")
        row["pct_basic_edu"] = edu.get(reg, {}).get("pct_basic_edu")
        rows.append(row)
    return rows

coarse = build_level("county")
fine = build_level("muni")
print("coarse", len(coarse), "fine", len(fine))

def write_csv(rows, path):
    fields = ["geo_code", "geo_name"] + VAR_NAMES
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

write_csv(coarse, "sweden_scb_coarse_lan.csv")
write_csv(fine, "sweden_scb_fine_kommun.csv")

# sanity print a couple rows
for r in coarse[:3]:
    print(r)
for r in fine[:3]:
    print(r)

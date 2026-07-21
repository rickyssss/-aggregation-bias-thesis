import json, csv, math, itertools
from collections import Counter

d = json.load(open("/tmp/claude-0/-home-user--aggregation-bias-thesis/47afdfda-2d25-5b41-9315-0f4e0f766487/scratchpad/poland_raw/all_vars.json"))

VARS = ["population_total","net_migration_per1000","live_births_per1000","deaths_per1000",
        "natural_increase_per1000","divorces_per10k","old_age_dependency_ratio",
        "urbanization_rate_pct","avg_wage_pct_of_national","unemployment_rate_dec_pct",
        "infant_deaths_per1000_livebirths"]

YEAR = "2024"

def extract(level):
    table = {}
    for name in VARS:
        for row in d[name][level]:
            code = row["id"]
            geoname = row["name"]
            val = None
            for v in row["values"]:
                if v["year"] == YEAR and v.get("attrId") == 1:
                    val = v["val"]
                    break
            if code not in table:
                table[code] = {"geo_code": code, "geo_name": geoname}
            table[code][name] = val
    return list(table.values())

coarse = extract("coarse")
fine = extract("fine")

# rename divorces_per10k -> divorces_per1000 by dividing by 10 for consistent per-1000 units
for rows in (coarse, fine):
    for r in rows:
        v = r.pop("divorces_per10k", None)
        r["divorces_per1000"] = (v / 10.0) if v is not None else None

VAR_NAMES = [v if v != "divorces_per10k" else "divorces_per1000" for v in VARS]

def write_csv(rows, path):
    fields = ["geo_code", "geo_name"] + VAR_NAMES
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

write_csv(coarse, "data/Poland/poland_bdl_coarse_voivodeship.csv")
write_csv(fine, "data/Poland/poland_bdl_fine_powiat.csv")
print("coarse", len(coarse), "fine", len(fine))

def correlation(xs, ys):
    n = len(xs)
    if n < 4:
        return None, n
    mx = sum(xs)/n; my = sum(ys)/n
    sxy=sx2=sy2=0.0
    for x,y in zip(xs,ys):
        dx=x-mx; dy=y-my
        sxy+=dx*dy; sx2+=dx*dx; sy2+=dy*dy
    if sx2==0 or sy2==0:
        return None, n
    return sxy/math.sqrt(sx2*sy2), n

T_TABLE = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
           11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086,
           21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}

def crit_t(df):
    if df <= 30:
        return T_TABLE[df]
    return 1.96 + (2.042-1.96)*max(0,(30.0/df))

def test_sig(r,n):
    if r is None or n<4:
        return "n/a"
    df=n-2
    ar=abs(r)
    if ar>=0.999999:
        return "yes"
    t=ar*math.sqrt(df/(1-ar*ar))
    return "yes" if t>=crit_t(df) else "no"

def get_pairs(rows, v1, v2):
    xs=[]; ys=[]
    for r in rows:
        a=r.get(v1); b=r.get(v2)
        if a is None or b is None:
            continue
        xs.append(a); ys.append(b)
    return xs,ys

results=[]
for v1,v2 in itertools.combinations(VAR_NAMES,2):
    cx,cy = get_pairs(coarse, v1, v2)
    rC,nC = correlation(cx,cy)
    fx,fy = get_pairs(fine, v1, v2)
    rF,nF = correlation(fx,fy)
    if rC is None or rF is None:
        continue
    diff_type="similar"
    if (rC>0)!=(rF>0) and abs(rC)>0.05 and abs(rF)>0.05:
        diff_type="reversed"
    elif abs(rC)>0.001:
        rel=abs(abs(rC)-abs(rF))/abs(rC)
        if rel>0.3:
            diff_type="magnitude_change"
    results.append({
        "variable": f"{v1} vs {v2}",
        "coarse_level": f"voivodeship(n={nC})",
        "coarse_stat": f"corr={round(rC,3)}",
        "fine_level": f"powiat(n={nF})",
        "fine_stat": f"corr={round(rF,3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC,nC),
        "fine_sig": test_sig(rF,nF),
    })

with open("results/poland_bdl_pairwise.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=["variable","coarse_level","coarse_stat","fine_level","fine_stat","diff_type","coarse_sig","fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
print(Counter(r["diff_type"] for r in results))

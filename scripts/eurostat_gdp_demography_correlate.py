import csv, math, json, os
from collections import defaultdict, Counter

REPO = "/home/user/-aggregation-bias-thesis"
GDP_RAW = "/tmp/claude-0/-home-user--aggregation-bias-thesis/98889ef9-74db-5de1-a5b9-f63f6e587bbd/scratchpad/gdp.csv"
OUT = "/tmp/claude-0/-home-user--aggregation-bias-thesis/98889ef9-74db-5de1-a5b9-f63f6e587bbd/scratchpad/out_gdp"
os.makedirs(OUT, exist_ok=True)

DEMO_VARS = ["total_dependency_ratio_per1000", "old_age_dependency_ratio_per1000",
             "youth_dependency_ratio_per1000", "median_age_years", "females_per1000_males",
             "young_0_14_per1000", "elderly_65plus_per1000", "oldest_80plus_per1000"]

COUNTRIES = {
    "BE": "Belgium", "BG": "Bulgaria", "CZ": "Czechia", "HR": "Croatia",
    "HU": "Hungary", "RO": "Romania", "SK": "Slovakia", "TR": "Turkey",
}
YEAR = "2024"

# gdp[country][glen] -> geo -> eur_hab
gdp = defaultdict(lambda: defaultdict(dict))
with open(GDP_RAW, newline="") as f:
    r = csv.DictReader(f)
    for row in r:
        if row["unit"] != "EUR_HAB" or row["TIME_PERIOD"] != YEAR:
            continue
        geo = row["geo"]
        country = geo[:2]
        if country not in COUNTRIES:
            continue
        glen = len(geo)
        if glen not in (4, 5):
            continue
        if row["OBS_VALUE"] == "":
            continue
        gdp[country][glen][geo] = float(row["OBS_VALUE"])

def load_demo(country_name, level):
    path = f"{REPO}/data/{country_name}/{country_name.lower()}_eurostat_demography_{level}.csv"
    rows = {}
    with open(path, newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            rows[row["geo"]] = {v: float(row[v]) for v in DEMO_VARS}
    return rows

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

T_TABLE = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306,
           9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131,
           16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080, 22: 2.074,
           23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045,
           30: 2.042}

def crit_t(df):
    if df<=30: return T_TABLE[df]
    return 1.96 + (2.042-1.96)*max(0,(30.0/df))

def test_sig(r,n):
    if r is None or n<4: return "n/a"
    df=n-2; ar=abs(r)
    if ar>=0.999999: return "yes"
    t=ar*math.sqrt(df/(1-ar*ar))
    return "yes" if t>=crit_t(df) else "no"

summary = {}
for cc, name in COUNTRIES.items():
    coarse_demo = load_demo(name, "coarse_nuts2")
    fine_demo = load_demo(name, "fine_nuts3")
    coarse_gdp = gdp[cc].get(4, {})
    fine_gdp = gdp[cc].get(5, {})

    coarse_geos = sorted(set(coarse_demo) & set(coarse_gdp))
    fine_geos = sorted(set(fine_demo) & set(fine_gdp))
    if len(coarse_geos) < 4 or len(fine_geos) < 4:
        print(cc, name, "SKIP insufficient overlap", len(coarse_geos), len(fine_geos))
        continue

    results = []
    for v in DEMO_VARS:
        cx = [coarse_gdp[g] for g in coarse_geos]
        cy = [coarse_demo[g][v] for g in coarse_geos]
        rC, nC = correlation(cx, cy)
        fx = [fine_gdp[g] for g in fine_geos]
        fy = [fine_demo[g][v] for g in fine_geos]
        rF, nF = correlation(fx, fy)
        if rC is None or rF is None:
            continue
        diff_type = "similar"
        if (rC>0)!=(rF>0) and abs(rC)>0.05 and abs(rF)>0.05:
            diff_type = "reversed"
        elif abs(rC)>0.001:
            rel = abs(abs(rC)-abs(rF))/abs(rC)
            if rel>0.3:
                diff_type = "magnitude_change"
        results.append({
            "variable": f"gdp_per_capita_eur vs {v}",
            "coarse_level": f"nuts2(n={nC})",
            "coarse_stat": f"corr={round(rC,3)}",
            "fine_level": f"nuts3(n={nF})",
            "fine_stat": f"corr={round(rF,3)}",
            "diff_type": diff_type,
            "coarse_sig": test_sig(rC,nC),
            "fine_sig": test_sig(rF,nF),
        })
    summary[cc] = {"name": name, "n_coarse": len(coarse_geos), "n_fine": len(fine_geos), "results": results}
    print(cc, name, "coarse:", len(coarse_geos), "fine:", len(fine_geos), "pairs:", len(results), Counter(x["diff_type"] for x in results))

    # write merged raw csvs
    with open(f"{OUT}/{name.lower()}_gdp_demography_coarse_nuts2.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["geo","gdp_per_capita_eur"]+DEMO_VARS)
        for g in coarse_geos:
            w.writerow([g, coarse_gdp[g]] + [coarse_demo[g][v] for v in DEMO_VARS])
    with open(f"{OUT}/{name.lower()}_gdp_demography_fine_nuts3.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["geo","gdp_per_capita_eur"]+DEMO_VARS)
        for g in fine_geos:
            w.writerow([g, fine_gdp[g]] + [fine_demo[g][v] for v in DEMO_VARS])

with open(f"{OUT}/summary.json","w") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
print("DONE")

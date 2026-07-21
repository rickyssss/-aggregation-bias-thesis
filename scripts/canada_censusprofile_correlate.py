import json, math, csv, itertools

COUNT_IDS = {
    "59": "married_or_commonlaw_per1000",
    "66": "not_married_not_commonlaw_per1000",
    "110": "one_person_households_per1000",
    "1415": "owner_households_per1000",
    "1416": "renter_households_per1000",
    "1529": "immigrants_per1000",
    "1528": "non_immigrants_per1000",
    "1999": "no_certificate_15plus_per1000",
    "2001": "postsecondary_cert_15plus_per1000",
    "2008": "bachelor_or_higher_15plus_per1000",
}
RATE_IDS = {
    "40": "median_age",
    "113": "median_total_income_recipients_2020",
    "115": "median_aftertax_income_recipients_2020",
    "243": "median_hh_total_income_2020",
    "244": "median_hh_aftertax_income_2020",
    "345": "lim_at_low_income_rate_pct",
    "360": "lico_at_low_income_rate_pct",
    "381": "gini_aftertax",
    "382": "p90_p10_ratio_aftertax",
    "1483": "owner_pct_with_mortgage",
    "1484": "owner_pct_30plus_shelter",
    "1486": "median_shelter_cost_owned",
    "1492": "tenant_pct_30plus_shelter",
    "1494": "median_shelter_cost_rented",
    "2228": "participation_rate",
    "2229": "employment_rate",
    "2230": "unemployment_rate",
}
POP_ID = "1"
VAR_NAMES = list(COUNT_IDS.values()) + list(RATE_IDS.values())

def load_table(path):
    with open(path) as f:
        data = json.load(f)
    rows = []
    for dguid, rec in data.items():
        vals = rec["values"]
        pop = vals.get(POP_ID)
        out = {"geo_name": rec["geo_name"], "dguid": dguid}
        ok = True
        if pop is None or pop <= 0:
            ok = False
        for cid, name in COUNT_IDS.items():
            v = vals.get(cid)
            out[name] = (v / pop * 1000.0) if (ok and v is not None) else None
        for cid, name in RATE_IDS.items():
            out[name] = vals.get(cid)
        rows.append(out)
    return rows

coarse = load_table("coarse.json")
fine = load_table("fine.json")

def write_csv(rows, path):
    fields = ["geo_name","dguid"] + VAR_NAMES
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

write_csv(coarse, "canada_censusprofile_coarse_province.csv")
write_csv(fine, "canada_censusprofile_fine_censusdivision.csv")
print("coarse rows", len(coarse), "fine rows", len(fine))

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

T_TABLE = {1:12.706,2:4.303,3:3.182,4:2.776,5:2.571,6:2.447,7:2.365,8:2.306,9:2.262,10:2.228,
11:2.201,12:2.179,13:2.160,14:2.145,15:2.131,16:2.120,17:2.110,18:2.101,19:2.093,20:2.086,
21:2.080,22:2.074,23:2.069,24:2.064,25:2.060,26:2.056,27:2.052,28:2.048,29:2.045,30:2.042}
def crit_t(df):
    if df<=30: return T_TABLE[df]
    return 1.96 + (2.042-1.96)*max(0,(30.0/df))
def test_sig(r,n):
    if r is None or n<4: return "n/a"
    df=n-2; ar=abs(r)
    if ar>=0.999999: return "yes"
    t = ar*math.sqrt(df/(1-ar*ar))
    return "yes" if t>=crit_t(df) else "no"

def get_pairs(rows, v1, v2):
    xs=[];ys=[]
    for r in rows:
        a=r[v1]; b=r[v2]
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
    if (rC>0) != (rF>0) and abs(rC) > 0.05 and abs(rF) > 0.05:
        diff_type = "reversed"
    elif abs(rC) > 0.001:
        rel = abs(abs(rC)-abs(rF))/abs(rC)
        if rel > 0.3:
            diff_type = "magnitude_change"
    results.append({
        "variable": f"{v1} vs {v2}",
        "coarse_level": f"province_territory(n={nC})",
        "coarse_stat": f"corr={round(rC,3)}",
        "fine_level": f"census_division(n={nF})",
        "fine_stat": f"corr={round(rF,3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC, nC),
        "fine_sig": test_sig(rF, nF),
    })

with open("canada_censusprofile_pairwise.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["variable","coarse_level","coarse_stat","fine_level","fine_stat","diff_type","coarse_sig","fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
from collections import Counter
print(Counter(r["diff_type"] for r in results))

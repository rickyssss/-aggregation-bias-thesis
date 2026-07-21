import json, math, csv, itertools

COUNT_IDS = {
    "KOSkvinne0000": "women_per1000",
    "KOSmenn0000": "men_per1000",
    "KOSfodde0000": "born_per1000_raw",
    "KOSdode0000": "died_per1000_raw",
    "KOSinnflytting0000": "migrants_in_per1000",
    "KOSutflytting0000": "moved_out_per1000",
    "KOSnettoinn0000": "net_immigration_per1000",
    "KOSskilteseparer0000": "divorced_separated_per1000",
    "KOSensligeover800000": "single_80plus_per1000",
    "KOSensligenav0000": "single_parents_benefit_per1000",
    "KOSuforepensjoni0000": "disability_benefit_per1000",
    "KOSinnvandrere0000": "immigrants_per1000",
}
RATE_IDS = {
    "KOSandelfodde0000": "births_per1000_pop_published",
    "KOSandeldodde0000": "deaths_per1000_pop_published",
    "KOSandelskilte0000": "pct_divorced_separated",
    "KOSandelenslige80000": "pct_single_80plus",
    "KOSandelensligen0000": "pct_single_parents_benefit",
    "KOSandelufor0000": "pct_disability_benefit",
    "KOSandelinntot0000": "pct_immigrant_background",
}
POP_ID = "KOSfolkemengde0000"
VAR_NAMES = list(COUNT_IDS.values()) + list(RATE_IDS.values())

def load(path, geo_dim_name):
    with open(path) as f:
        d = json.load(f)
    geo_dim = d["dimension"][geo_dim_name]["category"]
    content_dim = d["dimension"]["ContentsCode"]["category"]
    geo_codes = sorted(geo_dim["index"], key=lambda k: geo_dim["index"][k])
    content_codes = sorted(content_dim["index"], key=lambda k: content_dim["index"][k])
    geo_labels = geo_dim["label"]
    n_geo = len(geo_codes); n_content = len(content_codes)
    values = d["value"]
    rows = []
    for gi, gcode in enumerate(geo_codes):
        rec = {"geo_code": gcode, "geo_name": geo_labels[gcode]}
        for ci, ccode in enumerate(content_codes):
            rec[ccode] = values[gi*n_content+ci]
        rows.append(rec)
    return rows

def build_table(rows):
    out = []
    for r in rows:
        pop = r.get(POP_ID)
        if pop is None or pop <= 0:
            continue
        o = {"geo_code": r["geo_code"], "geo_name": r["geo_name"]}
        for cid, name in COUNT_IDS.items():
            v = r.get(cid)
            o[name] = (v/pop*1000.0) if v is not None else None
        for cid, name in RATE_IDS.items():
            o[name] = r.get(cid)
        out.append(o)
    return out

county_raw = load("county_2023.json", "KOKfylkesregion0000")
muni_raw = load("muni_2023.json", "KOKkommuneregion0000")
coarse = build_table(county_raw)
fine = build_table(muni_raw)
print("coarse", len(coarse), "fine", len(fine))

def write_csv(rows, path):
    fields = ["geo_code","geo_name"] + VAR_NAMES
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow(r)

write_csv(coarse, "norway_ssb_coarse_fylke.csv")
write_csv(fine, "norway_ssb_fine_kommune.csv")

def correlation(xs, ys):
    n = len(xs)
    if n < 4: return None, n
    mx=sum(xs)/n; my=sum(ys)/n
    sxy=sx2=sy2=0.0
    for x,y in zip(xs,ys):
        dx=x-mx; dy=y-my
        sxy+=dx*dy; sx2+=dx*dx; sy2+=dy*dy
    if sx2==0 or sy2==0: return None, n
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
        "coarse_level": f"fylke(n={nC})",
        "coarse_stat": f"corr={round(rC,3)}",
        "fine_level": f"kommune(n={nF})",
        "fine_stat": f"corr={round(rF,3)}",
        "diff_type": diff_type,
        "coarse_sig": test_sig(rC, nC),
        "fine_sig": test_sig(rF, nF),
    })

with open("norway_ssb_pairwise.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=["variable","coarse_level","coarse_stat","fine_level","fine_stat","diff_type","coarse_sig","fine_sig"])
    w.writeheader()
    for row in results:
        w.writerow(row)

print("pairs:", len(results))
from collections import Counter
print(Counter(r["diff_type"] for r in results))

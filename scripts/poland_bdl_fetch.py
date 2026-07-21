import json, time, urllib.request, urllib.error

VARS = {
    "population_total": 72305,
    "net_migration_per1000": 1365239,
    "live_births_per1000": 1616438,
    "deaths_per1000": 1616444,
    "natural_increase_per1000": 1616456,
    "divorces_per10k": 1616556,
    "old_age_dependency_ratio": 634067,
    "population_density_builtup": 458238,
    "urbanization_rate_pct": 1725015,
    "avg_wage_pct_of_national": 64429,
    "unemployment_rate_dec_pct": 461691,
    "infant_deaths_per1000_livebirths": 60569,
    "dwellings_completed_per1000_marriages": 148157,
}

def fetch(url, retries=5):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "thesis-research/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "ignore")
            print("HTTPERR", e.code, url, body[:200])
            if e.code == 429:
                time.sleep(10)
                continue
            return None
        except Exception as e:
            print("ERR", url, e)
            time.sleep(3)
    return None

def fetch_level(var_id, level):
    all_results = []
    page = 0
    while True:
        url = f"https://bdl.stat.gov.pl/api/v1/data/by-variable/{var_id}?unit-level={level}&format=json&page-size=100&page={page}"
        d = fetch(url)
        if d is None:
            break
        all_results.extend(d.get("results", []))
        total = d.get("totalRecords", 0)
        page += 1
        if page * 100 >= total:
            break
        time.sleep(0.2)
    return all_results

data = {}
for name, vid in VARS.items():
    print("fetching", name, vid)
    coarse = fetch_level(vid, 2)
    fine = fetch_level(vid, 5)
    data[name] = {"coarse": coarse, "fine": fine}
    print("  coarse", len(coarse), "fine", len(fine))
    time.sleep(0.3)

with open("/tmp/claude-0/-home-user--aggregation-bias-thesis/47afdfda-2d25-5b41-9315-0f4e0f766487/scratchpad/poland_raw/all_vars.json", "w") as f:
    json.dump(data, f)
print("done")

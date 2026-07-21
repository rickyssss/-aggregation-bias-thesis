import json, urllib.request

county = json.load(open("county_codes.json"))
muni = json.load(open("muni_codes.json"))

def post(url, query):
    body = json.dumps({"query": query, "response": {"format": "json-stat2"}}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def fetch(url, region_codes, extra_vars, out_path):
    query = [{"code": "Region", "selection": {"filter": "item", "values": region_codes}}]
    query += extra_vars
    d = post(url, query)
    json.dump(d, open(out_path, "w"))
    print(out_path, "size", d["size"] if "size" in d else "?")

# 1. Marital status (BefolkningNy)
url_pop = "https://api.scb.se/OV0104/v1/doris/en/ssd/BE/BE0101/BE0101A/BefolkningNy"
extra_pop = [
    {"code": "Civilstand", "selection": {"filter": "item", "values": ["OG", "G", "ÄNKL", "SK"]}},
    {"code": "Alder", "selection": {"filter": "item", "values": ["tot"]}},
    {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
    {"code": "ContentsCode", "selection": {"filter": "item", "values": ["BE0101N1"]}},
    {"code": "Tid", "selection": {"filter": "item", "values": ["2024"]}},
]
fetch(url_pop, county, extra_pop, "raw_pop_county.json")
fetch(url_pop, muni, extra_pop, "raw_pop_muni.json")

# 2. Net income (NetInk02)
url_inc = "https://api.scb.se/OV0104/v1/doris/en/ssd/HE/HE0110/HE0110A/NetInk02"
extra_inc = [
    {"code": "Kon", "selection": {"filter": "item", "values": ["1+2"]}},
    {"code": "Alder", "selection": {"filter": "item", "values": ["20-64"]}},
    {"code": "ContentsCode", "selection": {"filter": "item", "values": ["000001OR", "000001ON"]}},
    {"code": "Tid", "selection": {"filter": "item", "values": ["2024"]}},
]
fetch(url_inc, county, extra_inc, "raw_inc_county.json")
fetch(url_inc, muni, extra_inc, "raw_inc_muni.json")

# 3. Labour market status (ArRegArbStatus)
url_lab = "https://api.scb.se/OV0104/v1/doris/en/ssd/AM/AM0210/AM0210D/ArRegArbStatus"
extra_lab = [
    {"code": "Kon", "selection": {"filter": "item", "values": ["1+2"]}},
    {"code": "Alder", "selection": {"filter": "item", "values": ["16-64"]}},
    {"code": "Fodelseregion", "selection": {"filter": "item", "values": ["tot"]}},
    {"code": "ContentsCode", "selection": {"filter": "item", "values": ["000002NN", "000002NK", "000002NS"]}},
    {"code": "Tid", "selection": {"filter": "item", "values": ["2024"]}},
]
fetch(url_lab, county, extra_lab, "raw_lab_county.json")
fetch(url_lab, muni, extra_lab, "raw_lab_muni.json")

# 4. Education level (Utbildning)
url_edu = "https://api.scb.se/OV0104/v1/doris/en/ssd/UF/UF0506/UF0506B/Utbildning"
extra_edu = [
    {"code": "Alder", "selection": {"filter": "item", "values": ["tot16-74"]}},
    {"code": "UtbildningsNiva", "selection": {"filter": "item", "values": ["1", "2", "3", "4", "5", "6", "7", "US"]}},
    {"code": "Kon", "selection": {"filter": "item", "values": ["1", "2"]}},
    {"code": "ContentsCode", "selection": {"filter": "item", "values": ["UF0506A1"]}},
    {"code": "Tid", "selection": {"filter": "item", "values": ["2024"]}},
]
fetch(url_edu, county, extra_edu, "raw_edu_county.json")
fetch(url_edu, muni, extra_edu, "raw_edu_muni.json")

print("done")

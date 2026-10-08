#!/usr/bin/env python3
"""Rebuild the data files used by Mon Dossier Visa.

Usage:
  python scripts/build_data.py --visa PATH --embassies PATH --airports PATH [--zoneinfo /usr/share/zoneinfo] [--out data]

PATH arguments are local clones of:
  --visa       https://github.com/imorte/passport-index-data
  --embassies  https://github.com/database-of-embassies/database-of-embassies
  --airports   https://github.com/davidmegginson/ourairports-data

Writes data/visa.json, data/embassies.json, data/airports.json, data/tz.json and data/meta.json.
data/emergency.json and data/countries.geo.json are maintained by hand and left untouched.
Requires: pycountry (pip install pycountry).
"""
import argparse, collections, csv, json, os, re, subprocess, sys
from datetime import datetime, timezone

try:
    import pycountry
except ImportError:
    sys.exit("pycountry is required: pip install pycountry")


def write(out, name, obj):
    path = os.path.join(out, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {path} ({os.path.getsize(path):,} bytes)")


def git_date(repo):
    try:
        return subprocess.check_output(["git", "-C", repo, "log", "-1", "--format=%cs"], text=True).strip()
    except Exception:
        return ""


# ---------- Visa requirements ----------
DAYS = {"7": "a", "10": "b", "14": "c", "15": "d", "21": "e", "28": "f", "30": "g", "31": "h",
        "42": "i", "45": "j", "60": "k", "90": "l", "120": "m", "180": "n", "240": "o", "360": "p"}
CODE = {"-1": "-", "visa required": "R", "e-visa": "E", "visa on arrival": "O", "eta": "T",
        "visa free": "F", "no admission": "N"}


def nearest_days(v):
    n = int(v)
    key = min(DAYS, key=lambda k: abs(int(k) - n))
    return DAYS[key]


def build_visa(repo):
    rows = list(csv.reader(open(os.path.join(repo, "passport-index-matrix-iso2.csv"), encoding="utf-8")))
    dest = rows[0][1:]
    pas, m = [], []
    for r in rows[1:]:
        pas.append(r[0])
        line = []
        for v in r[1:]:
            v = v.strip()
            if v in CODE:
                line.append(CODE[v])
            elif v.isdigit():
                line.append(DAYS.get(v) or nearest_days(v))
            else:
                line.append("R")  # unknown value: safest default
        m.append("".join(line))
    updated = ""
    readme = os.path.join(repo, "README.md")
    if os.path.exists(readme):
        mt = re.search(r"Last updated:\s*\*\*(.+?)\*\*", open(readme, encoding="utf-8").read())
        if mt:
            updated = mt.group(1)
    return {"dest": dest, "pass": pas, "m": m}, updated or git_date(repo)


# ---------- Embassies ----------
NAME_FIX = {"Russia": "RU", "Turkey": "TR", "Vatican": "VA", "Vatican City": "VA", "Ivory Coast": "CI",
            "Palestine": "PS", "State of Palestine": "PS", "Democratic Republic of the Congo": "CD",
            "Brunei": "BN", "East Timor": "TL", "Cape Verde": "CV", "Kosovo": "XK", "The Gambia": "GM",
            "The Bahamas": "BS", "São Tomé and Príncipe": "ST", "Macau": "MO"}
_cache = {}


def cc(name):
    if name in NAME_FIX:
        return NAME_FIX[name]
    if name not in _cache:
        try:
            _cache[name] = pycountry.countries.lookup(name).alpha_2
        except LookupError:
            _cache[name] = None
    return _cache[name]


TYPES = {"embassy": "E", "high commission": "H", "consulate general": "G", "consulate": "C",
         "honorary consulate": "O", "de facto embassy": "D", "de facto consulate": "F", "apostolic nunciature": "N"}


def clean_city(c):
    c = c.strip()
    mt = re.match(r"^\d+(?:st|nd|rd|th|e|er)? arrondissement (?:of|de) (.+)$", c, re.I)
    if mt:
        return mt.group(1)
    return c


def build_embassies(repo):
    path = os.path.join(repo, "database_of_embassies.csv")
    out = collections.defaultdict(list)
    for r in csv.DictReader(open(path, encoding="utf-8"), delimiter=";"):
        o, c, t = cc(r["operator"]), cc(r["country"]), TYPES.get(r["type"])
        if not (o and c and t):
            continue
        try:
            lat, lng = round(float(r["latitude"]), 5), round(float(r["longitude"]), 5)
        except ValueError:
            lat = lng = None
        j = sorted({x for x in (cc(z) for z in r["jurisdictions"].split("|") if z) if x})
        ph = r["phone"].split("|")[0].strip() if r["phone"] else ""
        web = r["website"].split("|")[0].strip() if r["website"] else ""
        out[o].append([c, clean_city(r["city"]), lat, lng, ph, web, t, "".join(j)])
    return out, git_date(repo)


# ---------- Airports ----------
DEFAULT_AIRPORT = {"FR": "CDG", "DE": "FRA", "US": "JFK", "CA": "YUL", "CN": "PEK", "GB": "LHR", "IT": "FCO",
    "ES": "MAD", "BE": "BRU", "CH": "GVA", "MA": "CMN", "CI": "ABJ", "SN": "DSS", "NG": "LOS", "AE": "DXB",
    "TR": "IST", "JP": "HND", "IN": "DEL", "BR": "GRU", "RU": "SVO", "AU": "SYD", "ZA": "JNB", "EG": "CAI",
    "ET": "ADD", "KE": "NBO", "SA": "RUH", "QA": "DOH", "NL": "AMS", "PT": "LIS", "GH": "ACC", "TG": "LFW",
    "BJ": "COO", "CM": "DLA", "GA": "LBV", "ML": "BKO", "BF": "OUA", "NE": "NIM", "CD": "FIH", "CG": "BZV",
    "RW": "KGL", "TN": "TUN", "DZ": "ALG", "LU": "LUX", "AT": "VIE", "SE": "ARN", "NO": "OSL", "DK": "CPH",
    "FI": "HEL", "IE": "DUB", "PL": "WAW", "GR": "ATH", "KR": "ICN", "TH": "BKK", "SG": "SIN", "MY": "KUL",
    "ID": "CGK", "MX": "MEX", "AR": "EZE", "CO": "BOG", "PE": "LIM", "CL": "SCL", "GN": "CKY", "LR": "ROB",
    "SL": "FNA", "GM": "BJL", "MR": "NKC", "TD": "NDJ", "AO": "LAD", "TZ": "DAR", "UG": "EBB", "ZM": "LUN",
    "ZW": "HRE", "MG": "TNR", "MU": "MRU", "HT": "PAP", "IL": "TLV", "LB": "BEY", "JO": "AMM", "KW": "KWI",
    "BH": "BAH", "OM": "MCT", "PK": "ISB", "BD": "DAC", "VN": "SGN", "PH": "MNL", "NZ": "AKL", "CZ": "PRG",
    "HU": "BUD", "RO": "OTP", "BG": "SOF", "HR": "ZAG", "RS": "BEG"}


def build_airports(repo):
    a = collections.defaultdict(list)
    for r in csv.DictReader(open(os.path.join(repo, "airports.csv"), encoding="utf-8")):
        if r["scheduled_service"] != "yes" or not r["iata_code"] or r["type"] not in ("large_airport", "medium_airport"):
            continue
        city = (r["municipality"] or r["name"]).split("/")[0].strip()
        a[r["iso_country"]].append([r["iata_code"], city, 1 if r["type"] == "large_airport" else 0])
    out = {}
    for k, lst in a.items():
        lst.sort(key=lambda x: (x[0] != DEFAULT_AIRPORT.get(k), -x[2], x[1]))
        out[k] = [[i, c] for i, c, _ in lst]
    return out, git_date(repo)


# ---------- Time zones ----------
MAIN_TZ = {"US": "America/New_York", "CA": "America/Toronto", "BR": "America/Sao_Paulo", "RU": "Europe/Moscow",
    "AU": "Australia/Sydney", "MX": "America/Mexico_City", "CN": "Asia/Shanghai", "ID": "Asia/Jakarta",
    "KZ": "Asia/Almaty", "CD": "Africa/Kinshasa", "AR": "America/Argentina/Buenos_Aires", "CL": "America/Santiago",
    "ES": "Europe/Madrid", "PT": "Europe/Lisbon", "NZ": "Pacific/Auckland", "MN": "Asia/Ulaanbaatar",
    "EC": "America/Guayaquil", "UA": "Europe/Kyiv", "DE": "Europe/Berlin", "GL": "America/Nuuk",
    "FM": "Pacific/Pohnpei", "KI": "Pacific/Tarawa", "PF": "Pacific/Tahiti", "UZ": "Asia/Tashkent",
    "MY": "Asia/Kuala_Lumpur", "PG": "Pacific/Port_Moresby", "CY": "Asia/Nicosia", "UM": "Pacific/Wake",
    "AQ": "Antarctica/McMurdo"}


def build_tz(zoneinfo):
    from zoneinfo import ZoneInfo
    tz2cc, first, offsets = {}, {}, collections.defaultdict(set)
    for line in open(os.path.join(zoneinfo, "zone.tab"), encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        p = line.rstrip("\n").split("\t")
        code, name = p[0], p[2]
        tz2cc[name] = code
        first.setdefault(code, name)
        try:
            offsets[code].add(tuple(ZoneInfo(name).utcoffset(datetime(datetime.now().year, mth, 15)) for mth in (1, 7)))
        except Exception:
            pass
    zi = os.path.join(zoneinfo, "tzdata.zi")
    if os.path.exists(zi):
        for line in open(zi, encoding="utf-8"):
            if line.startswith("L "):
                _, target, alias = line.split()
                if alias not in tz2cc and target in tz2cc:
                    tz2cc[alias] = tz2cc[target]
    first.update(MAIN_TZ)
    multi = sorted(k for k, v in offsets.items() if len(v) > 1)
    return {"tz2cc": tz2cc, "cc2tz": first, "multi": multi}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--visa", required=True)
    ap.add_argument("--embassies", required=True)
    ap.add_argument("--airports", required=True)
    ap.add_argument("--zoneinfo", default="/usr/share/zoneinfo")
    ap.add_argument("--out", default="data")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    visa, visa_date = build_visa(a.visa)
    if len(visa["dest"]) < 190:
        sys.exit("visa matrix looks incomplete, aborting")
    emb, emb_date = build_embassies(a.embassies)
    if sum(len(v) for v in emb.values()) < 5000:
        sys.exit("embassies look incomplete, aborting")
    air, air_date = build_airports(a.airports)
    if len(air) < 200:
        sys.exit("airports look incomplete, aborting")
    tz = build_tz(a.zoneinfo)

    write(a.out, "visa.json", visa)
    write(a.out, "embassies.json", emb)
    write(a.out, "airports.json", air)
    write(a.out, "tz.json", tz)
    write(a.out, "meta.json", {
        "visa": visa_date, "embassies": emb_date, "airports": air_date,
        "built": datetime.now(timezone.utc).strftime("%Y-%m-%d")})


if __name__ == "__main__":
    main()

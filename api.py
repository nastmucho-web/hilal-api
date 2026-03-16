from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime, timedelta
from hijri_converter import convert

from skyfield.api import load, load_file, wgs84
from skyfield import almanac

app = FastAPI(title="Global Hilal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Astronomy
# =========================

ts = load.timescale()
eph = load_file("data/de421.bsp")

earth = eph["earth"]
moon = eph["moon"]
sun = eph["sun"]

# =========================
# Islamic countries
# =========================

countries = {
"Morocco": (34.0209,-6.8416),
"Algeria": (36.7538,3.0588),
"Tunisia": (36.8065,10.1815),
"Libya": (32.8872,13.1913),
"Egypt": (30.0444,31.2357),
"Sudan": (15.5007,32.5599),
"Mauritania": (18.0735,-15.9582),

"Saudi Arabia": (21.3891,39.8579),
"UAE": (25.2048,55.2708),
"Qatar": (25.2854,51.5310),
"Bahrain": (26.2235,50.5876),
"Kuwait": (29.3759,47.9774),
"Oman": (23.5880,58.3829),
"Yemen": (15.3694,44.1910),

"Jordan": (31.9454,35.9284),
"Palestine": (31.7683,35.2137),
"Lebanon": (33.8938,35.5018),
"Syria": (33.5138,36.2765),
"Iraq": (33.3152,44.3661),

"Turkey": (41.0082,28.9784),
"Iran": (35.6892,51.3890),

"Pakistan": (33.6844,73.0479),
"Afghanistan": (34.5553,69.2075),
"Bangladesh": (23.8103,90.4125),
"Maldives": (4.1755,73.5093),

"Indonesia": (-6.2088,106.8456),
"Malaysia": (3.1390,101.6869),
"Brunei": (4.9031,114.9398),

"Somalia": (2.0469,45.3182),
"Djibouti": (11.8251,42.5903),
"Eritrea": (15.3229,38.9251),
"Chad": (12.1348,15.0557),
"Niger": (13.5116,2.1254),
"Mali": (12.6392,-8.0029),
"Senegal": (14.7167,-17.4677),
"Gambia": (13.4549,-16.5790),
"Guinea": (9.6412,-13.5784),
"Sierra Leone": (8.4657,-13.2317),
"Nigeria": (9.0765,7.3986),
"Cameroon": (3.8480,11.5021),
"Uganda": (0.3476,32.5825),
"Tanzania": (-6.1630,35.7516),
"Comoros": (-11.7172,43.2473),
"Mozambique": (-25.9692,32.5732),

"Albania": (41.3275,19.8187),
"Bosnia": (43.8563,18.4131),
"Kosovo": (42.6629,21.1655)
}

days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# =========================
# Sunset
# =========================

def sunset_time(lat, lon, date):

    observer = wgs84.latlon(lat, lon)

    t0 = ts.utc(date.year,date.month,date.day)
    t1 = ts.utc(date.year,date.month,date.day+1)

    f = almanac.sunrise_sunset(eph,observer)

    times,events = almanac.find_discrete(t0,t1,f)

    for t,e in zip(times,events):
        if e == 0:
            return t

# =========================
# New Moons
# =========================

def new_moons(year):

    t0 = ts.utc(year-1,1,1)
    t1 = ts.utc(year+1,1,1)

    f = almanac.moon_phases(eph)

    times,phases = almanac.find_discrete(t0,t1,f)

    nm = []

    for t,p in zip(times,phases):
        if p == 0:
            nm.append(t.utc_datetime())

    return nm

# =========================
# Hilal visibility
# =========================

def hilal_visible(lat, lon, date, newmoon):

    observer = wgs84.latlon(lat, lon)

    sunset = sunset_time(lat, lon, date)

    if sunset.utc_datetime() < newmoon:
        return False

    moon_astrometric = (earth + observer).at(sunset).observe(moon)
    sun_astrometric = (earth + observer).at(sunset).observe(sun)

    moon_app = moon_astrometric.apparent()
    sun_app = sun_astrometric.apparent()

    moon_alt = moon_app.altaz()[0].degrees
    sun_alt = sun_app.altaz()[0].degrees

    elong = moon_app.separation_from(sun_app).degrees

    arcv = moon_alt - sun_alt

    W = 0.2725 * elong

    V = arcv - (-0.1018*W**3 + 0.7319*W**2 - 6.3226*W + 7.1651)

    if V > 0:
        return True

    return False
# =========================
# Find month start
# =========================

def find_month(lat,lon,hijri_month,year):

    hijri_year = convert.Gregorian(year,1,1).to_hijri().year

    approx = convert.Hijri(hijri_year,hijri_month,1).to_gregorian()

    approx_date = datetime(approx.year,approx.month,approx.day).date()

    moons = new_moons(year)

    for nm in moons:

        if abs((nm.date()-approx_date).days) < 20:

            for offset in range(0,5):

                d = nm.date()+timedelta(days=offset)

                if hilal_visible(lat,lon,d,nm):

                    start = d+timedelta(days=1)

                    weekday = days[start.weekday()]

                    month_name = convert.Hijri(
                        hijri_year,
                        hijri_month,
                        1
                    ).month_name()

                    return {
                        "weekday":weekday,
                        "gregorian":start.isoformat(),
                        "hijri":f"1 {month_name} {hijri_year}"
                    }

    return {"error":"month not found"}

# =========================
# Test multiple locations per country
# =========================

def find_month_country(lat,lon,month,year):

    offsets = [
        (0,0),
        (1.5,0),
        (-1.5,0),
        (0,1.5),
        (0,-1.5)
    ]

    for dlat,dlon in offsets:

        result = find_month(lat+dlat,lon+dlon,month,year)

        if "gregorian" in result:
            return result

    return {"error":"month not found"}

# =========================
# RAMADAN
# =========================

@app.get("/ramadan/world")
def ramadan_world(year:int):

    results = {}

    for country,(lat,lon) in countries.items():
        results[country] = find_month_country(lat,lon,9,year)

    return results

# =========================
# EID FITR
# =========================

@app.get("/eid_fitr/world")
def eid_fitr_world(year:int):

    results = {}

    for country,(lat,lon) in countries.items():
        results[country] = find_month_country(lat,lon,10,year)

    return results

# =========================
# EID ADHA
# =========================

@app.get("/eid_adha/world")
def eid_adha_world(year:int):

    results = {}

    for country,(lat,lon) in countries.items():

        start = find_month_country(lat,lon,12,year)

        if "gregorian" in start:

            g = datetime.fromisoformat(start["gregorian"]) + timedelta(days=9)

            weekday = days[g.weekday()]

            results[country] = {
                "weekday":weekday,
                "gregorian":g.date().isoformat(),
                "hijri":"10 Dhul Hijjah"
            }

        else:
            results[country] = start

    return results

# =========================
# ROOT
# =========================

@app.get("/")
def home():

    return {
        "API":"Global Hilal API",
        "usage":{
            "ramadan_world":"/ramadan/world?year=2026",
            "eid_fitr_world":"/eid_fitr/world?year=2026",
            "eid_adha_world":"/eid_adha/world?year=2026"
        }
    }
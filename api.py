from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from datetime import datetime, timedelta
from hijri_converter import convert

from skyfield.api import load, load_file, wgs84
from skyfield import almanac

app = FastAPI()

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
"Saudi Arabia": (21.3891,39.8579),
"UAE": (25.2048,55.2708),
"Qatar": (25.2854,51.5310),
"Kuwait": (29.3759,47.9774),
"Oman": (23.5880,58.3829),
"Pakistan": (33.6844,73.0479),
"Indonesia": (-6.2088,106.8456),
"Malaysia": (3.1390,101.6869),
"Turkey": (41.0082,28.9784),
"Iran": (35.6892,51.3890),
"Bangladesh": (23.8103,90.4125),
"Afghanistan": (34.5553,69.2075),
"Somalia": (2.0469,45.3182),
"Sudan": (15.5007,32.5599),
"Mauritania": (18.0735,-15.9582)
}

days = [
"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"
]

# =========================
# sunset
# =========================

def sunset_time(lat,lon,date):

    observer = wgs84.latlon(lat,lon)

    t0 = ts.utc(date.year,date.month,date.day)
    t1 = ts.utc(date.year,date.month,date.day+1)

    f = almanac.sunrise_sunset(eph,observer)

    times,events = almanac.find_discrete(t0,t1,f)

    for t,e in zip(times,events):
        if e == 0:
            return t

# =========================
# hilal visibility
# =========================

def hilal_visible(lat,lon,date):

    observer = wgs84.latlon(lat,lon)

    sunset = sunset_time(lat,lon,date)

    moon_astrometric = (earth+observer).at(sunset).observe(moon)
    sun_astrometric = (earth+observer).at(sunset).observe(sun)

    alt,az,d = moon_astrometric.apparent().altaz()

    moon_alt = alt.degrees
    elong = moon_astrometric.separation_from(sun_astrometric).degrees

    if elong < 7:
        return False

    if moon_alt > 5 and elong > 10:
        return True

    return False

# =========================
# calculate month start
# =========================

def find_month(lat,lon,hijri_month):

    today = datetime.utcnow().date()

    for i in range(40):

        test_day = today + timedelta(days=i)

        if hilal_visible(lat,lon,test_day):

            start = test_day + timedelta(days=1)

            h = convert.Gregorian(start.year,start.month,start.day).to_hijri()

            if h.month == hijri_month and h.day == 1:

                weekday = days[start.weekday()]

                return {
                    "weekday": weekday,
                    "gregorian": start.isoformat(),
                    "hijri": f"{h.day} {h.month_name()} {h.year}"
                }

# =========================
# RAMADAN
# =========================

@app.get("/ramadan/world")

def ramadan_world():

    results = {}

    for country,(lat,lon) in countries.items():
        results[country] = find_month(lat,lon,9)

    return results

# =========================
# EID AL FITR
# =========================

@app.get("/eid_fitr/world")

def eid_fitr_world():

    results = {}

    for country,(lat,lon) in countries.items():
        results[country] = find_month(lat,lon,10)

    return results

# =========================
# EID AL ADHA
# =========================

@app.get("/eid_adha/world")

def eid_adha_world():

    results = {}

    for country,(lat,lon) in countries.items():

        start = find_month(lat,lon,12)

        if start:

            g = datetime.fromisoformat(start["gregorian"]) + timedelta(days=9)

            weekday = days[g.weekday()]

            results[country] = {
                "weekday": weekday,
                "gregorian": g.date().isoformat(),
                "hijri": f"10 Dhul Hijjah"
            }

    return results

# =========================
# COUNTRY QUERY
# =========================

@app.get("/ramadan/country")

def ramadan_country(name:str):

    if name not in countries:
        return {"error":"country not found"}

    lat,lon = countries[name]

    return {
        name: find_month(lat,lon,9)
    }

# =========================
# ROOT
# =========================

@app.get("/")
def home():

    return {
        "API":"Global Hilal API",
        "endpoints":[
            "/ramadan/world",
            "/eid_fitr/world",
            "/eid_adha/world",
            "/ramadan/country?name=Morocco"
        ]
    }
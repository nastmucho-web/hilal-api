from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from datetime import date, timedelta
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


@app.get("/")
def home():
    return {
        "message": "Global Hilal API running",
        "ramadan_endpoint": "/ramadan/world",
        "eid_fitr_endpoint": "/eid_fitr/world",
        "eid_adha_endpoint": "/eid_adha/world"
    }
    
    

# =========================
# Astronomical data
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

"Morocco": (27.1536,-13.2033),
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
"Azerbaijan": (40.4093,49.8671),

"Iran": (35.6892,51.3890),
"Kazakhstan": (51.1605,71.4704),
"Uzbekistan": (41.2995,69.2401),
"Turkmenistan": (37.9601,58.3261),
"Kyrgyzstan": (42.8746,74.5698),
"Tajikistan": (38.5598,68.7870),

"Afghanistan": (34.5553,69.2075),
"Pakistan": (33.6844,73.0479),
"Bangladesh": (23.8103,90.4125),
"Maldives": (4.1755,73.5093),

"Indonesia": (-6.2088,106.8456),
"Malaysia": (3.1390,101.6869),
"Brunei": (4.9031,114.9398),

"Somalia": (2.0469,45.3182),
"Djibouti": (11.8251,42.5903),
"Eritrea": (15.3229,38.9251),
"Ethiopia": (9.1450,40.4897),
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
"Gabon": (0.4162,9.4673),

"Albania": (41.3275,19.8187),
"Bosnia": (43.8563,18.4131),
"Kosovo": (42.6629,21.1655)

}

# =========================
# weekdays
# =========================

days = [
"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"
]

# =========================
# sunset
# =========================

def sunset_time(lat,lon):

    observer = wgs84.latlon(lat,lon)

    t0 = ts.now()
    t1 = ts.utc(t0.utc_datetime().year,t0.utc_datetime().month,t0.utc_datetime().day+1)

    f = almanac.sunrise_sunset(eph,observer)

    times,events = almanac.find_discrete(t0,t1,f)

    for t,e in zip(times,events):

        if e == 0:
            return t

# =========================
# hilal visibility
# =========================

def hilal_visible(lat,lon):

    observer = wgs84.latlon(lat,lon)

    sunset = sunset_time(lat,lon)

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
# calculate event
# =========================

def calculate_event(h_month,h_day,name):

    results = {}
    today = date.today()

    for country,(lat,lon) in countries.items():

        visible = hilal_visible(lat,lon)

        if visible:
            start = today + timedelta(days=1)
        else:
            start = today + timedelta(days=2)

        weekday = days[start.weekday()]

        h = convert.Gregorian(start.year,start.month,start.day).to_hijri()

        results[country] = {
            "event": name,
            "weekday": weekday,
            "gregorian": start.isoformat(),
            "hijri": f"{h.day}-{h.month}-{h.year}"
        }

    return results

# =========================
# Ramadan
# =========================

@app.get("/ramadan/world")

def ramadan():

    return calculate_event(9,1,"Ramadan")

# =========================
# Eid Fitr
# =========================

@app.get("/eid_fitr/world")

def eid_fitr():

    return calculate_event(10,1,"Eid al-Fitr")

# =========================
# Eid Adha
# =========================

@app.get("/eid_adha/world")

def eid_adha():

    return calculate_event(12,10,"Eid al-Adha")
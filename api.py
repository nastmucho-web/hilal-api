from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from datetime import date
from hijri_converter import convert

from skyfield.api import load, load_file, wgs84

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تحميل البيانات الفلكية مرة واحدة فقط
ts = load.timescale()
eph = load_file("data/de421.bsp")

earth = eph["earth"]
moon = eph["moon"]


@app.get("/")
def home():
    return {"message": "Hilal API running"}


@app.get("/predict")
def predict(moon_age: float, moon_alt: float):

    if moon_age > 18 and moon_alt > 5:
        return {"prediction": "Visible"}
    else:
        return {"prediction": "Not Visible"}


@app.get("/ramadan")
def ramadan():

    today = date.today()
    hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()

    return {
        "ramadan_year": hijri.year
    }


@app.get("/eid_fitr")
def eid_fitr():

    today = date.today()
    hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()

    return {
        "eid_fitr_year": hijri.year
    }


@app.get("/eid_adha")
def eid_adha():

    today = date.today()
    hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()

    return {
        "eid_adha_year": hijri.year
    }


@app.get("/hilal/morocco")
def hilal_morocco():

    # مدينة العيون (أول مكان يظهر فيه الهلال في المغرب)
    observer = wgs84.latlon(27.1536, -13.2033)

    t = ts.now()

    astrometric = (earth + observer).at(t).observe(moon)
    alt, az, distance = astrometric.apparent().altaz()

    moon_altitude = alt.degrees

    visible = bool(moon_altitude > 5)

    return {
        "country": "Morocco",
        "city": "Laayoune",
        "moon_altitude": round(moon_altitude, 2),
        "visible": visible
    }
    
@app.get("/hilal/world")
def hilal_world():

    locations = {

        # شمال أفريقيا
        "Morocco": (27.1536, -13.2033),
        "Algeria": (36.7538, 3.0588),
        "Tunisia": (36.8065, 10.1815),
        "Libya": (32.8872, 13.1913),
        "Egypt": (30.0444, 31.2357),
        "Sudan": (15.5007, 32.5599),
        "Mauritania": (18.0735, -15.9582),

        # الخليج
        "Saudi Arabia": (21.3891, 39.8579),
        "UAE": (25.2048, 55.2708),
        "Qatar": (25.2854, 51.5310),
        "Bahrain": (26.2235, 50.5876),
        "Kuwait": (29.3759, 47.9774),
        "Oman": (23.5880, 58.3829),
        "Yemen": (15.3694, 44.1910),

        # الشام والعراق
        "Jordan": (31.9454, 35.9284),
        "Palestine": (31.7683, 35.2137),
        "Lebanon": (33.8938, 35.5018),
        "Syria": (33.5138, 36.2765),
        "Iraq": (33.3152, 44.3661),

        # تركيا والقوقاز
        "Turkey": (41.0082, 28.9784),
        "Azerbaijan": (40.4093, 49.8671),

        # إيران وآسيا الوسطى
        "Iran": (35.6892, 51.3890),
        "Kazakhstan": (51.1605, 71.4704),
        "Uzbekistan": (41.2995, 69.2401),
        "Turkmenistan": (37.9601, 58.3261),
        "Kyrgyzstan": (42.8746, 74.5698),
        "Tajikistan": (38.5598, 68.7870),

        # جنوب آسيا
        "Afghanistan": (34.5553, 69.2075),
        "Pakistan": (33.6844, 73.0479),
        "Bangladesh": (23.8103, 90.4125),
        "Maldives": (4.1755, 73.5093),

        # جنوب شرق آسيا
        "Indonesia": (-6.2088, 106.8456),
        "Malaysia": (3.1390, 101.6869),
        "Brunei": (4.9031, 114.9398),

        # أفريقيا
        "Somalia": (2.0469, 45.3182),
        "Djibouti": (11.8251, 42.5903),
        "Ethiopia": (9.1450, 40.4897),
        "Eritrea": (15.3229, 38.9251),
        "Chad": (12.1348, 15.0557),
        "Niger": (13.5116, 2.1254),
        "Mali": (12.6392, -8.0029),
        "Senegal": (14.7167, -17.4677),
        "Gambia": (13.4549, -16.5790),
        "Guinea": (9.6412, -13.5784),
        "Sierra Leone": (8.4657, -13.2317),
        "Nigeria": (9.0765, 7.3986),
        "Cameroon": (3.8480, 11.5021),
        "Uganda": (0.3476, 32.5825),
        "Tanzania": (-6.1630, 35.7516),
        "Comoros": (-11.7172, 43.2473),
        "Mozambique": (-25.9692, 32.5732),
        "Gabon": (0.4162, 9.4673),

        # أوروبا
        "Albania": (41.3275, 19.8187),
        "Bosnia": (43.8563, 18.4131),
        "Kosovo": (42.6629, 21.1655)
    }

    t = ts.now()

    results = {}

    for country, coords in locations.items():

        lat, lon = coords

        observer = wgs84.latlon(lat, lon)

        astrometric = (earth + observer).at(t).observe(moon)
        alt, az, distance = astrometric.apparent().altaz()

        altitude = float(alt.degrees)

        visible = bool(altitude > 5)

        results[country] = {
            "moon_altitude": round(altitude, 2),
            "visible": visible
        }

    return results
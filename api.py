from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from datetime import date
from hijri_converter import convert

from skyfield.api import load, Topos

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# تحميل البيانات الفلكية مرة واحدة
ts = load.timescale()
eph = load('de421.bsp')

earth = eph['earth']
moon = eph['moon']


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
        "ramadan": f"Ramadan {hijri.year}"
    }


@app.get("/eid_fitr")
def eid_fitr():

    today = date.today()
    hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()

    return {
        "eid_fitr": f"Eid Al-Fitr {hijri.year}"
    }


@app.get("/eid_adha")
def eid_adha():

    today = date.today()
    hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()

    return {
        "eid_adha": f"Eid Al-Adha {hijri.year}"
    }


@app.get("/hilal/morocco")
def hilal_morocco():

    location = earth + Topos(latitude_degrees=27.1536, longitude_degrees=-13.2033)

    t = ts.now()

    astrometric = location.at(t).observe(moon)
    alt, az, distance = astrometric.apparent().altaz()

    moon_altitude = alt.degrees

    visible = moon_altitude > 5

    return {
        "country": "Morocco",
        "city": "Laayoune",
        "moon_altitude": moon_altitude,
        "visible": visible
    }
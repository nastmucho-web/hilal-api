from fastapi import FastAPI
from datetime import datetime
import math

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hilal API is running"}

def calculate_moon_age():
    # حساب بسيط لعمر القمر (تقريبي)
    now = datetime.utcnow()
    days = now.timetuple().tm_yday
    moon_cycle = 29.53
    age = days % moon_cycle
    return round(age, 2)

def calculate_moon_altitude():
    # حساب تقريبي لارتفاع القمر
    now = datetime.utcnow()
    altitude = 10 + 5 * math.sin(now.timestamp())
    return round(altitude, 2)

@app.get("/predict")
def predict():

    moon_age = calculate_moon_age()
    moon_alt = calculate_moon_altitude()

    if moon_age > 15 and moon_alt > 5:
        result = "الهلال مرئي"
    else:
        result = "الهلال غير مرئي"

    return {
        "moon_age": moon_age,
        "moon_altitude": moon_alt,
        "prediction": result
    }
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hilal API running"}

@app.get("/predict")
def predict(moon_age: float, moon_alt: float):

    if moon_age > 18 and moon_alt > 5:
        return {"prediction": "Visible"}
    else:
        return {"prediction": "Not Visible"}

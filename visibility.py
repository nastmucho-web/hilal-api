import joblib
from astronomy import compute_features

model = joblib.load("manazel_model.pkl")


def hilal_visible_ai(lat, lon, date):

    features = compute_features(lat, lon, date)

    probability = model.predict_proba([features])[0][1]

    return probability > 0.6
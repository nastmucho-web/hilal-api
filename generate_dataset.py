import pandas as pd
import random

data = []

for i in range(20000):

    moon_alt = random.uniform(-5, 15)
    elong = random.uniform(2, 20)
    arcv = random.uniform(-5, 15)
    moon_age = random.uniform(0, 40)

    visible = 0

    # منطق قريب من معايير الرؤية
    if moon_alt > 5 and elong > 10 and arcv > 5 and moon_age > 18:
        visible = 1

    data.append([
        moon_alt,
        arcv,
        elong,
        moon_age,
        visible
    ])

df = pd.DataFrame(data, columns=[
    "moon_alt",
    "arcv",
    "elongation",
    "moon_age",
    "visible"
])

df.to_csv("dataset.csv", index=False)

print("dataset created")
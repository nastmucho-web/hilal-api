@app.get("/hilal/morocco")
def hilal_morocco():

    try:

        ts = load.timescale()
        eph = load('de421.bsp')

        earth = eph['earth']
        moon = eph['moon']

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

    except Exception as e:

        return {
            "error": str(e)
        }
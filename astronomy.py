from skyfield.api import load, load_file, wgs84
from skyfield import almanac

ts = load.timescale()
eph = load_file("data/de421.bsp")

earth = eph["earth"]
moon = eph["moon"]
sun = eph["sun"]


def sunset_time(lat, lon, date):

    observer = wgs84.latlon(lat, lon)

    t0 = ts.utc(date.year, date.month, date.day)
    t1 = ts.utc(date.year, date.month, date.day + 1)

    f = almanac.sunrise_sunset(eph, observer)

    times, events = almanac.find_discrete(t0, t1, f)

    for t, e in zip(times, events):
        if e == 0:
            return t


def compute_features(lat, lon, date):

    observer = wgs84.latlon(lat, lon)

    sunset = sunset_time(lat, lon, date)

    moon_ast = (earth + observer).at(sunset).observe(moon)
    sun_ast = (earth + observer).at(sunset).observe(sun)

    moon_app = moon_ast.apparent()
    sun_app = sun_ast.apparent()

    moon_alt = moon_app.altaz()[0].degrees
    sun_alt = sun_app.altaz()[0].degrees

    elong = moon_app.separation_from(sun_app).degrees

    arcv = moon_alt - sun_alt

    w = 0.5 * elong

    return [arcv, w]
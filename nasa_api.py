import requests
from datetime import datetime, timedelta

def get_nasa_power_data(lat, lon):
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d")
    url = "https://power.larc.nasa.gov/api/temporal/daily/point?parameters=PRECTOTCORR&community=AG&longitude={}&latitude={}&start={}&end={}&format=JSON".format(lon, lat, start_date, end_date)
    try:
        res = requests.get(url, timeout=15).json()
        rain_data = res.get('properties', {}).get('parameter', {}).get('PRECTOTCORR', {})
        if len(rain_data) == 0: return None
        last_date = list(rain_data.keys())[-1]
        return float(rain_data.get(last_date, 0))
    except:
        return None
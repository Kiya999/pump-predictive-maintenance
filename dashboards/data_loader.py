# data_loader.py

import pandas as pd
import dataretrieval.nwis as nwis
import requests
from datetime import datetime, timedelta
import os

CACHE_DIR = 'cache'

def _cache_path(prefix, start, end):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return f"{CACHE_DIR}/{prefix}_{start}_{end}.csv"

def load_hourly_discharge(station_id='01646500', start_date='2025-05-25', end_date='2026-05-25'):
    path = _cache_path(f'usgs_{station_id}', start_date, end_date)
    if os.path.exists(path):
        print("Loading cached USGS...")
        hourly = pd.read_csv(path, index_col=0, parse_dates=True)
        print(f"  {len(hourly)} cached")
        return hourly

    print(f"Downloading USGS {station_id}...")
    df, meta = nwis.get_iv(sites=station_id, start=start_date, end=end_date, parameterCd='00060')
    hourly = df[['00060']].resample('1h').mean()
    hourly.columns = ['discharge_cfs']
    hourly.index = hourly.index.tz_localize(None)
    hourly.to_csv(path)
    print(f"  {len(hourly)} records")
    return hourly

def load_weather(lat=38.9072, lon=-77.0369, start_date='2025-05-25', end_date='2026-05-25'):
    path = _cache_path(f'weather_{lat}_{lon}', start_date, end_date)
    if os.path.exists(path):
        print("Loading cached weather...")
        weather = pd.read_csv(path, index_col=0, parse_dates=True)
        print(f"  {len(weather)} cached")
        return weather

    print("Downloading weather...")
    params = {"latitude": lat, "longitude": lon,
              "start_date": start_date, "end_date": end_date,
              "hourly": "temperature_2m,precipitation",
              "timezone": "America/New_York"}
    resp = requests.get("https://archive-api.open-meteo.com/v1/archive",
                        params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    weather = pd.DataFrame({'datetime': pd.to_datetime(data['hourly']['time']),
                            'temp_c': data['hourly']['temperature_2m'],
                            'precip_mm': data['hourly']['precipitation']})
    weather.set_index('datetime', inplace=True)
    weather.to_csv(path)
    print(f"  {len(weather)} records")
    return weather

def load_combined(station_id='01646500', start_date='2025-05-25', end_date='2026-05-25', lat=38.9072, lon=-77.0369):
    path = _cache_path(f'combined_{station_id}', start_date, end_date)
    if os.path.exists(path):
        print("Loading combined data...")
        combined = pd.read_csv(path, index_col=0, parse_dates=True)
        print(f"  {len(combined)} cached")
        return combined

    q = load_hourly_discharge(station_id, start_date, end_date)
    w = load_weather(lat, lon, start_date, end_date)
    combined = q.join(w, how='inner').dropna()
    combined.to_csv(path)
    print(f"  Combined: {len(combined)}")
    return combined

def load_sample():
    end = datetime.now()
    start = end - timedelta(days=30)
    return load_combined(start_date=start.strftime('%Y-%m-%d'), end_date=end.strftime('%Y-%m-%d'))

if __name__ == '__main__':
    df = load_sample()
    print(df.shape, list(df.columns))

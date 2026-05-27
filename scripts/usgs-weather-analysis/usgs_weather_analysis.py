# usgs_weather_analysis.py

import dataretrieval.nwis as nwis
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from datetime import datetime, timedelta
from scipy.signal import correlate
import time, sys, warnings


warnings.filterwarnings('ignore')

DC_LAT, DC_LON = 38.9072, -77.0369
SITE = '01646500'

end = datetime.now()
start = end - timedelta(days=365)

print(f"Period: {start.date()} to {end.date()}")

# Download
print("Downloading USGS streamflow...")
for attempt in range(3):
    try:
        df, meta = nwis.get_iv(sites=SITE, start=start.strftime('%Y-%m-%d'),
                               end=end.strftime('%Y-%m-%d'), parameterCd='00060')
        print(f"  {len(df)} records")
        time.sleep(2)
        break
    except Exception as e:
        print(f"  Retry {attempt+1}: {e}")
        time.sleep(5 * (attempt + 1))
else:
    sys.exit("Could not download USGS data")

# Profile
col, qc_col = '00060', '00060_cd'
diffs = df.index.to_series().diff().dropna()
gaps = diffs[diffs > pd.Timedelta('15 minutes')]
gap_dur = gaps.sum()

# Save profile
with open('usgs_data_profile.txt', 'w') as f:
    f.write("Station: 01646500 - Potomac River near Wash DC (Little Falls)\n")
    f.write(f"Range: {df.index.min()} to {df.index.max()}\n")
    f.write(f"Records: {len(df)}, Missing: {df[col].isna().sum()}\n")
    f.write(f"Approved: {(df[qc_col]=='A').sum()}, Provisional: {(df[qc_col]=='P').sum()}\n")
    f.write(f"Gaps >15min: {len(gaps)} (total {gap_dur})\n")
    f.write(f"Discharge (cfs): min={df[col].min():.0f}, max={df[col].max():.0f}, "
            f"mean={df[col].mean():.0f}, median={df[col].median():.0f}")

# Resample
hourly = df[['00060']].resample('1H').mean()
hourly.columns = ['01646500_cfs']
hourly.index = hourly.index.tz_localize(None)
print(f"Resampled to {len(hourly)} hourly records")

# Plots
fig, axes = plt.subplots(3, 1, figsize=(16, 13))

axes[0].plot(hourly.index, hourly['01646500_cfs'], lw=0.5, color='steelblue')
axes[0].set_title('Hourly Discharge - 12 Months')
axes[0].set_ylabel('cfs')
axes[0].grid(True, alpha=0.3)

plot_df = hourly.copy()
plot_df['month'] = plot_df.index.month
melted = plot_df.melt(id_vars='month', var_name='Station', value_name='Discharge')
sns.boxplot(data=melted, x='month', y='Discharge', ax=axes[1], color='steelblue')
axes[1].set_title('Monthly Distribution')
axes[1].grid(True, alpha=0.3)

missing_weekly = hourly.isna().astype(int).resample('W').sum()
gaps_weekly = gaps.resample('W').count()
axes[2].fill_between(missing_weekly.index, missing_weekly['01646500_cfs'],
                     alpha=0.3, color='crimson')
axes[2].plot(missing_weekly.index, missing_weekly['01646500_cfs'],
             marker='o', ms=3, color='crimson', label='Missing hours')
ax2 = axes[2].twinx()
ax2.plot(gaps_weekly.index, gaps_weekly.values, marker='s', ms=3,
         color='darkorange', label='Gaps >15min')
axes[2].set_title(f'Missing Data ({len(gaps)} gaps)')
axes[2].set_ylabel('Missing hours')
ax2.set_ylabel('# gaps')
axes[2].grid(True, alpha=0.3)
axes[2].legend(loc='upper left')
plt.tight_layout()
plt.savefig('usgs_exploratory_plots.png', dpi=150)

fig2, ax = plt.subplots(figsize=(12, 5))
ax.hist(hourly['01646500_cfs'].dropna(), bins=80, density=True,
        color='steelblue', edgecolor='white', lw=0.3)
ax.set_title('Discharge Distribution')
ax.set_xlabel('cfs')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('usgs_discharge_histogram.png', dpi=150)
plt.close('all')

# Weather
print("Downloading weather...")
params = {"latitude": DC_LAT, "longitude": DC_LON,
          "start_date": start.strftime('%Y-%m-%d'),
          "end_date": end.strftime('%Y-%m-%d'),
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
print(f"  {len(weather)} records")

# Join and correlate
combined = hourly.join(weather, how='inner').dropna()
print(f"Joined: {len(combined)} records")

if len(combined) < 500:
    sys.exit("Not enough data")

def z(s):
    return (s - s.mean()) / s.std()

q, p, t = z(combined['01646500_cfs']), z(combined['precip_mm']), z(combined['temp_c'])
n = len(q)

corr_qp = correlate(q, p, mode='full', method='auto') / n
corr_qt = correlate(q, t, mode='full', method='auto') / n
lags = np.arange(-n + 1, n)

targets = [0, 6, 12, 24]
r_p = {lag: corr_qp[np.argmin(np.abs(lags - lag))] for lag in targets}
r_t = {lag: corr_qt[np.argmin(np.abs(lags - lag))] for lag in targets}

mask = np.abs(lags) <= 72
best_p = lags[np.where(mask)[0][np.argmax(np.abs(corr_qp[mask]))]]
best_t = lags[np.where(mask)[0][np.argmax(np.abs(corr_qt[mask]))]]

print("\nLag correlations (discharge vs):")
for lag in targets:
    print(f"  lag={lag:2d}h  precip r={r_p[lag]:.4f}  temp r={r_t[lag]:.4f}")
print(f"  Best precip lag: {best_p}h (r={corr_qp[np.argmin(np.abs(lags - best_p))]:.4f})")
print(f"  Best temp lag:   {best_t}h (r={corr_qt[np.argmin(np.abs(lags - best_t))]:.4f})")

with open('lag_correlation_results.txt', 'w') as f:
    f.write(f"Station: 01646500, Period: {start.date()} to {end.date()}\n")
    f.write(f"Samples: {len(combined)}\n\n")
    for lag in targets:
        f.write(f"lag={lag}h  Q vs Precip r={r_p[lag]:.4f}  Q vs Temp r={r_t[lag]:.4f}\n")
    f.write("\nBest within +/-72h:\n")
    f.write(f"  Precip: lag={best_p}h, r={corr_qp[np.argmin(np.abs(lags - best_p))]:.4f}\n")
    f.write(f"  Temp:   lag={best_t}h, r={corr_qt[np.argmin(np.abs(lags - best_t))]:.4f}\n")

# Cross-correlation plot
fig3, axes3 = plt.subplots(2, 1, figsize=(14, 10))
titles = ['Discharge vs Precipitation', 'Discharge vs Temperature']
for ax, (title, corr) in zip(axes3, zip(titles, [corr_qp, corr_qt])):
    m = np.abs(lags) <= 72
    ax.plot(lags[m], corr[m], color='steelblue')
    ax.axhline(0, color='gray', lw=0.5)
    ax.axvline(0, color='red', ls='--', alpha=0.6)
    ax.set_title(title)
    ax.set_xlabel('Lag (hours)')
    ax.set_ylabel("Pearson's r")
    ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('lag_correlation_plots.png', dpi=150)
plt.close('all')

print("Done")
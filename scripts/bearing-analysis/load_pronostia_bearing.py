# load_pronostia_bearing.py
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

bearing_dir = "../../datasets/datasets/bearings_data/2nd_test"

if not os.path.exists(bearing_dir):
    print(f"Error: {bearing_dir} not found")
    sys.exit(1)

os.makedirs("output", exist_ok=True)

files = sorted([f for f in os.listdir(bearing_dir) if os.path.isfile(os.path.join(bearing_dir, f))])
print(f"Found {len(files)} files: {files[0]} to {files[-1]}")

first_file_path = os.path.join(bearing_dir, files[0])
data_sample = np.loadtxt(first_file_path)
print(f"Data shape: {data_sample.shape}")

def parse_filename_timestamp(filename):
    parts = filename.split('.')
    if len(parts) == 6:
        try:
            year, month, day, hour, minute, second = map(int, parts)
            return pd.Timestamp(year, month, day, hour, minute, second)
        except ValueError:
            return None
    return None

timestamps = []
for f in files:
    ts = parse_filename_timestamp(f)
    if ts:
        timestamps.append(ts)

if len(timestamps) != len(files):
    print(f"Warning: parsed {len(timestamps)} of {len(files)} filenames")
    sys.exit(1)

print(f"\nTime range: {timestamps[0]} to {timestamps[-1]}")
duration_hours = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
print(f"Duration: {duration_hours:.1f} hours")

# compute RMS for all bearings
rms_all_bearings = {0: [], 1: [], 2: [], 3: []}
for f in files:
    data = np.loadtxt(os.path.join(bearing_dir, f))
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    rms_per_channel = np.sqrt(np.mean(data**2, axis=0))
    for ch in range(rms_per_channel.shape[0]):
        rms_all_bearings[ch].append(rms_per_channel[ch])

for ch in rms_all_bearings:
    rms_all_bearings[ch] = np.array(rms_all_bearings[ch])

rms_array = np.array(rms_all_bearings[0])
time_index = np.arange(len(rms_array))

print(f"RMS (Bearing 1): min={rms_array.min():.6f}, max={rms_array.max():.6f}, mean={rms_array.mean():.6f}")

# bearing 1 is the failure case, find where baseline ends
window = max(10, len(rms_array) // 20)
rolling_std = pd.Series(rms_array).rolling(window).std().dropna().values

early_rolling_std = rolling_std[:max(1, len(rolling_std) // 4)]
std_threshold = np.median(early_rolling_std) * 2.0

baseline_end_idx = len(rms_array)
for i, val in enumerate(rolling_std):
    if val > std_threshold:
        baseline_end_idx = i + window - 1
        break

# Use first half of detected baseline as the clean reference
clean_baseline = rms_array[:baseline_end_idx // 2]
baseline_mean = clean_baseline.mean()
baseline_std = clean_baseline.std()
threshold_accel = baseline_mean + 3 * baseline_std

# baseline_region = rms_array[:baseline_end_idx]
# baseline_mean = baseline_region.mean()
# baseline_std = baseline_region.std()
# threshold_accel = baseline_mean + 3 * baseline_std

print(f"Baseline: 0 to index {baseline_end_idx} ({100*baseline_end_idx/len(rms_array):.1f}%)")
print(f"Baseline mean={baseline_mean:.6f}, std={baseline_std:.6f}, threshold={threshold_accel:.6f}")

accel_start_idx = None
for i in range(baseline_end_idx, len(rms_array)):
    if rms_array[i] > threshold_accel:
        accel_start_idx = i
        break

if accel_start_idx is not None:
    pct = 100 * accel_start_idx / len(rms_array)
    rms_max = rms_array.max()
    increase_pct = 100 * (rms_max - baseline_mean) / baseline_mean
    print(f"Acceleration starts at index {accel_start_idx} ({pct:.1f}%)")
    print(f"RMS increase: {baseline_mean:.6f} to {rms_max:.6f} ({increase_pct:.1f}%)")
else:
    print("No clear acceleration phase")

rms_df = pd.DataFrame({
    'timestamp': timestamps,
    'time_index': time_index,
    'rms': rms_array,
})
rms_df.to_csv("output/pronostia_rms_timeseries.csv", index=False)

stats_df = pd.DataFrame([{
    'baseline_mean': baseline_mean,
    'baseline_std': baseline_std,
    'threshold_accel': threshold_accel,
    'baseline_end_idx': baseline_end_idx,
    'accel_start_idx': int(accel_start_idx) if accel_start_idx is not None else -1,
    'total_measurements': len(rms_array),
}])
stats_df.to_csv("output/pronostia_baseline_stats.csv", index=False)

fig, ax = plt.subplots(figsize=(14, 6))
bearing_labels = ['Bearing 1 (failure)', 'Bearing 2', 'Bearing 3', 'Bearing 4']
colors = ['steelblue', 'green', 'crimson', 'orange']
for ch in range(4):
    ax.plot(time_index, rms_all_bearings[ch], linewidth=1.0, color=colors[ch],
            label=bearing_labels[ch], alpha=0.8)
ax.axvline(baseline_end_idx, color='gray', linestyle='--', linewidth=1.0, alpha=0.6)
if accel_start_idx is not None:
    ax.axvline(accel_start_idx, color='gray', linestyle=':', linewidth=1.0, alpha=0.6)
ax.set_xlabel('Measurement index')
ax.set_ylabel('RMS (g)')
ax.set_title('PRONOSTIA 2nd Test - All 4 Bearings RMS Progression')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("output/pronostia_rms_progression.png", dpi=150)
plt.close()

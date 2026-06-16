# data_quality.py
import pandas as pd
import numpy as np
from scipy.stats import iqr as scipy_iqr
from scipy.stats import ttest_ind


def welch_ttest(a, b):
    n1, n2 = len(a), len(b)
    m1, m2 = a.mean(), b.mean()
    s1, s2 = a.std(ddof=1), b.std(ddof=1)
    diff = m2 - m1
    t_stat, p_value = ttest_ind(a, b, equal_var=False)
    num = (s1**2 / n1 + s2**2 / n2)**2
    den = (s1**2 / n1)**2 / (n1 - 1) + (s2**2 / n2)**2 / (n2 - 1)
    df_welch = num / den if den > 0 else n1 + n2 - 2
    return diff, t_stat, df_welch, p_value, m1, m2, s1, s2, n1, n2


def compute_signal_stats(df, numeric_cols):
    result = {}
    for col in numeric_cols:
        if col not in df.columns:
            continue
        s = df[col].dropna()
        result[col] = {
            "mean": round(float(s.mean()), 4),
            "min": round(float(s.min()), 4),
            "max": round(float(s.max()), 4),
            "std": round(float(s.std()), 4),
            "count": int(len(s)),
        }
    return result


def check_completeness(df, numeric_cols):
    total = len(df)
    per_col = {}
    for col in df.columns:
        missing = df[col].isna().sum()
        per_col[col] = {
            "missing_count": int(missing),
            "completeness_pct": round(100.0 * (total - missing) / total, 3) if total > 0 else 0.0,
        }
    overall_cells = total * len(df.columns)
    overall_missing = sum(v["missing_count"] for v in per_col.values())
    overall_pct = round(100.0 * (overall_cells - overall_missing) / overall_cells, 3) if overall_cells > 0 else 0.0
    return {"per_column": per_col, "overall_completeness_pct": overall_pct}


def check_gaps(df, timestamp_col, expected_freq_min, asset_col=None):
    threshold = pd.Timedelta(minutes=expected_freq_min) * 1.5

    if asset_col and asset_col in df.columns:
        assets = df[asset_col].unique()
    else:
        assets = [None]

    all_durations = []
    all_timestamps = []

    for asset in assets:
        if asset is not None:
            ts = df.loc[df[asset_col] == asset, timestamp_col].dropna().sort_values().reset_index(drop=True)
        else:
            ts = df[timestamp_col].dropna().sort_values().reset_index(drop=True)

        if len(ts) < 2:
            continue

        diffs = ts.diff().dropna()
        gaps = diffs[diffs > threshold]
        all_durations.extend((gaps / pd.Timedelta(minutes=1)).round(1).tolist())
        all_timestamps.extend(ts[gaps.index].dt.strftime("%Y-%m-%d %H:%M:%S").tolist())

    return {
        "gap_count": len(all_durations),
        "longest_gap_min": max(all_durations) if all_durations else 0.0,
        "gap_durations_min": sorted(all_durations, reverse=True),
        "gap_timestamps": all_timestamps,
    }


def check_duplicates(df, timestamp_col=None, asset_col=None):
    dup_rows = int(df.duplicated().sum())

    dup_ts = 0
    if timestamp_col and timestamp_col in df.columns:
        if asset_col and asset_col in df.columns:
            dup_ts = int(df.duplicated(subset=[asset_col, timestamp_col]).sum())
        else:
            dup_ts = int(df.duplicated(subset=[timestamp_col]).sum())

    return {
        "duplicate_row_count": dup_rows,
        "duplicate_timestamp_count": dup_ts,
    }


def check_outliers(df, numeric_cols, iqr_multiplier=1.5, asset_col=None):
    result = {}
    for col in numeric_cols:
        if col not in df.columns:
            continue

        if asset_col and asset_col in df.columns:
            outlier_indices = []
            for asset in df[asset_col].unique():
                s = df.loc[df[asset_col] == asset, col].dropna()
                if len(s) == 0:
                    continue
                q1 = float(s.quantile(0.25))
                q3 = float(s.quantile(0.75))
                iq = float(scipy_iqr(s))
                lower = q1 - iqr_multiplier * iq
                upper = q3 + iqr_multiplier * iq
                outlier_mask = (s < lower) | (s > upper)
                outlier_indices.extend(s[outlier_mask].index.tolist())

            s_all = df[col].dropna()
            n_outliers = len(set(outlier_indices))
            result[col] = {
                "method": "per-asset IQR",
                "outlier_count": n_outliers,
                "outlier_pct": round(100.0 * n_outliers / len(s_all), 3) if len(s_all) > 0 else 0.0,
            }
        else:
            s = df[col].dropna()
            if len(s) == 0:
                continue
            q1 = float(s.quantile(0.25))
            q3 = float(s.quantile(0.75))
            iq = float(scipy_iqr(s))
            lower = q1 - iqr_multiplier * iq
            upper = q3 + iqr_multiplier * iq
            outlier_mask = (s < lower) | (s > upper)
            n_outliers = int(outlier_mask.sum())
            result[col] = {
                "method": "global IQR",
                "q1": round(q1, 4),
                "q3": round(q3, 4),
                "iqr": round(iq, 4),
                "lower_fence": round(lower, 4),
                "upper_fence": round(upper, 4),
                "outlier_count": n_outliers,
                "outlier_pct": round(100.0 * n_outliers / len(s), 3),
            }

    return result


def check_timestamp_regularity(df, timestamp_col, expected_freq_min):
    ts = df[timestamp_col].dropna().sort_values().reset_index(drop=True)
    if len(ts) < 2:
        return {"irregular_count": 0, "irregularity_rate_pct": 0.0, "median_interval_min": None}

    diffs_min = ts.diff().dropna() / pd.Timedelta(minutes=1)
    diffs_min = diffs_min[diffs_min > 0]
    expected = expected_freq_min
    tolerance = expected * 0.1  # 10% tolerance
    irregular = ((diffs_min - expected).abs() > tolerance).sum()
    median_interval = round(float(diffs_min.median()), 3)

    return {
        "expected_freq_min": expected_freq_min,
        "median_interval_min": median_interval,
        "irregular_count": int(irregular),
        "irregularity_rate_pct": round(100.0 * irregular / len(diffs_min), 3),
    }



def check_unit_consistency(df, asset_col, pressure_cols):
    if not pressure_cols or asset_col not in df.columns:
        return {"checked": False, "flagged_assets": {}}

    flagged = {}
    for col in pressure_cols:
        if col not in df.columns:
            continue
        asset_means = df.groupby(asset_col)[col].mean()
        group_median = asset_means.median()
        if group_median == 0:
            continue
        ratios = asset_means / group_median
        for asset_id, ratio in ratios.items():
            if ratio > 10 or ratio < 0.1:
                if asset_id not in flagged:
                    flagged[asset_id] = {}
                flagged[asset_id][col] = round(float(ratio), 2)

    return {"checked": True, "flagged_assets": flagged}



def assess_quality(df: pd.DataFrame, config: dict) -> dict:
    timestamp_col = config.get("timestamp_col")
    asset_col = config.get("asset_col")
    expected_freq_min = config.get("expected_freq_min")
    iqr_multiplier = config.get("iqr_multiplier", 1.5)
    pressure_cols = config.get("pressure_cols", [])

    numeric_cols = config.get("numeric_cols")
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    report = {}

    report["row_count"] = len(df)
    report["column_count"] = len(df.columns)

    report["completeness"] = check_completeness(df, numeric_cols)

    if timestamp_col and expected_freq_min:
        report["gaps"] = check_gaps(df, timestamp_col, expected_freq_min, asset_col=asset_col)
        report["timestamp_regularity"] = check_timestamp_regularity(df, timestamp_col, expected_freq_min)
    else:
        report["gaps"] = {"skipped": "timestamp_col or expected_freq_min not provided"}
        report["timestamp_regularity"] = {"skipped": "timestamp_col or expected_freq_min not provided"}

    report["duplicates"] = check_duplicates(df, timestamp_col, asset_col)

    report["outliers"] = check_outliers(df, numeric_cols, iqr_multiplier, asset_col)

    report["unit_consistency"] = check_unit_consistency(df, asset_col, pressure_cols)

    report["signal_stats"] = compute_signal_stats(df, numeric_cols)

    return report


def format_report(report: dict) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("DATA QUALITY REPORT")
    lines.append("=" * 60)
    lines.append(f"Rows: {report['row_count']:,}    Columns: {report['column_count']}")

    lines.append("\n--- Completeness ---")
    lines.append(f"Overall: {report['completeness']['overall_completeness_pct']}%")
    for col, v in report['completeness']['per_column'].items():
        if v['missing_count'] > 0:
            lines.append(f"  {col}: {v['completeness_pct']}%  ({v['missing_count']} missing)")

    lines.append("\n--- Duplicates ---")
    d = report['duplicates']
    lines.append(f"  Duplicate rows: {d['duplicate_row_count']}")
    lines.append(f"  Duplicate timestamps (per asset): {d['duplicate_timestamp_count']}")

    lines.append("\n--- Gaps ---")
    g = report.get('gaps', {})
    if 'skipped' in g:
        lines.append(f"  Skipped: {g['skipped']}")
    else:
        lines.append(f"  Gap count: {g['gap_count']}")
        lines.append(f"  Longest gap: {g['longest_gap_min']} min")
        if g['gap_durations_min']:
            lines.append(f"  Top 5 gaps (min): {g['gap_durations_min'][:5]}")

    lines.append("\n--- Timestamp Regularity ---")
    tr = report.get('timestamp_regularity', {})
    if 'skipped' in tr:
        lines.append(f"  Skipped: {tr['skipped']}")
    else:
        lines.append(f"  Expected interval: {tr['expected_freq_min']} min")
        lines.append(f"  Median interval: {tr['median_interval_min']} min")
        lines.append(f"  Irregular intervals: {tr['irregular_count']} ({tr['irregularity_rate_pct']}%)")

    lines.append("\n--- Outliers (IQR method) ---")
    for col, v in report['outliers'].items():
        if v['outlier_count'] > 0:
            method = v.get("method", "global IQR")
            if method == "per-asset IQR":
                lines.append(f"  {col}: {v['outlier_count']} outliers ({v['outlier_pct']}%)  [per-asset]")
            else:
                lines.append(f"  {col}: {v['outlier_count']} outliers ({v['outlier_pct']}%)  "
                             f"fences=[{v['lower_fence']}, {v['upper_fence']}]")

    lines.append("\n--- Unit Consistency ---")
    uc = report['unit_consistency']
    if not uc.get('checked'):
        lines.append("  Skipped: no pressure_cols or asset_col provided")
    elif not uc['flagged_assets']:
        lines.append("  No unit mismatches detected")
    else:
        for asset_id, cols in uc['flagged_assets'].items():
            for col, ratio in cols.items():
                lines.append(f"  {asset_id} / {col}: ratio to group median = {ratio}x  [FLAGGED]")

    lines.append("\n--- Signal Statistics ---")
    for col, v in report['signal_stats'].items():
        lines.append(f"  {col:30s}  mean={v['mean']:12.4f}  min={v['min']:12.4f}  "
                     f"max={v['max']:12.4f}  std={v['std']:12.4f}")

    lines.append("=" * 60)
    return "\n".join(lines)

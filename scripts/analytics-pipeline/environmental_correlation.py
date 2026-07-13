# environmental_correlation.py
import pandas as pd

def find_overlap_window(hist_df, env_df, hist_ts_col="timestamp", env_ts_col="timestamp"):
    hist_ts = set(hist_df[hist_ts_col])
    env_ts = set(env_df[env_ts_col])
    overlap_ts = hist_ts & env_ts

    if len(overlap_ts) == 0:
        return None, None, 0

    overlap_ts = sorted(list(overlap_ts))
    return overlap_ts[0], overlap_ts[-1], len(overlap_ts)


def compute_overlap_correlation(hist_df, env_df, hist_col="flow_m3h", env_col="discharge_cfs",
                               hist_ts_col="timestamp", env_ts_col="timestamp"):
    overlap_start, overlap_end, overlap_count = find_overlap_window(
        hist_df, env_df, hist_ts_col, env_ts_col
    )

    if overlap_count == 0:
        return {
            "correlation": None,
            "correlation_str": "N/A",
            "overlap_start": None,
            "overlap_end": None,
            "overlap_count": 0,
            "overlap_pct": 0.0,
            "message": "No overlapping timestamps between historian and environmental data",
            "data_available": False,
        }

    merge_df = pd.merge(
        hist_df[[hist_ts_col, hist_col]],
        env_df[[env_ts_col, env_col]],
        left_on=hist_ts_col,
        right_on=env_ts_col,
        how="inner"
    )

    if len(merge_df) == 0:
        return {
            "correlation": None,
            "correlation_str": "N/A",
            "overlap_start": overlap_start,
            "overlap_end": overlap_end,
            "overlap_count": 0,
            "overlap_pct": 0.0,
            "message": "No aligned rows after merge",
            "data_available": False,
        }

    corr = merge_df[hist_col].corr(merge_df[env_col])
    hist_total = len(hist_df)
    overlap_pct = 100.0 * len(merge_df) / hist_total if hist_total > 0 else 0.0

    return {
        "correlation": round(float(corr), 3) if not pd.isna(corr) else None,
        "correlation_str": f"{float(corr):.3f}" if not pd.isna(corr) else "N/A",
        "overlap_start": overlap_start,
        "overlap_end": overlap_end,
        "overlap_count": len(merge_df),
        "overlap_pct": round(overlap_pct, 1),
        "message": f"Correlation computed on {len(merge_df):,} rows ({overlap_pct:.1f}% of historian). Period: {overlap_start.strftime('%Y-%m-%d')} to {overlap_end.strftime('%Y-%m-%d')}",
        "data_available": True,
    }
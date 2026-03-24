"""
Drift detection for Credit Risk model inputs.

This module compares a baseline dataset (training/known-good) against a
rolling window of recent inference inputs and computes drift metrics.

Current implementation focuses on:
- Numerical feature drift via Population Stability Index (PSI)
- Missingness drift (difference in missing-rate)

Run:
  python -m src.monitoring.drift_detection

Environment variables:
  - DRIFT_BASELINE_CSV: path to baseline CSV (default: home-credit-default-risk/data/processed/consolidated_features.csv)
  - DRIFT_CURRENT_CSV:  path to current window CSV (default: data/monitoring/inference_window.csv)
  - DRIFT_FEATURES:     optional comma-separated feature list to evaluate
  - DRIFT_BINS:         histogram bins for PSI (default: 10)
  - DRIFT_OUTPUT_JSON:  output report path (default: data/monitoring/drift_report.json)
  - DRIFT_OUTPUT_CSV:   optional per-feature metrics CSV path
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional
import json
import os

import numpy as np
import pandas as pd


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _default_repo_root() -> Path:
    # src/monitoring/drift_detection.py -> repo root
    return Path(__file__).resolve().parents[2]


def _read_csv_safely(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    return pd.read_csv(path)


def _parse_features_env(value: str | None) -> list[str]:
    if not value:
        return []
    return [f.strip() for f in value.split(",") if f.strip()]


def _infer_feature_list(baseline_df: pd.DataFrame, current_df: pd.DataFrame) -> list[str]:
    # Exclude common non-features
    exclude = {"TARGET", "SK_ID_CURR", "timestamp"}
    common = [c for c in baseline_df.columns if c in current_df.columns and c not in exclude]
    # Keep only numeric columns (PSI implementation assumes numeric)
    numeric = [c for c in common if pd.api.types.is_numeric_dtype(baseline_df[c])]
    return numeric


def _to_numeric(series: pd.Series) -> pd.Series:
    # Convert to numeric; non-parsable values become NaN
    return pd.to_numeric(series, errors="coerce")


def _missing_rate(series: pd.Series) -> float:
    s = _to_numeric(series)
    return float(s.isna().mean())


def _psi_from_arrays(
    baseline: np.ndarray,
    current: np.ndarray,
    bins: int = 10,
    eps: float = 1e-6,
) -> float:
    """
    Population Stability Index (PSI).

    PSI = sum((p_i - q_i) * ln(p_i / q_i))
    where p_i is baseline bin proportion and q_i is current bin proportion.
    """
    baseline = baseline.astype(float)
    current = current.astype(float)

    baseline = baseline[~np.isnan(baseline)]
    current = current[~np.isnan(current)]

    if baseline.size == 0 or current.size == 0:
        return float("nan")

    # Use baseline quantile bins to get robust binning
    try:
        quantiles = np.linspace(0, 1, bins + 1)
        edges = np.quantile(baseline, quantiles)
        edges = np.unique(edges)
        if edges.size < 3:
            # Not enough variation; treat as no drift if both are nearly constant
            return 0.0
    except Exception:
        # Fallback to min/max bins
        edges = np.linspace(np.min(baseline), np.max(baseline), bins + 1)
        edges = np.unique(edges)
        if edges.size < 3:
            return 0.0

    # Ensure last edge includes max
    edges[0] = -np.inf
    edges[-1] = np.inf

    base_counts, _ = np.histogram(baseline, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)

    base_prop = base_counts / max(base_counts.sum(), 1)
    cur_prop = cur_counts / max(cur_counts.sum(), 1)

    # Avoid log(0)
    base_prop = np.clip(base_prop, eps, 1.0)
    cur_prop = np.clip(cur_prop, eps, 1.0)

    psi = np.sum((base_prop - cur_prop) * np.log(base_prop / cur_prop))
    return float(psi)


def compute_feature_metrics(
    baseline_df: pd.DataFrame,
    current_df: pd.DataFrame,
    features: Iterable[str],
    bins: int = 10,
) -> pd.DataFrame:
    rows: list[dict] = []
    for feat in features:
        b = _to_numeric(baseline_df[feat]).to_numpy()
        c = _to_numeric(current_df[feat]).to_numpy()
        rows.append(
            {
                "feature": feat,
                "psi": _psi_from_arrays(b, c, bins=bins),
                "baseline_missing_rate": _missing_rate(baseline_df[feat]),
                "current_missing_rate": _missing_rate(current_df[feat]),
            }
        )
    df = pd.DataFrame(rows)
    df["missing_rate_delta"] = df["current_missing_rate"] - df["baseline_missing_rate"]
    df = df.sort_values(by="psi", ascending=False, na_position="last").reset_index(drop=True)
    return df


def classify_psi(psi: float) -> str:
    if np.isnan(psi):
        return "unknown"
    if psi < 0.1:
        return "no_drift"
    if psi < 0.2:
        return "moderate"
    return "significant"


@dataclass(frozen=True)
class DriftReport:
    generated_at_utc: str
    baseline_csv: str
    current_csv: str
    n_baseline_rows: int
    n_current_rows: int
    n_features: int
    worst_feature: Optional[str]
    worst_psi: Optional[float]
    significant_features: int
    moderate_features: int


def run_drift_check(
    baseline_csv: Path,
    current_csv: Path,
    features: list[str] | None = None,
    bins: int = 10,
) -> tuple[DriftReport, pd.DataFrame]:
    baseline_df = _read_csv_safely(baseline_csv)
    current_df = _read_csv_safely(current_csv)

    if features is None or len(features) == 0:
        features = _infer_feature_list(baseline_df, current_df)

    if not features:
        raise RuntimeError("No comparable numeric features found between baseline and current datasets.")

    metrics_df = compute_feature_metrics(baseline_df, current_df, features, bins=bins)
    metrics_df["psi_level"] = metrics_df["psi"].apply(classify_psi)

    worst_feature = None
    worst_psi = None
    if len(metrics_df) > 0 and not np.isnan(metrics_df.loc[0, "psi"]):
        worst_feature = str(metrics_df.loc[0, "feature"])
        worst_psi = float(metrics_df.loc[0, "psi"])

    report = DriftReport(
        generated_at_utc=_utc_now_iso(),
        baseline_csv=str(baseline_csv),
        current_csv=str(current_csv),
        n_baseline_rows=int(len(baseline_df)),
        n_current_rows=int(len(current_df)),
        n_features=int(len(features)),
        worst_feature=worst_feature,
        worst_psi=worst_psi,
        significant_features=int((metrics_df["psi_level"] == "significant").sum()),
        moderate_features=int((metrics_df["psi_level"] == "moderate").sum()),
    )
    return report, metrics_df


def main() -> int:
    repo_root = _default_repo_root()

    baseline_csv = Path(
        os.getenv(
            "DRIFT_BASELINE_CSV",
            str(repo_root / "home-credit-default-risk" / "data" / "processed" / "consolidated_features.csv"),
        )
    )
    current_csv = Path(os.getenv("DRIFT_CURRENT_CSV", str(repo_root / "data" / "monitoring" / "inference_window.csv")))
    features = _parse_features_env(os.getenv("DRIFT_FEATURES"))
    bins = int(os.getenv("DRIFT_BINS", "10"))

    out_json = Path(os.getenv("DRIFT_OUTPUT_JSON", str(repo_root / "data" / "monitoring" / "drift_report.json")))
    out_csv = os.getenv("DRIFT_OUTPUT_CSV")
    out_csv_path = Path(out_csv) if out_csv else None

    report, metrics_df = run_drift_check(
        baseline_csv=baseline_csv,
        current_csv=current_csv,
        features=features if features else None,
        bins=bins,
    )

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    if out_csv_path is not None:
        out_csv_path.parent.mkdir(parents=True, exist_ok=True)
        metrics_df.to_csv(out_csv_path, index=False)

    # Console summary
    print("=== DRIFT REPORT ===")
    print(json.dumps(asdict(report), indent=2))
    print("\nTop drifting features:")
    print(metrics_df.head(10).to_string(index=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


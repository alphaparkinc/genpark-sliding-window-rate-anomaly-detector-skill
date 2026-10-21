"""Sliding Window Rate Anomaly Detector.
100% Python Standard Library.
"""
import math
import time
from typing import Dict, Any, List, Optional, Tuple

class SlidingWindowRateAnomalyDetector:
    """Real-time streaming sliding-window anomaly and burst detector using z-score and EWMA."""
    def __init__(self, default_window_seconds: float = 60.0, default_z_threshold: float = 3.0, alpha: float = 0.3):
        self.default_window_seconds = default_window_seconds
        self.default_z_threshold = default_z_threshold
        self.alpha = alpha
        self.streams: Dict[str, List[Tuple[float, float]]] = {}
        self.ewma: Dict[str, float] = {}

    def record_event(self, metric_name: str, value: float, timestamp: Optional[float] = None) -> Dict[str, Any]:
        ts = timestamp if timestamp is not None else time.time()
        if metric_name not in self.streams:
            self.streams[metric_name] = []
            self.ewma[metric_name] = value
        else:
            self.ewma[metric_name] = self.alpha * value + (1.0 - self.alpha) * self.ewma[metric_name]

        self.streams[metric_name].append((ts, value))
        return {
            "status": "recorded",
            "metric": metric_name,
            "value": value,
            "timestamp": ts,
            "current_ewma": round(self.ewma[metric_name], 4)
        }

    def detect_anomaly(self, metric_name: str, window_seconds: Optional[float] = None, z_threshold: Optional[float] = None) -> Dict[str, Any]:
        win = window_seconds or self.default_window_seconds
        z_th = z_threshold or self.default_z_threshold
        now = time.time()

        if metric_name not in self.streams or not self.streams[metric_name]:
            return {"metric": metric_name, "is_anomaly": False, "reason": "No data points"}

        points = [p for p in self.streams[metric_name] if now - p[0] <= win]
        self.streams[metric_name] = points

        if len(points) < 3:
            return {
                "metric": metric_name,
                "is_anomaly": False,
                "data_points_in_window": len(points),
                "reason": "Insufficient samples for statistical confidence"
            }

        values = [p[1] for p in points]
        latest_val = values[-1]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)

        z_score = (latest_val - mean) / std_dev if std_dev > 1e-6 else 0.0
        is_anomaly = abs(z_score) >= z_th

        return {
            "metric": metric_name,
            "latest_value": latest_val,
            "window_seconds": win,
            "data_points_in_window": len(values),
            "mean": round(mean, 4),
            "std_dev": round(std_dev, 4),
            "z_score": round(z_score, 4),
            "z_threshold": z_th,
            "ewma_baseline": round(self.ewma.get(metric_name, mean), 4),
            "is_anomaly": is_anomaly,
            "severity": "CRITICAL" if abs(z_score) >= z_th * 1.5 else ("WARNING" if is_anomaly else "NORMAL")
        }

    def get_metric_summary(self, metric_name: str) -> Dict[str, Any]:
        points = self.streams.get(metric_name, [])
        if not points:
            return {"metric": metric_name, "count": 0}
        vals = [p[1] for p in points]
        vals_sorted = sorted(vals)
        n = len(vals)
        return {
            "metric": metric_name,
            "count": n,
            "min": vals_sorted[0],
            "max": vals_sorted[-1],
            "median": vals_sorted[n // 2],
            "ewma": round(self.ewma.get(metric_name, 0.0), 4)
        }

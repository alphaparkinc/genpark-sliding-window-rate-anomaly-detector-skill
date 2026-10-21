"""Example usage for GenPark Sliding Window Rate Anomaly Detector."""
from client import SlidingWindowRateAnomalyDetector
import time

def main():
    detector = SlidingWindowRateAnomalyDetector()
    now = time.time()
    print("Recording normal baseline token rate (~100 tokens/sec)...")
    for i in range(12):
        detector.record_event("token_rate", 100.0 + (i % 3), timestamp=now - (12 - i))

    check = detector.detect_anomaly("token_rate", window_seconds=20)
    print("Baseline Anomaly Status:", check["is_anomaly"], "| Z-Score:", check["z_score"])

    print("
Simulating massive burst spike (500 tokens/sec)...")
    detector.record_event("token_rate", 500.0, timestamp=now)
    spike = detector.detect_anomaly("token_rate", window_seconds=20)
    print("Spike Anomaly Status:", spike["is_anomaly"], "| Severity:", spike["severity"], "| Z-Score:", spike["z_score"])

if __name__ == "__main__":
    main()

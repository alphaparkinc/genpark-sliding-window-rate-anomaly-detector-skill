"""MCP Stdio Server for Sliding Window Rate Anomaly Detector.
100% Python Standard Library.
"""
import sys
import json
from client import SlidingWindowRateAnomalyDetector

detector = SlidingWindowRateAnomalyDetector()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-sliding-window-rate-anomaly-detector-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "record_event",
                "description": "Ingest metric data point into real-time sliding window",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "metric_name": {"type": "string"},
                        "value": {"type": "number"},
                        "timestamp": {"type": "number"}
                    },
                    "required": ["metric_name", "value"]
                }
            },
            {
                "name": "detect_anomaly",
                "description": "Calculate statistical z-score, variance, and EWMA deviation anomaly alerts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "metric_name": {"type": "string"},
                        "window_seconds": {"type": "number"},
                        "z_threshold": {"type": "number"}
                    },
                    "required": ["metric_name"]
                }
            },
            {
                "name": "get_metric_summary",
                "description": "Get summary metrics, percentiles, and EWMA baseline",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "metric_name": {"type": "string"}
                    },
                    "required": ["metric_name"]
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "record_event":
            out = detector.record_event(args.get("metric_name"), float(args.get("value", 0.0)), args.get("timestamp"))
        elif name == "detect_anomaly":
            out = detector.detect_anomaly(args.get("metric_name"), args.get("window_seconds"), args.get("z_threshold"))
        elif name == "get_metric_summary":
            out = detector.get_metric_summary(args.get("metric_name"))
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()

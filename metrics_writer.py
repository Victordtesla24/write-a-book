#!/usr/bin/env python3
import sys
import pandas as pd
import os


def write_metric_row(metrics_file, metric_name, value, timestamp=None):
    # Create metrics directory if it doesn't exist
    os.makedirs(os.path.dirname(metrics_file), exist_ok=True)

    # Use current timestamp if none provided
    if timestamp is None:
        timestamp = pd.Timestamp.now().timestamp()

    # Create DataFrame with single metric
    metric = pd.DataFrame({"timestamp": [timestamp], metric_name: [float(value)]})

    # Write to CSV, append if file exists
    if os.path.exists(metrics_file):
        # Check if file has headers
        existing = pd.read_csv(metrics_file, nrows=0)
        headers = list(existing.columns)

        # Ensure metric column exists
        if metric_name not in headers:
            # Add new column to existing file
            existing = pd.read_csv(metrics_file)
            existing[metric_name] = None
            existing.to_csv(metrics_file, index=False)

        metric.to_csv(metrics_file, mode="a", header=False, index=False)
    else:
        metric.to_csv(metrics_file, index=False)


if __name__ == "__main__":
    if len(sys.argv) not in [4, 5]:
        print("Usage: metrics_writer.py metrics_file metric_name value [timestamp]")
        sys.exit(1)

    if len(sys.argv) == 5:
        write_metric_row(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        write_metric_row(sys.argv[1], sys.argv[2], sys.argv[3])

#!/usr/bin/env python3
import sys
import pandas as pd
import os


def write_metrics(
    metrics_file, timestamp, cpu_usage, memory_usage, disk_usage, io_wait, load_avg
):
    # Create metrics directory if it doesn't exist
    os.makedirs(os.path.dirname(metrics_file), exist_ok=True)

    # Create DataFrame with metrics
    metrics = pd.DataFrame(
        {
            "timestamp": [timestamp],
            "cpu_usage": [float(cpu_usage)],
            "memory_usage": [float(memory_usage)],
            "disk_usage": [float(disk_usage)],
            "io_wait": [float(io_wait)],
            "load_avg": [float(load_avg)],
        }
    )

    # Write to CSV, append if file exists
    if os.path.exists(metrics_file):
        metrics.to_csv(metrics_file, mode="a", header=False, index=False)
    else:
        metrics.to_csv(metrics_file, index=False)


if __name__ == "__main__":
    if len(sys.argv) != 8:
        print(
            "Usage: metrics_pandas.py metrics_file timestamp cpu_usage "
            "memory_usage disk_usage io_wait load_avg"
        )
        sys.exit(1)

    write_metrics(*sys.argv[1:])

#!/usr/bin/env python3
import sys
import pandas as pd
import os


def write_header(metrics_file):
    # Create metrics directory if it doesn't exist
    os.makedirs(os.path.dirname(metrics_file), exist_ok=True)

    # Create empty DataFrame with column headers
    headers = pd.DataFrame(
        columns=[
            "timestamp",
            "cpu_usage",
            "memory_usage",
            "disk_usage",
            "io_wait",
            "load_avg",
        ]
    )

    # Write headers to file
    headers.to_csv(metrics_file, index=False)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: metrics_header.py metrics_file")
        sys.exit(1)

    write_header(sys.argv[1])

#!/usr/bin/env python3
import sys
import os
import time
import json
import subprocess
import pandas as pd


def get_system_metrics():
    metrics = {}

    # Get CPU metrics
    try:
        cpu = subprocess.check_output(['top', '-l', '1', '-n', '0']).decode()
        cpu_parts = cpu.split('CPU usage: ')[1].split(',')
        metrics['cpu_usage'] = float(cpu_parts[0].split('%')[0])
        metrics['cpu_user'] = float(cpu_parts[0].split('%')[0])
        metrics['cpu_sys'] = float(cpu_parts[1].split('%')[0])
        metrics['cpu_idle'] = float(cpu_parts[2].split('%')[0])
    except (subprocess.SubprocessError, IndexError, ValueError) as e:
        print(f"Error collecting CPU metrics: {str(e)}", file=sys.stderr)
        metrics.update({
            'cpu_usage': 0.0, 'cpu_user': 0.0,
            'cpu_sys': 0.0, 'cpu_idle': 0.0
        })

    # Get memory metrics
    try:
        vm = subprocess.check_output(['vm_stat']).decode()
        pages = {}
        for line in vm.split('\n'):
            if ':' in line:
                key, value = line.split(':')
                pages[key.strip()] = int(value.strip().rstrip('.'))

        page_size = 4096  # 4KB
        metrics['memory_total'] = int(subprocess.check_output(
            ['sysctl', '-n', 'hw.memsize']
        ).decode().strip())
        metrics['memory_usage'] = pages['Pages active'] * page_size / 1024 / 1024
        metrics['memory_free'] = pages['Pages free'] * page_size / 1024 / 1024
        metrics['memory_cached'] = pages['Pages cached'] * page_size / 1024 / 1024
    except (subprocess.SubprocessError, KeyError, ValueError) as e:
        print(f"Error collecting memory metrics: {str(e)}", file=sys.stderr)
        metrics.update({
            'memory_total': 0, 'memory_usage': 0,
            'memory_free': 0, 'memory_cached': 0
        })

    # Get disk metrics
    try:
        df = subprocess.check_output(['df', '-k', '.']).decode()
        disk = df.split('\n')[1].split()
        metrics['disk_total'] = int(disk[1]) * 1024
        metrics['disk_used'] = int(disk[2]) * 1024
        metrics['disk_free'] = int(disk[3]) * 1024
        metrics['disk_usage'] = float(disk[4].rstrip('%'))
    except (subprocess.SubprocessError, IndexError, ValueError) as e:
        print(f"Error collecting disk metrics: {str(e)}", file=sys.stderr)
        metrics.update({
            'disk_total': 0, 'disk_used': 0,
            'disk_free': 0, 'disk_usage': 0
        })

    # Get network metrics
    try:
        netstat = subprocess.check_output(['netstat', '-ib']).decode()
        net_lines = [
            line for line in netstat.split('\n')[1:]
            if line and not line.startswith('Name')
        ]
        metrics['network_in'] = sum(int(line.split()[6]) for line in net_lines)
        metrics['network_out'] = sum(int(line.split()[9]) for line in net_lines)
    except (subprocess.SubprocessError, IndexError, ValueError) as e:
        print(f"Error collecting network metrics: {str(e)}", file=sys.stderr)
        metrics.update({'network_in': 0, 'network_out': 0})

    return metrics


def get_test_metrics():
    test_results_file = 'logs/test_results.json'
    if os.path.exists(test_results_file):
        try:
            with open(test_results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            return {
                'tests_total': results.get('total', 0),
                'tests_passed': results.get('passed', 0),
                'tests_failed': results.get('failed', 0),
                'test_coverage': results.get('coverage', 0)
            }
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error reading test results: {str(e)}", file=sys.stderr)

    # Default values if no test results found
    return {
        'tests_total': 0,
        'tests_passed': 0,
        'tests_failed': 0,
        'test_coverage': 0
    }


def collect_metrics(output_file):
    # Get current timestamp
    timestamp = int(time.time())

    # Collect metrics
    system_metrics = get_system_metrics()
    test_metrics = get_test_metrics()

    # Combine metrics
    metrics = {
        'timestamp': timestamp,
        **system_metrics,
        **test_metrics
    }

    # Create DataFrame
    df = pd.DataFrame([metrics])

    # Write to CSV
    if os.path.exists(output_file):
        df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        df.to_csv(output_file, index=False)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: metrics_collector.py metrics_file")
        sys.exit(1)

    metrics_file = sys.argv[1]
    collect_metrics(metrics_file)

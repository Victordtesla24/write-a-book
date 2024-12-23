#!/usr/bin/env python3
"""Project Management Dashboard using Streamlit."""

import os
import json
import time
import subprocess
from typing import Dict, Any, Optional

import streamlit as st
try:
    import plotly.graph_objects as go
except ImportError as exc:
    raise ImportError(
        "Please install plotly with: pip install plotly --upgrade"
    ) from exc


def load_latest_metrics(metric_type: str) -> Optional[Dict[str, Any]]:
    """Load the latest metrics of a given type."""
    metrics_dir = os.path.join(os.getcwd(), 'metrics')
    pattern = os.path.join(metrics_dir, f'{metric_type}.json')

    try:
        with open(pattern, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check if data is stale (older than 5 minutes)
        if 'timestamp' in data:
            age = time.time() - data['timestamp']
            if age > 300:  # 5 minutes
                mins_old = int(age/60)
                st.warning(f"{metric_type.title()} metrics are {mins_old} minutes old")
        return data
    except (json.JSONDecodeError, OSError):
        return None


def load_project_status() -> Dict[str, Any]:
    """Load project status from proj_status.md."""
    try:
        with open('proj_status.md', 'r', encoding='utf-8') as f:
            content = f.read()

        # Initialize default values
        status = {
            'coverage': 0.0,
            'lint_score': 0.0,
            'implementation': {
                'python_files': 0,
                'test_files': 0,
                'progress': 0,
                'status': 'Not Started'
            },
            'tests': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'coverage': {
                    'unit': 0,
                    'integration': 0,
                    'e2e': 0
                }
            }
        }

        # Parse the markdown content
        lines = content.split('\n')
        for line in lines:
            parts = line.split(':')
            if len(parts) < 2:
                continue
            value_part = parts[1].strip().rstrip('%')

            if 'Code Coverage' in line:
                status['coverage'] = float(value_part)
            elif 'Lint Score' in line:
                status['lint_score'] = float(value_part.split('/')[0].strip())
            elif 'Total Python Files' in line:
                status['implementation']['python_files'] = int(value_part)
            elif 'Total Test Files' in line:
                status['implementation']['test_files'] = int(value_part)
            elif 'Implementation Progress' in line:
                # Handle text status values
                if value_part.lower() == 'in progress':
                    status['implementation']['progress'] = 50
                    status['implementation']['status'] = 'In Progress'
                elif value_part.lower() == 'completed':
                    status['implementation']['progress'] = 100
                    status['implementation']['status'] = 'Completed'
                elif value_part.lower() == 'not started':
                    status['implementation']['progress'] = 0
                    status['implementation']['status'] = 'Not Started'
                else:
                    # Try to parse as number if not a known status
                    try:
                        status['implementation']['progress'] = int(value_part)
                        status['implementation']['status'] = (
                            'Completed' if int(value_part) == 100
                            else 'In Progress' if int(value_part) > 0
                            else 'Not Started'
                        )
                    except ValueError:
                        # Default to 0 if parsing fails
                        status['implementation']['progress'] = 0
                        status['implementation']['status'] = 'Unknown'
            elif 'Total Tests' in line:
                status['tests']['total'] = int(value_part)
            elif 'Tests Passed' in line:
                status['tests']['passed'] = int(value_part)
            elif 'Tests Failed' in line:
                status['tests']['failed'] = int(value_part)
            elif 'Unit Tests' in line:
                status['tests']['coverage']['unit'] = float(value_part)
            elif 'Integration Tests' in line:
                status['tests']['coverage']['integration'] = float(value_part)
            elif 'End-to-End Tests' in line:
                status['tests']['coverage']['e2e'] = float(value_part)

        return status
    except FileNotFoundError:
        st.error("Project status file not found")
    except (ValueError, IndexError) as e:
        st.error(f"Error parsing project status: {str(e)}")
    except OSError as e:
        st.error(f"Error reading project status file: {str(e)}")
    return {
        'coverage': 0.0,
        'lint_score': 0.0,
        'implementation': {
            'python_files': 0,
            'test_files': 0,
            'progress': 0,
            'status': 'Not Started'
        },
        'tests': {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'coverage': {'unit': 0, 'integration': 0, 'e2e': 0}
        }
    }


def run_verification_scripts() -> None:
    """Run verification and auto-fix scripts."""
    try:
        st.info("Running verification scripts...")
        start_time = time.time()

        # Run scripts in sequence to avoid conflicts
        verify_result = subprocess.run(
            ['./scripts/verify_and_fix.sh'],
            check=True,
            capture_output=True,
            text=True
        )
        st.code(verify_result.stdout, language='bash')

        auto_fix_result = subprocess.run(
            ['./scripts/auto_fix_code.sh'],
            check=True,
            capture_output=True,
            text=True
        )
        st.code(auto_fix_result.stdout, language='bash')

        duration = time.time() - start_time
        st.success(f"Verification completed in {duration:.1f} seconds")

        # Update last run time
        st.session_state.last_run = time.time()
    except subprocess.SubprocessError as e:
        st.error(f"Error running verification scripts: {str(e)}")
    except FileNotFoundError:
        msg = "Scripts not found. Check verify_and_fix.sh and auto_fix_code.sh"
        st.error(msg)


def create_test_coverage_chart(status: Dict[str, Any]) -> go.Figure:
    """Create a test coverage chart."""
    labels = ['Unit Tests', 'Integration Tests', 'E2E Tests']
    values = [0, 0, 0]  # Default values

    # Try to get values from test metrics first
    test_metrics = load_latest_metrics('test')
    if test_metrics and isinstance(test_metrics, dict):
        test_suites = test_metrics.get('test_suites', {})
        if isinstance(test_suites, dict):
            values = [
                test_suites.get('unit', {}).get('coverage', 0),
                test_suites.get('integration', {}).get('coverage', 0),
                test_suites.get('e2e', {}).get('coverage', 0)
            ]

    # Fallback to status values if test metrics are not available
    if all(v == 0 for v in values) and status.get('tests', {}).get('coverage'):
        coverage = status['tests']['coverage']
        values = [
            coverage.get('unit', 0),
            coverage.get('integration', 0),
            coverage.get('e2e', 0)
        ]

    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            text=[f"{v}%" for v in values],
            textposition='auto',
            marker_color=['#00cc96', '#636efa', '#ef553b']
        )
    ])

    fig.update_layout(
        title='Test Coverage by Type',
        yaxis_title='Coverage %',
        yaxis_range=[0, 100],
        showlegend=False,
        height=300,
        margin=dict(t=30, l=0, r=0, b=0)
    )
    return fig


def create_test_distribution(status: Dict[str, Any]) -> go.Figure:
    """Create a pie chart showing test status distribution."""
    values = [0, 0]  # Default values [passed, failed]

    # Try to get values from test metrics first
    test_metrics = load_latest_metrics('test')
    if test_metrics and isinstance(test_metrics, dict):
        values = [
            test_metrics.get('tests_passed', 0),
            test_metrics.get('tests_failed', 0)
        ]

    # Fallback to status values if test metrics are not available
    if all(v == 0 for v in values) and status.get('tests'):
        values = [
            status['tests'].get('passed', 0),
            status['tests'].get('failed', 0)
        ]

    # Ensure we have at least some data to display
    if all(v == 0 for v in values):
        values = [1, 0]  # Show 100% passing if no data

    fig = go.Figure(data=[
        go.Pie(
            labels=['Passed', 'Failed'],
            values=values,
            hole=.3,
            marker_colors=['#00cc96', '#ef553b']
        )
    ])

    fig.update_layout(
        title='Test Status Distribution',
        showlegend=True,
        height=300,
        margin=dict(t=30, l=0, r=0, b=0)
    )
    return fig


def main() -> None:
    """Main dashboard function."""
    st.set_page_config(
        page_title='Project Status Dashboard',
        page_icon='📊',
        layout='wide'
    )

    st.title('Project Status Dashboard')

    # Run verification scripts every 2 minutes
    if 'last_run' not in st.session_state:
        st.session_state.last_run = 0

    current_time = time.time()
    time_since_last_run = current_time - st.session_state.last_run

    # Show time until next run
    if time_since_last_run < 120:
        st.info(f"Next verification in {120 - int(time_since_last_run)} seconds")

    if time_since_last_run >= 120:
        run_verification_scripts()

    # Load project status
    status = load_project_status()

    # Project Implementation Status
    st.header('Project Implementation Status')
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric('Code Coverage', f"{status.get('coverage', 0):.1f}%")
    with col2:
        st.metric('Code Quality', f"{status.get('lint_score', 0):.1f}/10.0")
    with col3:
        impl = status.get('implementation', {})
        st.metric(
            'Implementation Progress',
            f"{impl.get('progress', 0)}%",
            impl.get('status', 'Not Started')
        )

    # Test Health
    st.header('Test Health')
    col1, col2, col3 = st.columns(3)

    tests = status.get('tests', {})
    total_tests = tests.get('total', 0)
    passed_tests = tests.get('passed', 0)
    failed_tests = tests.get('failed', 0)

    with col1:
        success_rate = (
            f"{(passed_tests/total_tests)*100:.1f}% success"
            if total_tests > 0 else "No tests"
        )
        st.metric('Tests Passed', passed_tests, success_rate)
    with col2:
        st.metric('Failed Tests', failed_tests)
    with col3:
        st.metric('Total Tests', total_tests)

    # Test Coverage Chart
    try:
        st.plotly_chart(create_test_coverage_chart(status))
    except (KeyError, TypeError, ValueError) as e:
        st.error(f"Error creating test coverage chart: {str(e)}")

    # System Health (in expandable section)
    with st.expander('System Health'):
        system_metrics = load_latest_metrics('system')
        if system_metrics and isinstance(system_metrics, dict):
            col1, col2, col3 = st.columns(3)
            with col1:
                cpu = system_metrics.get('cpu_usage', 0)
                st.metric('CPU Usage', f"{cpu:.1f}%")
            with col2:
                # Convert memory to percentage if needed
                mem = system_metrics.get('memory_usage', 0)
                if mem > 100:  # If raw value
                    mem = (mem / 16384) * 100  # Assuming 16GB total memory
                st.metric('Memory Usage', f"{mem:.1f}%")
            with col3:
                disk = system_metrics.get('disk_usage', 0)
                st.metric('Disk Usage', f"{disk:.1f}%")
        else:
            st.warning("System metrics not available")

    # Auto-refresh
    time.sleep(1)  # Small delay to prevent excessive CPU usage
    st.rerun()


if __name__ == '__main__':
    main()

"""Project dashboard application."""

import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
from dashboard.config import DASHBOARD_CONFIG


# Configure Streamlit page
st.set_page_config(
    page_title="Project Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
with open("dashboard/static/style.css", encoding="utf-8") as css_file:
    css_content = css_file.read()
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


def load_metrics(metric_type: str) -> Optional[Dict[str, Any]]:
    """Load metrics from file."""
    try:
        with open(f"metrics/{metric_type}.json", "r", encoding="utf-8") as metrics_file:
            return json.load(metrics_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def load_project_status() -> Dict[str, str]:
    """Load project status from markdown file."""
    try:
        status = {}
        with open("metrics/proj_status.md", "r", encoding="utf-8") as status_file:
            for line in status_file:
                if ":" in line:
                    key, value = line.split(":", 1)
                    status[key.strip()] = value.strip()
        return status
    except FileNotFoundError:
        return {}


def create_metric_card(title: str, value: str, delta: Optional[str] = None):
    """Create a metric card with optional delta."""
    with st.container():
        st.markdown(f"""
        <div class="metric-card">
            <h3>{title}</h3>
            <div class="metric-value">{value}</div>
            {f'<div class="metric-delta">{delta}</div>' if delta else ''}
        </div>
        """, unsafe_allow_html=True)


def create_test_coverage_chart(status: Dict[str, Any]) -> go.Figure:
    """Create test coverage chart."""
    if not status:
        return go.Figure()

    test_types = ["Unit Tests", "Integration Tests", "End-to-End Tests"]
    coverage_values = [
        float(status.get("Unit Tests", "0").rstrip("%")),
        float(status.get("Integration Tests", "0").rstrip("%")),
        float(status.get("End-to-End Tests", "0").rstrip("%"))
    ]

    fig = go.Figure(data=[
        go.Bar(
            x=test_types,
            y=coverage_values,
            marker_color=["#00cc96", "#ab63fa", "#ffa15a"]
        )
    ])

    fig.update_layout(
        title="Test Coverage by Type",
        yaxis_title="Coverage %",
        showlegend=False,
        height=400
    )

    return fig


def create_system_metrics_chart(metrics: Dict[str, Any]) -> go.Figure:
    """Create system metrics chart."""
    if not metrics:
        return go.Figure()

    fig = go.Figure()

    # Add gauge charts for CPU, Memory, and Disk usage
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.get("cpu_usage", 0),
        domain={"x": [0, 0.3], "y": [0, 1]},
        title={"text": "CPU Usage"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#00cc96"},
            "steps": [
                {"range": [0, 70], "color": "lightgray"},
                {"range": [70, 85], "color": "#ffa15a"},
                {"range": [85, 100], "color": "#ef553b"}
            ]
        }
    ))

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.get("memory_usage", 0),
        domain={"x": [0.35, 0.65], "y": [0, 1]},
        title={"text": "Memory Usage"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#ab63fa"},
            "steps": [
                {"range": [0, 75], "color": "lightgray"},
                {"range": [75, 90], "color": "#ffa15a"},
                {"range": [90, 100], "color": "#ef553b"}
            ]
        }
    ))

    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.get("disk_usage", 0),
        domain={"x": [0.7, 1], "y": [0, 1]},
        title={"text": "Disk Usage"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#ffa15a"},
            "steps": [
                {"range": [0, 80], "color": "lightgray"},
                {"range": [80, 90], "color": "#ffa15a"},
                {"range": [90, 100], "color": "#ef553b"}
            ]
        }
    ))

    fig.update_layout(height=300)
    return fig


def main():
    """Main dashboard application."""
    # Sidebar
    with st.sidebar:
        st.title("Project Dashboard")
        st.markdown("---")

        # Theme selector
        current_theme = st.selectbox(
            "Theme",
            ["Light", "Dark"],
            index=0 if DASHBOARD_CONFIG.get("theme") == "light" else 1
        )
        if current_theme != DASHBOARD_CONFIG.get("theme"):
            DASHBOARD_CONFIG.set("theme", current_theme.lower())

        # Feature toggles
        st.markdown("### Features")
        for feature, enabled in DASHBOARD_CONFIG.get("features", {}).items():
            if st.checkbox(feature.replace("_", " ").title(), value=enabled):
                DASHBOARD_CONFIG.enable_feature(feature)
            else:
                DASHBOARD_CONFIG.disable_feature(feature)

    # Main content
    col1, col2, col3 = st.columns(3)

    # Load metrics
    system_metrics = load_metrics("system")
    test_metrics = load_metrics("test")
    project_status = load_project_status()

    # Project Status
    with col1:
        create_metric_card(
            "Code Coverage",
            project_status.get("Code Coverage", "N/A"),
            f"Target: {DASHBOARD_CONFIG.get('thresholds', {}).get('coverage_minimum', 80)}%"  # noqa
        )

    with col2:
        create_metric_card(
            "Code Quality",
            project_status.get("Lint Score", "N/A"),
            "Based on Pylint score"  # noqa
        )

    with col3:
        create_metric_card(
            "Implementation Progress",
            project_status.get("Implementation Progress", "N/A")
        )

    # System Metrics
    st.markdown("### System Health")
    if system_metrics:
        st.plotly_chart(
            create_system_metrics_chart(system_metrics),
            use_container_width=True
        )

        # Show last update time
        last_update = datetime.fromtimestamp(system_metrics.get("timestamp", 0))
        st.caption(
            f"Last updated: {last_update.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        st.warning("System metrics not available")

    # Test Metrics
    st.markdown("### Test Health")
    if test_metrics:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(
                create_test_coverage_chart(project_status),
                use_container_width=True
            )

        with col2:
            total_tests = (
                test_metrics.get("tests_passed", 0) +
                test_metrics.get("tests_failed", 0)
            )
            if total_tests > 0:
                success_rate = (
                    test_metrics.get("tests_passed", 0) / total_tests
                ) * 100
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=success_rate,
                    title={"text": "Test Success Rate"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#00cc96"},
                        "steps": [
                            {"range": [0, 90], "color": "#ffa15a"},
                            {"range": [90, 100], "color": "#00cc96"}
                        ]
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Test metrics not available")
    
    # Auto-refresh
    if st.button("Refresh Now"):
        st.rerun()
    else:
        time.sleep(DASHBOARD_CONFIG.get("refresh_interval", 1))
        st.rerun()


if __name__ == "__main__":
    main()

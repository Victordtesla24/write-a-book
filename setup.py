"""Setup configuration for the project."""

from setuptools import setup, find_packages

setup(
    name="write-a-book",
    version="0.1.0",
    packages=find_packages() + [''],  # Include root directory modules
    py_modules=['cursor_config'],  # Explicitly include cursor_config.py
    install_requires=[
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "markdown>=3.0.0",
        "psutil>=5.9.0",
        "requests>=2.31.0",
        "coverage>=7.4.0",
        "streamlit>=1.31.0",
        "markdown>=3.5.0",  # Required by template.py
    ],
    python_requires=">=3.8",
)

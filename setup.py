import module."""
import streamlit as st"""setup
from setuptools import find_packages, setup  # type: ignore

setup(
    name="book_editor",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "streamlit>=1.41.1",
        "markdown>=3.7",
        "pygments>=2.18.0",
        "python-dotenv",
        "pytest",
        "pytest-cov",
        "black",
        "isort",
        "flake8",
        "pylint",
        "autopep8",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
            "pylint",
            "autopep8",
        ]
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Streamlit-based book editor with template management",
    keywords="book editor, markdown, templates",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Text Editors :: Text Processing",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)

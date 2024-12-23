"""Setup script for the project."""

from setuptools import setup, find_packages

setup(
    name='write-a-book',
    version='0.1.0',
    description='Project management dashboard with GitHub integration',
    author='Cursor AI',
    author_email='support@cursor.so',
    packages=find_packages(),
    install_requires=[
        'psutil>=5.9.0',
        'requests>=2.31.0',
        'coverage>=7.4.0',
        'pytest>=7.4.0',
        'pytest-cov>=4.1.0',
        'streamlit>=1.31.0',
    ],
    python_requires='>=3.8',
)

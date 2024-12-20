"""Setup configuration for Book Editor package."""

from setuptools import setup, find_packages

setup(
    name="book-editor",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "streamlit>=1.41.1",
        "markdown>=3.7",
        "pygments>=2.18.0",
    ],
    extras_require={
        "dev": [
            "black>=24.1.1",
            "isort>=5.13.2",
            "autopep8>=2.0.4",
            "autoflake>=2.2.1",
            "pylint>=3.0.3",
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

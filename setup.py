"""Setup configuration for Kodezi Chronos research package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="chronos-research",
    version="1.0.0",
    author="Kodezi Inc.",
    author_email="research@kodezi.com",
    description="Research repository for Kodezi Chronos - A Debugging-First Language Model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kodezi/chronos-research",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "scipy>=1.7.0",
        "scikit-learn>=0.24.0",
        "tqdm>=4.62.0",
        "pyyaml>=5.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.6b0",
            "flake8>=3.9.0",
            "mypy>=0.910",
            "pre-commit>=2.13.0",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "notebook>=6.4.0",
            "ipykernel>=6.0.0",
            "plotly>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chronos-benchmark=benchmarks.cli:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/kodezi/chronos-research/issues",
        "Source": "https://github.com/kodezi/chronos-research",
        "Documentation": "https://chronos.kodezi.com",
        "Research Paper": "https://arxiv.org/abs/2507.12482",
    },
)
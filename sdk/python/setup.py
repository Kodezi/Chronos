from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kodezi-chronos",
    version="2025.1.0",
    author="Kodezi",
    author_email="support@kodezi.com",
    description="Python SDK for Kodezi Chronos Autonomous Debugging System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kodezi/chronos-python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Debuggers",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.27.0",
        "aiohttp>=3.8.0",
        "pydantic>=1.10.0",
        "python-dotenv>=0.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "mypy>=0.950",
        ]
    },
    entry_points={
        "console_scripts": [
            "chronos=kodezi_chronos.cli:main",
        ],
    },
)
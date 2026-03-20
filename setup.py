"""
Setup script for the content generator package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="tiktok-content-system",
    version="1.0.0",
    author="Demo Team",
    description="AI-powered TikTok content generation system with script and layout generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sherlock-126/demo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Content Creators",
        "Topic :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "content-generator=content_generator.cli:cli",
            "layout-generator=layout_generator.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "content_generator": ["../templates/*.txt"],
        "layout_generator": ["../config/*.yaml", "../assets/**/*"],
    },
)
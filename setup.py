"""
Setup script for the Tarkov Map Assistant package.
"""
from setuptools import setup, find_packages

setup(
    name="tarkov_app",
    version="1.0.0",
    description="A tool for translating Escape from Tarkov game coordinates to positions on map images",
    author="TarkovProjekt",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "customtkinter>=5.0.0",
        "Pillow>=9.0.0",
        "tksvg>=0.7.0",
    ],
    entry_points={
        "console_scripts": [
            "tarkov-assistant=tarkov_app.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment",
    ],
    python_requires=">=3.8",
)
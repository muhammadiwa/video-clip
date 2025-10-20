"""Setup script for Viral Clip AI Generator."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="viral-clip-generator",
    version="1.0.0",
    author="Muhammad Iwa",
    description="AI-powered tool to generate viral clips from long videos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muhammadiwa/video-clip",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "yt-dlp>=2024.0.0",
        "moviepy>=1.0.3",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "Pillow>=10.0.0",
        "openai>=1.0.0",
        "scenedetect[opencv]>=0.6.0",
        "openai-whisper>=20231117",
        "pydub>=0.25.1",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
        "requests>=2.31.0",
        "click>=8.1.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "viral-clip=cli:cli",
        ],
    },
)

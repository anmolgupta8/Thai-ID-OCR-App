#!/bin/bash

# Install system-level dependencies using the native package manager
# Note: This assumes a Debian-based system; adjust as needed for macOS
apt-get update
apt-get install -y leptonica tesseract

# Install Python dependencies
pip install -r requirements.txt

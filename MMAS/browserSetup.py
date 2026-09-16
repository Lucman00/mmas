import subprocess
import sys

from pathlib import Path

def main():
    """Download Playwright browsers for the mmas tool."""
    print("Downloading Playwright browsers (this may take a few minutes)...")
    try:
        subprocess.check_call([sys.executable, "-m", "playwright", "install"])
        print("Playwright browsers installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Playwright browsers: {e}")
        print("This tool needs Playwright browsers. You can retry manually with: playwright install")
        sys.exit(1)
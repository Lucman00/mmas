from setuptools import setup, find_packages
from pathlib import Path


long_description = (Path(__file__).parent / "README.md").read_text()
setup(
    name='mmas',
    version='3.0.0',
    packages=find_packages(),
    py_modules=['main', 'config'],
    install_requires=[
        'click>=8.0.0',
        'requests>=2.28.0',
        'cryptography>=39.0.0',
        'platformdirs>=4.11.0',
        'playwright>=1.63.0',
        'beautifulsoup4>=4.15.0',
    ],
    entry_points={
        'console_scripts': [
            'mmas=main:cli'
        ],
    },
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
)

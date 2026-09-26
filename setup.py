from setuptools import setup, find_packages

setup(
    name='mmas',
    version='2.5.6',
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
)

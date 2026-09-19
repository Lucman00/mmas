from setuptools import setup, find_packages

setup(
    name='mmas',
    version='2.1.0',
    packages=find_packages(),
    py_modules=['main', 'config', 'browserSetup'],
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
            'mmas=main:cli',
            'mmas-setup=browserSetup:main'
        ],
    },
    include_package_data=True,
)
from setuptools import setup, find_packages

setup(
    name='MMAS',
    version='0.1.0',
    packages=find_packages(),
    py_modules=['main', 'config'],
    package_data={
        '': ['token.json'],
    },
    install_requires=[
        'click>=8.0.0',
        'requests>=2.28.0',
        'cryptography>=39.0.0',
        'python-dotenv>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'MMAS=main:cli',  
        ],
    },
    include_package_data=True,
)
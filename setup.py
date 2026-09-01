from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8") if (here / "README.md").exists() else ""

# Single source version - read from openchart/__init__.py
import re
version = "0.2.0"
init_path = here / "openchart" / "__init__.py"
if init_path.exists():
    match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", init_path.read_text(), re.M)
    if match:
        version = match.group(1)

setup(
    name='openchart',
    version=version,
    description='A Python library to download intraday and EOD historical data from NSE India',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Rajandran R',
    author_email='rajandran@marketcalls.in',
    url='https://github.com/unn-Known1/openchart',
    packages=find_packages(),
    install_requires=[
        'requests>=2.20.0',
        'pandas>=1.3.0',
    ],
    extras_require={
        'dev': ['pytest>=7.0', 'pytest-cov'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    project_urls={
        'Source': 'https://github.com/unn-Known1/openchart',
        'Bug Reports': 'https://github.com/unn-Known1/openchart/issues',
    },
)

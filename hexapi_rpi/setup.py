from setuptools import setup, find_packages


setup(
    name="hexarpi",
    version="0.2",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "hexarpi = hexarpi.rpi:main"]
    }
)

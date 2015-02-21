from setuptools import setup, find_packages


setup(
    name="hexarpi",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "hexarpi = hexarpi.rpi:main"]
    }
)

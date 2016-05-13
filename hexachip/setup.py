from setuptools import setup, find_packages


setup(
    name="hexachip",
    version="0.3",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "hexagui = hexagui.gui:main",
            "hexarpi = hexarpi.rpi:main"]
    },
    package_data={
        'hexagui': ['resources/*'],
    },
    requires=['PyQt5']
)

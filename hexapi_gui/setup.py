from setuptools import setup, find_packages


setup(
    name="hexagui",
    version="0.2",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "hexagui = hexagui.gui:main"]
    },
    package_data={
        'hexagui': ['resources/*'],
    },
    requires=['PyQt5']
)

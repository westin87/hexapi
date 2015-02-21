from setuptools import setup, find_packages


setup(
    name="hexagui",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "mcp = amraatlas.mcp:main"]
    },
    package_data={
        'hexagui': ['resources/*'],
    }, requires=['PyQt5']
)

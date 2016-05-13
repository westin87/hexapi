from setuptools import setup, find_packages


setup(
    name="hexachip",
    version="0.3",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "run-hexagui = hexagui.gui:main",
            "run-hexarpi = hexarpi.rpi:main",
            "test-prototype = hexarpi.tests.integration.test_regulator:main",
            "test-orientation = hexarpi.utils.orientation:main",
            "test-position = hexarpi.utils.position:main"]
    },
    package_data={
        'hexagui': ['resources/*'],
    }
)

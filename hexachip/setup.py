from setuptools import setup, find_packages

setup(
    name="hexachip",
    version="0.4",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "run-hexagui = hexagui.gui:main",
            "run-hexacopter = hexacopter.copter:main",
            "test-prototype = hexacopter.tests.integration.test_regulator:main",
            "test-orientation = hexacopter.utils.orientation:main",
            "test-position = hexacopter.utils.position:main"]
    },
    package_data={
        'hexagui': ['resources/*'],
    }
)

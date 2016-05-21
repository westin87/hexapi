from setuptools import setup


setup(
    name="hexachip",
    version="0.3",
    packages=['hexacommon', 'hexagui', 'hexacoppter'],
    entry_points={
        "console_scripts": [
            "run-hexagui = hexagui.gui:main",
            "run-hexacoppter = hexacoppter.rpi:main",
            "test-prototype = hexacoppter.tests.integration.test_regulator:main",
            "test-orientation = hexacoppter.utils.orientation:main",
            "test-position = hexacoppter.utils.position:main"]
    },
    package_data={
        'hexagui': ['resources/*'],
    }
)

from setuptools import setup


setup(
    name="Hexachip",
    version="0.3",
    packages=['hexacommon', 'hexagui', 'hexarpi'],
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

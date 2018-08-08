from setuptools import setup

setup(
    name = "spotify_tui",
    version = "1.0.0",
    packages = ["spotify_tui"],
    entry_points = {
        "console_scripts": [
            "spotify_tui = spotify_tui.__main__:main"
        ]
    },
    install_requires=[
        "py-applescript",
        "pyobjc"
    ]
)

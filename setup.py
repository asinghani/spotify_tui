from setuptools import setup

setup(
    name = "mac_spotify_terminal",
    version = "1.0.0",
    packages = ["mac_spotify_terminal"],
    entry_points = {
        "console_scripts": [
            "spotify_tui = mac_spotify_terminal.__main__:main"
        ]
    }
)

import sys
from setuptools import setup, find_packages

setup(
    name = "JetBot-Pi",
    version = "1.0",
    packages = find_packages(),
    install_requires = [],
    author = "Diez B. Roggisch",
    author_email = "deets@web.de",
    description = "The Raspberry PI-side of the Jet-Bot project.",
    license = "MIT",
    keywords = "python rasbpberry pi robot",
    entry_points = {
        'console_scripts': [
            'pi-protocol-test = jetbot:pi_protocol_test',
            'protocol-test = jetbot:protocol_test',
            'drive-test = jetbot:drive_test',
            'jetbot-drive = jetbot:jetbot_driver',
            'motor-test = jetbot:motor_test',
        ],
    }
)

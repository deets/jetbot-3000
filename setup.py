import sys
from setuptools import setup, find_packages

setup(
    name = "JetBot 3000",
    version = "1.0",
    packages = find_packages(),
    install_requires = [],
    author = "Diez B. Roggisch",
    author_email = "deets@web.de",
    description = "The Jet-Bot project, an experiment in telepresence-robotics.",
    license = "MIT",
    keywords = "python rasbpberry pi robot",
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        'jetbot.server': [
            'views/*.tpl',
            'static/*.*',
            'static/js/*.*',
            'static/css/*.*',
            'static/fonts/*.*',
        ],
    },
    entry_points = {
        'console_scripts': [
            # commands to be run on the pi
            'pi-protocol-test = jetbot.pi:pi_protocol_test',
            'pi-jetbot-drive = jetbot.pi:jetbot_driver',
            'pi-gui-simulator = jetbot.pi:gui_simulator',
            'pi-motor-test = jetbot.pi:motor_test',
            # commands running on the server/host side
            'protocol-test = jetbot.host:protocol_test',
            'drive-test = jetbot.host:drive_test',
            'server = jetbot.host:server',
        ],
    }
)

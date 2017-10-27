from setuptools import setup, find_packages
from version import __version__
setup(
    name="Momoi Bot",
    version=__version__,
    packages=find_packages(),
    scripts=[],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['aiohttp','asyncio', 'websockets', 'logging'],

    package_data={
        '': {

        },
    },

    # metadata for upload to PyPI
    description="This is my Discord Bot: Momoi Bot",
    license="MIT",
    keywords="discord bot Momoi Generation Miracles",
    url="https://github.com/ShifuYee/Discord-Bot",
)

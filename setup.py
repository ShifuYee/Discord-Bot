from setuptools import setup, find_packages
setup(
    name="Momoi Bot",
    version=open("discord_bot/_version.py").readlines()[-1].split()[-1].strip("\"'"),
    packages=find_packages(),
    scripts=[],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['requests', 'asyncio', 'websockets', 'logging', 'aiohttp'],

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

from setuptools import setup, find_packages
setup(
    name="Momoi Bot",
    version="0.0.1",
    packages=find_packages(),
    scripts=[],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['requests', 'asyncio', 'websockets'],

    package_data={
        '': {},
    },

    # metadata for upload to PyPI
    description="This is my Discord Bot: Momoi Bot",
    license="MIT",
    keywords="discord bot Momoi Generation Miracles",
    url="https://github.com/ShifuYee/Discord-Bot",
)

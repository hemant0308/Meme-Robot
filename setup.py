from setuptools import setup

# List of dependencies installed via `pip install -e .`
# by virtue of the Setuptools `install_requires` value below.
requires = [
    'requests',
    'selenium',
    'lxml',
    'cssselect',
    'Pillow',
    'logging'
]
setup(
    name='meme-robot',
    install_requires=requires,
)
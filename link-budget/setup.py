from setuptools import setup, find_packages

setup(
    name="linkbudget",
    version="0.1",
    author="ASAT Cubesat",
    license="GPL3",
    python_requires='>=3',
    packages=find_packages(),
    install_requires=['astropy', 'pycraf', 'numpy'],
)

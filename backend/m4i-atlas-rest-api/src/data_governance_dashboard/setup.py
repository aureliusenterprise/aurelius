from setuptools import find_packages, setup

setup(
    name="m4i-data-governance-dashboard",
    version="0.1.0",
    url="http://gitlab.com/m4i/models4insight",
    author="Aurelius Enterprise",
    packages=find_packages(),
    install_requires=[
        "m4i_atlas_core",
        "m4i_backend_core",
        "dataclasses-json",
        "pandas",
        "numpy",
        "deepdiff",
        "flask"
    ]
)

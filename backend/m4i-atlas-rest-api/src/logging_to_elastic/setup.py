from setuptools import find_packages, setup

setup(
    name="m4i-logging-to-elastic",
    version="1.0.0",
    author="Aurelius Enterprise",
    packages=find_packages(),
    install_requires=[
        "flask",
        "m4i_atlas_core",
        "m4i_backend_core",
        "elasticsearch"
    ],
    zip_safe=False
)

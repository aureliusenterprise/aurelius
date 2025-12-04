from setuptools import find_packages, setup

setup(
    name="m4i-lineage-model",
    version="1.0.0",
    url="http://gitlab.com/m4i/models4insight",
    author="Aurelius Enterprise",
    packages=find_packages(),
    install_requires=[
        "m4i_atlas_core",
        "m4i_backend_core",
        "flask",
        "pandas",
    ],
    zip_safe=False
)

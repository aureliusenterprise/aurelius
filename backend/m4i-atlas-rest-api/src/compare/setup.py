from setuptools import find_packages, setup

setup(
    name="m4i-compare",
    version="1.0.0",
    url="http://gitlab.com/m4i/models4insight",
    author="Aurelius Enterprise",
    packages=find_packages(),
    install_requires=[
        "flask",
        "m4i-backend-core",
        "numpy",
        "pandas"
    ],
    zip_safe=False
)

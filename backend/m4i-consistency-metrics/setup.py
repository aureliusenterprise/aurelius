from setuptools import find_packages, setup

setup(
    name="m4i-consistency-metrics",
    version="1.0.0",
    url="http://gitlab.com/m4i/models4insight",
    author="Aurelius Enterprise",
    packages=find_packages(),
    install_requires=[
        "bokeh",
        "flask",
        "m4i-backend-core",
        "pandas",
        "requests-cache"
    ],
    zip_safe=False
)

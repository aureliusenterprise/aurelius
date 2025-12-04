from setuptools import find_packages, setup

setup(
    name="m4i-data2model",
    version="1.0.0",
    url="http://gitlab.com/m4i/models4insight",
    author="Aurelius Enterprise",
    packages=find_packages(),
    install_requires=[
        "bokeh",
        "flask",
        "m4i-analytics",
        "numpy",
        "pandas",
        "xlrd"
    ],
    zip_safe=False
)

from setuptools import find_packages, setup

setup(
    name="m4i-backend-core",
    version="1.0.0",
    url="http://gitlab.com/m4i/models4insight",
    author="Aurelius Enterprise",
    packages=find_packages(),
    install_requires=[
        "flask",
        "keycloak-client",
        "python-jose[pycryptodome]",
    ],
    zip_safe=False
)

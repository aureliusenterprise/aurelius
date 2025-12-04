from setuptools import setup, find_packages


setup(
      name="m4i-metrics",
      version = "1.0.0",
      url="http://gitlab.com/m4i/analytics-library-extensions",
      author="Aurelius Enterprise",
      packages=find_packages(),
      install_requires=["future"],
      zip_safe=False
)

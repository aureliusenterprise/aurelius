from setuptools import setup, find_packages


setup(
      name="m4i-graphviz-layouts",
      version = "1.0.0",
      url="http://gitlab.com/m4i/analytics-library",
      author="Aurelius Enterprise",
      packages=find_packages(),
      install_requires=["future", "graphviz", "pydotplus"],
      zip_safe=False
)

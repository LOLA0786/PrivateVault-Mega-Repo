from setuptools import setup, find_packages

setup(
    name="galani",
    version="3.0.0",
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    python_requires=">=3.10",
)

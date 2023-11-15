from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="zermelo_api_vogk",
    version="0.0.7",
    description="A Module to create a Zermelo access token and put data from Zermelo in dataclasses",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/KlaasVogel/zermelo_api_vogk",
    author="KlaasVogel",
    author_email="klaas@klaasvogel.nl",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests"],
    extras_require={
        "dev": [],
    },
    python_requires=">=3.11",
)

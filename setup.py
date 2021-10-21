import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="thespikeapi-michelececcacci",
    version="0.0.1",
    author="Michele Ceccacci",
    author_email="michelececcacci1@gmail.com",
    description="A json api that parses thespike.gg",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/michelececcacci/thespikeapi",
    project_urls={
        "Bug Tracker": "https://github.com/michelececcacci/thespikeapi/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["python", "valorant", "json", "parser", "api", "thespike", "thespike.gg"],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
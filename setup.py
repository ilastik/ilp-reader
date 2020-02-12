from pathlib import Path

from setuptools import find_packages, setup

long_description = Path(".").parent.joinpath("README.md").read_text()

setup(
    name="ilp-reader",
    description=long_description.splitlines()[2].rstrip("."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ilastik/ilp-reader",
    author="ilastik Developers",
    author_email="team@ilastik.org",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    project_urls={
        "Bug Reports": "https://github.com/ilastik/ilp-reader/issues",
        "Source": "https://github.com/ilastik/ilp-reader",
    },
    keywords="ilastik",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=["h5py>=2.10", "numpy>=1.18"],
)

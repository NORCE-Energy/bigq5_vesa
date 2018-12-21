import setuptools

with open("../README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="norce",
    version="0.0.1",
    author="H.H",
    author_email="haha@norceresearch.no",
    description="BigQ5 realization generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NORCE-Energy/bigq5_vesa",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'jsoncomment',
        'numpy',
    ],

)

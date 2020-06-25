import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AL-Logger",
    version="0.2.3",
    author="Sebastian Blaes",
    author_email="sblaes@tue.mpg.de",
    description="Logging experimental data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pandas',
        'tensorboardX',
        'numpy',
        'tables',
        'gitpython',
        'pillow'
      ],
)

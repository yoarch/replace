import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="replacefs",
    version="1.1.1",
    python_requires='>=3',
    author="yoarch",
    author_email="yo.managements@gmail.com",
    description="search and replace tool for strings on the all system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yoarch/replace",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
	"console_scripts": [
	"replacefs = replacefs.replacefs:main",
	"rp = replacefs.replacefs:main"
        ]
    })

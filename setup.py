import setuptools

with open('README.md', 'r', encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="memepack_builder",
    version="0.0.1",
    author="MysticNebula70",
    author_email="alpha5130@outlook.com",
    description="A tool for packaging Memefied Chinese resource pack.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Teahouse-Studios/memepack-builder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ]
)
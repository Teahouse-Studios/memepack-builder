import setuptools

with open('README.md', 'r', encoding='utf8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="memepack_builder",
    version="0.2.0a2",
    author="MysticNebula70",
    author_email="mysticnebula70@teahou.se",
    description="A tool for packaging Memefied Chinese resource pack",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Teahouse-Studios/memepack-builder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.9'
)

# memepack-builder

[![Issues](https://img.shields.io/github/issues/Teahouse-Studios/memepack-builder?logo=github&style=flat-square)](https://github.com/Teahouse-Studios/memepack-builder/issues)    [![Pull requests](https://img.shields.io/github/issues-pr/Teahouse-Studios/memepack-builder?logo=github&style=flat-square)](https://github.com/Teahouse-Studios/memepack-builder/pulls)    [![License](https://img.shields.io/static/v1?label=License&message=Apache-2.0&color=db2331&style=flat-square&logo=apache)](http://www.apache.org/licenses/LICENSE-2.0)

[简体中文](./doc/README.zh-hans.md)

A tool for packaging Memefied Chinese resource pack for Minecraft.

This is the source code repository of PyPI package `memepack-builder`. It's not intended for production use. Please use `pip install memepack-builder` to install the package.

This package has no dependencies.

This package requires Python 3.9 or above.

## Usage

This package can be invoked by other Python programs, or run from command line interface.

### Used as library

The package provides four classes: `PlatformChecker`, `ModuleChecker`, `JEPackBuilder` and `BEPackBuilder`. In a simple build (which is the most case), just import the module checker and one of the two builders, and call `build()`. The build log is stored as a list in the builder's `build_log` property. Use `'\n'.join()` if you prefer string.

### Used in CLI

When called in CLI (i.e. `python -m memepack_builder`), the package will ask for proper arguments, and build the resource pack as needed. For full usage, see [this page](./doc/CLI_Manual.md).

## Contribution

We would be grateful if you can contribute to this project. See the [contribution guide](./CONTRIBUTING.md) for more information.

## License

> Copyright 2021 MysticNebula70 & Teahouse Studios
>
> Licensed under the Apache License, Version 2.0 (the "License");
> you may not use this file except in compliance with the License.
> You may obtain a copy of the License at
>
> http://www.apache.org/licenses/LICENSE-2.0
>
> Unless required by applicable law or agreed to in writing, software
> distributed under the License is distributed on an "AS IS" BASIS,
> WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
> See the License for the specific language governing permissions and
> limitations under the License.

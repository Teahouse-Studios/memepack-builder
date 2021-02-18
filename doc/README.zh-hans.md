# memepack-builder

[![Issues](https://img.shields.io/github/issues/Teahouse-Studios/memepack-builder?logo=github&style=flat-square)](https://github.com/Teahouse-Studios/memepack-builder/issues)    [![Pull requests](https://img.shields.io/github/issues-pr/Teahouse-Studios/memepack-builder?logo=github&style=flat-square)](https://github.com/Teahouse-Studios/memepack-builder/pulls)    [![License](https://img.shields.io/static/v1?label=License&message=Apache-2.0&color=db2331&style=flat-square&logo=apache)](http://www.apache.org/licenses/LICENSE-2.0)

一个用于打包适用于Minecraft的梗体中文资源包的工具。

此仓库用于存放PyPI包`memepack-builder`的源代码，不适合直接用于生产环境。请使用`pip install memepack-builder`来安装和管理包。

此包没有其他的依赖项。

此包需要Python 3.9或更高版本才能运行。

## 用法

此包可以被其他Python程序调用，或是直接从命令行运行。

### 作为运行库

此包对外提供四个类：`PlatformChecker`、`ModuleChecker`、`JEPackBuilder`和`BEPackBuilder`。在简单情形（也是大多数情形）下，只需要导入module checker和后两个builder中需要的那个，然后调用`build()`方法。构建的日志以列表形式存放在builder的`build_log`属性内。如果需要字符串形式，请使用`'\n'.join()`。

### 在命令行内

从命令行使用时（`python -m memepack_builder`），程序会提示输入合适的参数，然后按要求自动构建资源包。关于完整用法，请见[此页](./CLI_Manual.zh-hans.md)。

## 贡献

我们欢迎您为此项目作出贡献。请参考此[指导](./CONTRIBUTING.zh-hans.md)以获取详细信息。

## 授权许可

本项目所有源代码以及生成的二进制文件，均以Apache License 2.0协议授权。

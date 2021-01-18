# CLI用法

``` sh
memepack_builder <platform> <type> [-l <language> ...] [-r <resource> ...] [-x <mixed> ...] [-c <collection> ...] [-m <mod> ...] [-f <format>] [-s] [-p] [--hash] [-o <output>]
```

**`platform`**：此资源包适用的平台。应当是`je`或`be`。

**`type`**：资源包类型。在`je`上应当是`normal`、`compat`或`legacy`。`legacy`也指定了`-f 3`。在`be`上应当是`mcpack`或`zip`。

**`-l, --language`**：语言模块。默认是`none`。

**`-r, --resource`**：资源模块。默认是`all`。

**`-x, --mixed`**：混合模块。默认是`none`。

**`-c, --collection`**：集合模块。默认是`none`。

**`-m, --mod`**：（仅`je`）mod语言文件。默认是`none`。

**`-f, --format`**：（仅`je`）资源包的`pack_format`值。默认是`7`。

**`-s, --sfw`**：使用“适用于工作场合”语言文件。是`-l sfw`的快速输入方式。

**`-p, --compatible`**：（仅`be`）使此资源包兼容其他包。

**`--hash`**：在包名中添加散列值。

**`-o, --output`**：此资源包生成位置。默认位置是当前目录下的`builds/`目录。

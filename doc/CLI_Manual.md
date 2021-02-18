# CLI Usage

``` sh
memepack_builder <platform> <type> [-l <language> ...] [-r <resource> ...] [-x <mixed> ...] [-c <collection> ...] [-m <mod> ...] [-f <format>] [-s] [-p] [--hash] [-o <output>]
```

**`platform`** : where the pack is using. should be `je` or `be`.

**`type`** : pack type. For `je` platform, should be `normal`, `compat` or `legacy`. `legacy` implies `-f 3`. For `be` platform, should be `mcpack` or `zip`.

~~**`-l, --language`** : language modules. Default is `none`.~~ This option is deprecated.

**`-r, --resource`** : resource modules. Default is `all`.

~~**`-x, --mixed`** : mixed modules. Default is `none`.~~ This option is deprecated.

**`-c, --collection`** : collection modules. Default is `none`.

**`-m, --mod`** : (`je` only) mod language files. Default is `none`.

**`-f, --format`**: (`je` only) the `pack_format` of the resource pack. The newest and default value is `7`.

**`-s, --sfw`** : use "suitable for work" language module. Shortcut of `-l sfw`.

**`-p, --compatible`** : (`be` only) the pack is compatible with other packs.

**`--hash`** : add a hash to the pack name.

**`-o, --output`** : where the pack will be generated. Default location is `builds/` directory in the current directory.

__all__ = [
    'PACK_LEGACY_FORMAT', 'PACK_CURRENT_FORMAT', 'JEPackBuilder'
]
import json
import os
from zipfile import ZipFile, ZIP_DEFLATED
from memepack_builder._internal.builder import *
from memepack_builder._internal.common import _build_message
from memepack_builder._internal.err_code import *


PACK_LEGACY_FORMAT = 3
PACK_CURRENT_FORMAT = 7


def _get_lang_filename(type: str) -> str:
    return type == 'normal' and 'zh_meme.json' or (
        type == 'compat' and 'zh_cn.json' or 'zh_cn.lang')


class JEPackBuilder(builder):
    def __init__(self, main_res_path: str, module_info: dict, mods_path: str, legacy_mapping_path: str):
        super().__init__(main_res_path, module_info)
        self.__mods_path = mods_path
        self.__legacy_mapping_path = legacy_mapping_path

    @property
    def mods_path(self):
        return self.__mods_path

    @property
    def legacy_mapping_path(self):
        return self.__legacy_mapping_path

    def build(self):
        self.clean_status()
        args = self.build_args
        # args validation
        result = self.__check_args()
        if result['code'] == ERR_OK:
            # process args
            lang_supp, res_supp = self._get_lists()
            # get mods strings
            mod_supp = self.__parse_mods()
            # merge language supplement
            # TODO: split mod strings into namespaces
            main_lang_data = json.load(open(os.path.join(self.main_resource_path,
                                                         "assets/minecraft/lang/zh_meme.json"), 'r', encoding='utf8'))
            main_lang_data = self._merge_language(
                main_lang_data, lang_supp) | self.__get_mod_content(mod_supp)
            # get realms strings
            realms_lang_data = json.load(open(os.path.join(
                self.main_resource_path, "assets/realms/lang/zh_meme.json"), 'r', encoding='utf8'))
            self._file_name = args['hash'] and f"mcwzh-meme.{self._digest[:7]}.zip" or "mcwzh-meme.zip"
            # process mcmeta
            mcmeta = self.__process_meta(args)
            # decide language file name & ext
            lang_file_name = _get_lang_filename(args['type'])
            pack_name = self._create_dir()
            # create pack
            info = f"Building pack {pack_name}"
            self._logger.append(info)
            pack = ZipFile(
                pack_name, 'w', compression=ZIP_DEFLATED, compresslevel=5)
            pack.write(os.path.join(self.main_resource_path,
                                    "pack.png"), arcname="pack.png")
            pack.write(os.path.join(self.main_resource_path,
                                    "LICENSE"), arcname="LICENSE")
            pack.writestr("pack.mcmeta", json.dumps(
                mcmeta, indent=4, ensure_ascii=False))
            # dump lang file into pack
            if args['type'] != 'legacy':
                # normal/compat
                pack.writestr(f"assets/minecraft/lang/{lang_file_name}",
                              json.dumps(main_lang_data, indent=4, ensure_ascii=True, sort_keys=True))
                pack.writestr(f"assets/realms/lang/{lang_file_name}",
                              json.dumps(realms_lang_data, indent=4, ensure_ascii=True, sort_keys=True))
            else:
                # legacy
                main_lang_data |= realms_lang_data
                legacy_content = self.__generate_legacy_content(main_lang_data)
                pack.writestr(
                    f"assets/minecraft/lang/{lang_file_name}", legacy_content)
            # dump resources
            self.__dump_resources(res_supp, pack)
            pack.close()
            self._logger.append(f"Successfully built {pack_name}.")
        else:
            self._raise_error(result)

    def __dump_resources(self, modules: list, pack: ZipFile):
        excluding = ('module_manifest.json', 'add.json', 'remove.json')
        module_path = self.module_info['path']
        for item in modules:
            base_folder = os.path.join(module_path, item)
            for root, _, files in os.walk(base_folder):
                for file in files:
                    if file not in excluding:
                        path = os.path.join(root, file)
                        arcpath = path[path.find(
                            base_folder) + len(base_folder) + 1:]
                        # prevent duplicates
                        if (testpath := arcpath.replace(os.sep, "/")) not in pack.namelist():
                            pack.write(os.path.join(
                                root, file), arcname=arcpath)
                        else:
                            self._raise_warning(_build_message(
                                WARN_DUPLICATED_FILE, f'Duplicated file "{testpath}", skipping.'))

    def __check_args(self):
        args = self.build_args
        # check essential arguments
        for key in ('type', 'modules', 'mod', 'output', 'hash'):
            if key not in args:
                return _build_message(ERR_MISSING_ARGUMENT, f'Missing required argument "{key}".')
        # check "format"
        if 'format' not in args or args['format'] is None:
            # did not specify "format", assume a value
            format = args['type'] == 'legacy' and PACK_LEGACY_FORMAT or PACK_CURRENT_FORMAT
            self._raise_warning(_build_message(
                WARN_IMPLICIT_FORMAT, f'Did not specify "pack_format". Assuming value is "{format}".'))
            args['format'] = format
        else:
            if (args['type'] == 'legacy' and args['format'] > 3) or (args['type'] in ('normal', 'compat') and args['format'] <= 3):
                return _build_message(ERR_MISMATCHED_FORMAT, f'Type "{args["type"]}" does not match pack_format {args["format"]}.')
        return _build_message(ERR_OK, 'Check passed.')

    def __process_meta(self, args: dict) -> dict:
        data = json.load(open(os.path.join(self.main_resource_path,
                                           'pack.mcmeta'), 'r', encoding='utf8'))
        pack_format = args['type'] == 'legacy' and PACK_LEGACY_FORMAT or (
            'format' in args and args['format'] or None)
        data['pack']['pack_format'] = pack_format or data['pack']['pack_format']
        if args['type'] == 'compat':
            data.pop('language')
        return data

    def __parse_mods(self) -> list:
        mods = self.build_args['mod']
        existing_mods = os.listdir(self.mods_path)
        if 'none' in mods:
            return []
        elif 'all' in mods:
            return existing_mods
        else:
            mods_list = []
            for item in mods:
                if item in existing_mods:
                    mods_list.append(item)
                elif (normed_path := os.path.basename(os.path.normpath(item))) in existing_mods:
                    mods_list.append(normed_path)
                else:
                    self._raise_warning(_build_message(
                        WARN_MOD_NOT_FOUND, f'Mod file "{item}" does not exist, skipping.'))
            return mods_list

    def __get_mod_content(self, mod_list: list) -> dict:
        mods = {}
        for file in mod_list:
            if file.endswith(".json"):
                mods |= json.load(
                    open(os.path.join(self.mods_path, file), 'r', encoding='utf8'))
            elif file.endswith(".lang"):
                with open(os.path.join(self.mods_path, file), 'r', encoding='utf8') as f:
                    mods |= (line.strip().split(
                        "=", 1) for line in f if line.strip() != '' and not line.startswith('#'))
            else:
                self._raise_warning(_build_message(
                    WARN_UNKNOWN_MOD_FILE, f'File type "{file[file.rfind(".") + 1:]}" is not supported, skipping.'))
        return mods

    def __generate_legacy_content(self, content: dict) -> str:
        # get mappings list
        mappings = json.load(open(os.path.join(self.legacy_mapping_path,
                                               "all_mappings"), 'r', encoding='utf8'))
        legacy_lang_data = {}
        for item in mappings:
            if (mapping_file := f"{item}.json") not in os.listdir(self.legacy_mapping_path):
                self._raise_warning(_build_message(
                    WARN_MAPPING_NOT_FOUND, f'Missing mapping "{mapping_file}", skipping.'))
            else:
                mapping = json.load(
                    open(os.path.join(self.legacy_mapping_path, mapping_file), 'r', encoding='utf8'))
                for k, v in mapping.items():
                    if v not in content:
                        self._raise_warning(_build_message(
                            WARN_CORRUPTED_MAPPING, f'In file "{mapping_file}": Corrupted key-value pair {{"{k}": "{v}"}}.'))
                    else:
                        legacy_lang_data[k] = content[v]
        return ''.join(f'{k}={v}\n' for k, v in legacy_lang_data.items())

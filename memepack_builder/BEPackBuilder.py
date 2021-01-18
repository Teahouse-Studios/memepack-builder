__all__ = ['BEPackBuilder']

import json
import os
from zipfile import ZipFile, ZIP_DEFLATED
from memepack_builder._internal.builder import *
from memepack_builder._internal.common import _build_message
from memepack_builder._internal.err_code import *


class BEPackBuilder(builder):
    def __init__(self, main_res_path: str, module_info: dict):
        super().__init__(main_res_path, module_info)

    def build(self):
        self.clean_status()
        args = self.build_args
        # args validation
        result = self.__check_args()
        if result['code'] == ERR_OK:
            lang_supp, res_supp = self._get_lists()
            self._file_name = args['hash'] and f"meme-resourcepack.{self._digest[:7]}.{args['type']}" or f"meme-resourcepack.{args['type']}"
            # create pack
            pack_name = self._create_dir()
            info = f"Building pack {pack_name}"
            self._logger.append(info)
            pack = ZipFile(
                pack_name, 'w', compression=ZIP_DEFLATED, compresslevel=5)
            pack.write(os.path.join(self.main_resource_path,
                                    "LICENSE"), arcname="LICENSE")
            pack.write(os.path.join(self.main_resource_path, "pack_icon.png"),
                       arcname="pack_icon.png")
            pack.write(os.path.join(self.main_resource_path, "manifest.json"),
                       arcname="manifest.json")
            self.__dump_language_file(pack, lang_supp)
            pack.write(os.path.join(self.main_resource_path, "textures/map/map_background.png"),
                       arcname="textures/map/map_background.png")
            # dump resources
            item_texture, terrain_texture = self.__dump_resources(
                res_supp, pack)
            if item_texture:
                item_texture_content = self.__merge_json(item_texture, "item")
                pack.writestr("textures/item_texture.json",
                              json.dumps(item_texture_content, indent=4))
            if terrain_texture:
                terrain_texture_content = self.__merge_json(
                    terrain_texture, "terrain")
                pack.writestr("textures/terrain_texture.json",
                              json.dumps(terrain_texture_content, indent=4))
            pack.close()
            self._logger.append(f'Successfully built {pack_name}.')
        else:
            self._raise_error(result)

    def __check_args(self):
        for item in ('type', 'compatible', 'modules', 'output', 'hash'):
            if item not in self.build_args:
                return _build_message(ERR_MISSING_ARGUMENT, f'Missing required argument "{item}".')
        return _build_message(ERR_OK, 'Check passed.')

    def __merge_json(self, modules: list, type: str) -> dict:
        name = type == "item" and "item_texture.json" or "terrain_texture.json"
        result = {'texture_data': {}}
        for item in modules:
            texture_file = os.path.join(
                self.module_info['path'], item, "textures", name)
            content = json.load(open(texture_file, 'r', encoding='utf8'))
            result['texture_data'] |= content['texture_data']
        return result

    def __dump_resources(self, modules: list, pack: ZipFile):
        item_texture = []
        terrain_texture = []
        for item in modules:
            base_folder = os.path.join(self.module_info['path'], item)
            for root, _, files in os.walk(base_folder):
                for file in files:
                    if file != "module_manifest.json":
                        if file == "item_texture.json":
                            item_texture.append(item)
                        elif file == "terrain_texture.json":
                            terrain_texture.append(item)
                        else:
                            path = os.path.join(root, file)
                            arcpath = path[path.find(
                                base_folder) + len(base_folder) + 1:]
                            # prevent duplicates
                            if (testpath := arcpath.replace(os.sep, "/")) not in pack.namelist():
                                pack.write(os.path.join(
                                    root, file), arcname=arcpath)
                            else:
                                self._raise_warning(_build_message(
                                    WARN_DUPLICATED_FILE, f"Duplicated '{testpath}', skipping."))
        return item_texture, terrain_texture

    def __dump_language_file(self, pack: ZipFile, lang_supp: list):
        with open(os.path.join(self.main_resource_path, "texts/zh_ME.lang"), 'r', encoding='utf8') as f:
            lang_data = dict(line[:line.find('#') - 1].strip().split("=", 1)
                             for line in f if line.strip() != '' and not line.startswith('#'))
        lang_data = ''.join(f'{k}={v}\t#\n' for k, v in self._merge_language(
            lang_data, lang_supp).items())
        if self.build_args['compatible']:
            pack.writestr("texts/zh_CN.lang", lang_data)
        else:
            for file in os.listdir(os.path.join(self.main_resource_path, "texts")):
                if os.path.basename(file) != 'zh_ME.lang':
                    pack.write(os.path.join(self.main_resource_path, f"texts/{file}"),
                               arcname=f"texts/{file}")
            pack.writestr("texts/zh_ME.lang", lang_data)
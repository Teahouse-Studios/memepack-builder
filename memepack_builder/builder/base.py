__all__ = [
    'PackBuilder'
]

import json
import os
import re
from hashlib import sha256
from zipfile import ZipFile


class PackBuilder(object):
    '''
    Build packs.
    The builder accepts the building args, then build the packs on demand.
    '''

    def __init__(self, main_res_path: str, module_overview: dict, options: dict):
        self._config = json.load(
            open(os.path.join(os.getcwd(), 'config.json')))
        self.__main_res_path = main_res_path
        self.__module_overview = module_overview
        self.log = []
        self.options = options

    # Deprecated: keeps only as an alias
    @property
    def build_args(self):
        return self.options

    @property
    def main_resource_path(self):
        return self.__main_res_path

    # Deprecated: keeps only as an alias
    @property
    def module_info(self):
        return self.__module_overview

    @property
    def module_overview(self):
        return self.__module_overview

    def _append_log(self, *entry):
        self.log.extend(entry)

    def _build(self, extra_files: list = [], extra_content: dict = {}, excluded_files: list = []):
        excluded_files.extend(
            ('add.json', 'remove.json', 'module_manifest.json'))
        module_path = self.module_overview['modulePath']
        valid_modules = tuple(
            map(lambda item: item['name'], self.module_overview['modules']['resource']))

        name = self.options['output']
        if (self.options['hash']):
            hash = sha256(json.dumps(self.options)).hexdigest()[:7]
            name = re.sub(r'\.(\w+)$', rf'.{hash}.\1', name)
        zip_file = ZipFile(name, compresslevel=5)

        for file in extra_files:
            zip_file.write(f'{self.main_resource_path}/{file}', file)

        for k, v in extra_content.items():
            if v != '':
                zip_file.writestr(k, v)

        for module in self.options['modules']:
            if module not in valid_modules:
                self._append_log(
                    f'Warning: Module "{module}" does not exist, skipping.')
                continue
            for root, _, files in os.walk(os.path.join(module_path, module)):
                for file in files:
                    if file not in excluded_files:
                        path = os.path.join(root, file)
                        dest_path = path.replace(
                            f'{module_path}{os.sep}{module}{os.sep}', '').replace(os.sep, '/')
                        if dest_path not in zip_file.namelist():
                            zip_file.write(path, dest_path)
                        else:
                            self._append_log(
                                f'Warning: Duplicated "{dest_path}", skipping.')

        zip_file.close()

    def _merge_collection_into_resource(self):
        selected_collections = self.options['modules']['collection']
        selected_resource = {*self.options['modules']['resource']}
        collections = self.module_overview['modules']['collection']
        for item in selected_collections:
            target = list(
                filter(lambda value: value['name'] == item, collections))
            if not target:
                self._append_log(
                    f'Warning: Module "{item}" does not exist, skipping.')
                continue
            else:
                selected_resource.update(target[0]['contains'])
        return [*selected_resource]

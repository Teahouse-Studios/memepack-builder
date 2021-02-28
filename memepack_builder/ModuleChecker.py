__all__ = ['ModuleChecker']

import json
import os
from memepack_builder._internal.error_code import *
from memepack_builder._internal.module_classifier import *

MODULE_MANIFEST_FILE = 'module_manifest.json'


class ModuleChecker(object):
    def __init__(self, module_path: str):
        self.__module_path = module_path
        self.__logger = []
        self.clean_status()

    @property
    def check_log(self):
        return self.__logger

    @property
    def module_info(self):
        if not self.__checked:
            self.check_module()
        return self.__module_info

    @property
    def module_path(self):
        return self.__module_path

    @property
    def warning_count(self):
        return self.__warning_count

    @module_path.setter
    def module_path(self, value: str):
        self.__module_path = value

    def clean_status(self):
        self.__checked = False
        self.__module_info = {}
        self.__warning_count = 0
        self.__logger.clear()

    def check_module(self):
        self.clean_status()
        module_info = {
            'path': self.module_path,
            'modules': {
                'resource': [],
                'collection': []
            }
        }
        for module in os.listdir(self.module_path):
            result = self._analyze_module(
                os.path.join(self.module_path, module))
            if result['code'] == WARN_OK:
                module_info['modules'][result['data'].pop(
                    'type')].append(result['data'])
            else:
                entry = f"Warning [{result['code']}]: {result['message']}"
                self.__logger.append(entry)
                self.__warning_count += 1
        self.__module_info = self._flatten_collection(module_info)
        self.__checked = True

    def _analyze_module(self, path: str):
        manifest = os.path.join(path, MODULE_MANIFEST_FILE)
        dir_name = os.path.basename(path)
        if os.path.exists(manifest) and os.path.isfile(manifest):
            data = json.load(open(manifest, 'r', encoding='utf8'))
            for key in ('name', 'type', 'description'):
                if key not in data:
                    return self._result_msg(WARN_BROKEN_MODULE, f'In path "{dir_name}": Incomplete module_manifest.json, missing "{key}" field.')
            if data['type'] in ('resource', 'language', 'mixed'):
                # some compatibility, planned to remove in 0.3.0
                if data['type'] != 'resource':
                    self._raise_warning(
                        WARN_DEPRECATED_MODULE_CONTENT, f'In path "{dir_name}": Module type "{data["type"]}" is deprecated, please use "resource" instead.')
                    data['type'] = 'resource'
                for func, classifier, modified_type in (self._exist_resource_dirs, MODULE_MODIFIED_RESOURCE, 'resource'), (self._exist_language_files, MODULE_MODIFIED_LANGUAGE, 'language'):
                    if func(path):
                        def add_classifier(data, classifier):
                            if 'classifier' not in data:
                                self._raise_warning(
                                    WARN_MISSING_CLASSIFIER, f'In path "{dir_name}": Module modified {modified_type}, but cannot find corresponding classifier.')
                                data['classifier'] = [classifier]
                            elif classifier not in data['classifier']:
                                self._raise_warning(
                                    WARN_MISSING_CLASSIFIER, f'In path "{dir_name}": Module modified {modified_type}, but cannot find corresponding classifier.')
                                data['classifier'].append(classifier)
                        add_classifier(data, classifier)
            elif data['type'] == 'collection':
                if 'contains' not in data:
                    return self._result_msg(WARN_BROKEN_MODULE, f'In path "{dir_name}": Expected a module collection, but "contains" key is missing in module_manifest.json.')
                else:
                    # compatibility start
                    if isinstance(data['contains'], dict):
                        self._raise_warning(
                            WARN_DEPRECATED_MODULE_CONTENT, f'In path "{dir_name}": Deprecated "contains" structure is detected, please update it.')
                        data['contains'] = [i for k in data['contains']
                                            for i in data['contains'][k]]
                    # compatibility end
            else:
                return self._result_msg(WARN_UNKNOWN_MODULE, f'In path "{dir_name}": Unknown module type "{data["type"]}".')
            data['dirname'] = dir_name
            return self._result_msg(WARN_OK, "Analysis successfully finished.", data)
        else:
            return self._result_msg(WARN_BROKEN_MODULE, f'In path "{dir_name}": No module_manifest.json.')

    def _exist_resource_dirs(self, path: str):
        res_dir_names = 'assets', 'credits', 'models', 'textures', 'sounds'
        for dir_name in res_dir_names:
            if os.path.exists(os.path.join(path, dir_name)) and os.path.isdir(os.path.join(path, dir_name)):
                return True
        return False

    def _exist_language_files(self, path: str):
        lang_file_names = 'add.json', 'remove.json'
        for file_name in lang_file_names:
            if os.path.exists(os.path.join(path, file_name)) and os.path.isfile(os.path.join(path, file_name)):
                return True
        return False

    def _result_msg(self, code: int, message: str, data=None):
        result = {'code': code, 'message': message}
        if data:
            result['data'] = data
        return result

    def _raise_warning(self, code: int, message: str):
        self.__logger.append(f'Warning [{code}]: {message}')
        self.__warning_count += 1

    def _flatten_collection(self, module_info: dict):
        resource_list = [i['name'] for i in module_info['modules']['resource']]
        collection_list = [i['name']
                           for i in module_info['modules']['collection']]
        collection_info = module_info['modules']['collection']
        for collection in collection_info:
            flattened_names = {*collection['contains']}
            for name in collection['contains']:
                if name in resource_list:
                    pass
                elif name in collection_list:
                    self._raise_warning(
                        WARN_LOOP_COLLECTION, f'In path "{collection["dirname"]}": Looping collection detected.')
                    if name in flattened_names:
                        flattened_names.remove(name)
                else:
                    self._raise_warning(
                        WARN_UNKNOWN_MODULE, f'In path "{collection["dirname"]}": Collection contains unknown module.')
                    if name in flattened_names:
                        flattened_names.remove(name)
            collection['contains'] = [*flattened_names]
        return module_info

import json
import os

ADD_FILE = 'add.json'
REMOVE_FILE = 'remove.json'
MAPPING_FILE = 'all_mappings'


class LanguageFileGenerator(object):
    def __init__(self, main_language_path) -> None:
        super().__init__()
        self._main = main_language_path
        self._additional_path = []
        self._additional_content = []
        self._prefix = ''
        self._log = []

    @property
    def additional_path(self):
        return self._additional_path

    @additional_path.setter
    def additional_path(self, value: list):
        self._additional_path = value

    @property
    def additional_content(self):
        return self._additional_content

    @additional_content.setter
    def additional_content(self, value: list):
        self._additional_content = value

    @property
    def common_prefix(self):
        return self._prefix

    @common_prefix.setter
    def common_prefix(self, value: str):
        self._prefix = value

    @property
    def log(self):
        return self._log

    def merge_language(self):
        if self._main.endswith('.lang'):
            main_data = self.read_legacy_file()
        else:
            main_data = json.load(open(self._main, 'r', encoding='utf8'))
        for item in self._additional_path:
            add_file = os.path.join(self._prefix, item, ADD_FILE)
            remove_file = os.path.join(self._prefix, item, REMOVE_FILE)
            if os.path.exists(add_file):
                main_data |= json.load(open(add_file, 'r', encoding='utf8'))
            if os.path.exists(remove_file):
                for key in json.load(open(remove_file, 'r', encoding='utf8')):
                    if key in main_data:
                        main_data.pop(key)
                    else:
                        self._log.append(
                            f'Key "{key}" does not exist, skipping.')
        for item in self._additional_content:
            main_data |= item
        return main_data

    def read_legacy_file(self):
        with open(self._main, 'r', encoding='utf8') as f:
            return dict(line[:line.find('#') - 1].strip().split("=", 1)
                        for line in f if line.strip() != '' and not line.startswith('#'))


class LegacyLanguageFileGenerator(LanguageFileGenerator):
    def __init__(self, main_language_path, mapping_path=None) -> None:
        super().__init__(main_language_path)
        self._mapping = mapping_path or ''

    def generate_legacy(self):
        if self._mapping:
            return self._generate_legacy_with_mapping()
        else:
            return self._generate_legacy_without_mapping()

    def _generate_legacy_with_mapping(self):
        # this method is used primarily with je
        mappings = json.load(open(os.path.join(self._mapping,
                                               MAPPING_FILE), 'r', encoding='utf8'))
        legacy_data = {}
        content = self.merge_language()
        for item in mappings:
            if (mapping_file := f"{item}.json") not in os.listdir(self._mapping):
                self._log.append(
                    f'Missing mapping "{mapping_file}", skipping.')
            else:
                mapping = json.load(
                    open(os.path.join(self._mapping, mapping_file), 'r', encoding='utf8'))
                for k, v in mapping.items():
                    if v not in content:
                        self._log.append(
                            f'In file "{mapping_file}": Corrupted key-value pair {{"{k}": "{v}"}}.')
                    else:
                        legacy_data[k] = content[v]
        return ''.join(f'{k}={v}\n' for k, v in legacy_data.items())

    def _generate_legacy_without_mapping(self):
        # this method is used primarily with be
        content = self.merge_language()
        return ''.join(f'{k}={v}\t#\n' for k, v in content.items())

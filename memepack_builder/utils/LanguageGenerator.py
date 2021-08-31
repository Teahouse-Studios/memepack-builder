import json
import os

ADD_FILE = 'add.json'
REMOVE_FILE = 'remove.json'
MAPPING_FILE = 'all_mappings'


def generate_json(file_path: str, with_modules: bool, module_overview, modules: list[str] = None, mod_files: list[str] = None):
    gen = LanguageFileGenerator(file_path, module_overview, modules, mod_files)
    content = gen.generate_json(with_modules)
    return {'content': content, 'log': gen.log}


def generate_java_legacy(file_path: str, with_modules: bool, module_overview, modules: list[str] = None, mod_files: list[str] = None):
    gen = LanguageFileGenerator(file_path, module_overview, modules, mod_files)
    content = gen.generate_java_legacy(with_modules)
    return {'content': content, 'log': gen.log}


def generate_bedrock(file_path: str, with_modules: bool, module_overview, modules: list[str] = None, mod_files: list[str] = None):
    gen = LanguageFileGenerator(file_path, module_overview, modules, mod_files)
    content = gen.generate_bedrock(with_modules)
    return {'content': content, 'log': gen.log}


class LanguageFileGenerator(object):
    def __init__(self, main_language_path: str, module_overview, modules: list[str] = None, mod_files: list[str] = None):
        super().__init__()
        self._main_language_path = os.path.abspath(main_language_path)
        self._module_overview = module_overview
        self._modules = modules or []
        self._mod_files = mod_files or []
        self.log = []

    def _append_log(self, *entry):
        self.log.extend(entry)

    def get_content(self):
        content = {}
        with open(self._main_language_path, 'r', encoding='utf8') as fp:
            if self._main_language_path.endswith('.json'):
                content = json.load(fp)
            elif self._main_language_path.endswith('.lang'):
                content = self.lang_to_json(fp.read())
        return content

    def merge_modules(self, content: dict):
        module_path = self._module_overview['modulePath'] or ''
        for module in self._modules:
            add_file = os.path.join(module_path, module, ADD_FILE)
            if os.path.exists(add_file):
                content |= json.load(open(add_file, 'r', encoding='utf8'))
            remove_file = os.path.join(module_path, module, REMOVE_FILE)
            if os.path.exists(remove_file):
                for key in json.load(open(remove_file, 'r', encoding='utf8')):
                    if key in content:
                        content.pop(key)
                    else:
                        self.log.append(
                            f'Key "{key}" does not exist, skipping.')
        return content

    def merge_mods(self, content: dict):
        for mod in self._mod_files:
            mod_content = {}
            with open(mod, 'r', encoding='utf8') as fp:
                if mod.endswith('json'):
                    mod_content = json.load(fp)
                if mod.endswith('lang'):
                    mod_content = self.lang_to_json(fp.read())
            for k, v in mod_content.items():
                content[k] = v
        return content

    def generate_json(self, with_modules: bool):
        content = self.get_content()
        if with_modules:
            content = self.merge_modules(content)
        return json.dumps(content, ensure_ascii=True, indent=4)

    def generate_java_legacy(self, with_modules: bool):
        content = self.get_content()
        if with_modules:
            content = self.merge_modules(content)
        return self.json_to_lang(content)

    def generate_bedrock(self, with_modules: bool):
        content = self.get_content()
        if with_modules:
            content = self.merge_modules(content)
        return self.json_to_lang(content).replace('\n', '\t#\n')

    def lang_to_json(self, object: str):
        return dict(line[:line.find('#') - 1].strip().split('=', 1)
                    for line in object.splitlines() if line.strip() != '' and not line.startswith('#'))

    def json_to_lang(self, object: dict):
        return ''.join(f'{k}={v}\n' for k, v in object.items())

import json
import os


class ModuleChecker(object):
    def __init__(self, module_path: str):
        self.module_path = os.path.abspath(module_path)
        self.log = []

    # Deprecated: keeps only as an alias
    @property
    def module_info(self):
        return self.validate_modules()

    @property
    def module_overview(self):
        return self.validate_modules()

    def _append_log(self, *entry):
        self.log.extend(entry)

    def validate_modules(self):
        overview = {
            'modulePath': self.module_path,
            'modules': {
                'resource': [],
                'collection': []
            }
        }
        for module in os.listdir(self.module_path):
            manifest = os.path.abspath(os.path.join(
                    self.module_path, module, 'module_manifest.json'))
            data = json.load(open(manifest, 'r', encoding='utf8'))
            overview['modules'][data.pop('type')].append(data)
        return overview

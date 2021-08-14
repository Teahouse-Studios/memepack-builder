from .builder import JavaBuilder, BedrockBuilder
from .module_checker import ModuleChecker


class MemepackBuilder(object):
    def __init__(self, platform: str, resource_path: str, module_path: str, build_options: dict, mod_path: str = None) -> None:
        super().__init__()
        self.log = []
        self.module_checker = ModuleChecker(module_path)
        overview = self.module_checker.validate_modules()
        self.log.extend(self.module_checker.log)
        if platform == 'be':
            self.builder = BedrockBuilder(
                resource_path, overview, build_options)
        elif platform == 'je':
            mod_path = mod_path or ''
            self.builder = JavaBuilder(
                resource_path, overview, mod_path, build_options)
        else:
            raise ValueError() from None

    def build(self):
        self.builder.build()
        self.log.extend(self.builder.log)

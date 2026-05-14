import importlib.util
import inspect
import os
from types import ModuleType
from typing import Iterable


class ModulesLoader:
    @classmethod
    def get_specs_and_modules(cls, directory_path: str) -> Iterable[tuple['ModuleSpec', ModuleType]]:
        for root, dirs, files_names in os.walk(directory_path):
            for file_name in files_names:
                if not file_name.endswith('.py'):
                    continue
                module_name = os.path.basename(file_name)[:-3]
                if module_name.startswith('__'):
                    continue
                file_path = os.path.join(root, file_name)
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                yield spec, module

    @classmethod
    def get_classes_from_module(cls, module: ModuleType) -> Iterable[type]:
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and obj.__module__ == module.__name__:
                yield obj

    @classmethod
    def get_all_classes_from_directory(cls, directory_path: str) -> Iterable[type]:
        for _, module in cls.get_specs_and_modules(directory_path):
            for klass in cls.get_classes_from_module(module):
                yield klass

    @classmethod
    def get_all_classes_and_path_from_directory(cls, directory_path: str) -> Iterable[tuple[type, str]]:
        for _, module in cls.get_specs_and_modules(directory_path):
            for klass in cls.get_classes_from_module(module):
                yield klass, inspect.getfile(module)

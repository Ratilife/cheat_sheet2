import os
from antlr4 import *
from preparation.audit.parser.antlr4.Python3.PythonParserListener import PythonParserListener
from preparation.audit.parser.antlr4.Python3.PythonParser import PythonParser

class ModuleCollector(PythonParserListener):
    def __init__(self, file_path):
        # Эта информация собирается один раз при инициализации.
        self._collecting_info(file_path)

    def _collecting_info(self, file_path):
        """Общая информация о модуле"""
        self._module_info = {
            "file_path": os.path.abspath(file_path),
            "module_name": os.path.basename(file_path),
            "lines_count": 0,
        }
        with open(file_path, 'r', encoding='utf-8') as f:
            self._module_info["lines_count"] = len(f.readlines())

    def get_module_info(self) -> dict:
        return self._module_info
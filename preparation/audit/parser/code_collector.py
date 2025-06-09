import os
from antlr4 import *
from preparation.audit.parser.antlr4.Python3.PythonParserListener import PythonParserListener
from preparation.audit.parser.antlr4.Python3.PythonParser import PythonParser

class CodeCollector(PythonParserListener):
    """
        Универсальный сборщик данных из Python-кода.
        Обходит синтаксическое дерево один раз и собирает всю информацию.
        Предоставляет отдельные методы для получения результатов по каждой задаче.
    """

    pass


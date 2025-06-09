import os
from antlr4 import *
from preparation.audit.parser.antlr4.Python3.PythonParserListener import PythonParserListener
from preparation.audit.parser.antlr4.Python3.PythonParser import PythonParser

class ClassCollector(PythonParserListener):
    def __init__(self):
        # Здесь будет храниться результат по классам и методам
        self._classes_structure = []
        # Хранит данные о классе, внутри которого мы сейчас находимся.
        # Если None, значит мы находимся вне какого-либо класса.
        self._current_class_data = None

    def get_classes(self) -> list:
        """Задача 1: Вернуть только список имен классов и строк их определения."""
        return [
            {"class_name": cls["class_name"], "line_number": cls["line_number"]}
            for cls in self._classes_structure
        ]

    def get_methods_by_class(self) -> list:
        """Задача 2: Вернуть полную структуру: классы с вложенными методами."""
        return self._classes_structure


    def _enterClassdef(self, ctx: PythonParser.Class_defContext):
        """
        Вызывается, когда парсер ВХОДИТ в определение класса ('class ...:').
        Здесь мы "активируем" состояние, показывая, что мы внутри класса.
        """
        # Извлекаем имя класса и номер строки из контекста (ctx)
        class_name = ctx.NAME().getText()
        line_number = ctx.start.line

        # Создаем временный словарь для данных этого класса
        self._current_class_data = {
            "class_name": class_name,
            "line_number": line_number,
            "methods": []
        }

    def _exitClassdef(self, ctx: PythonParser.Class_defContext):
        """
        Вызывается, когда парсер ВЫХОДИТ из блока класса.
        Здесь мы сохраняем накопленную информацию о классе и его методах.
        """
        # Если у нас есть собранные данные о классе, добавляем их в общий результат
        if self._current_class_data:
            self._classes_structure.append(self._current_class_data)

        # "Забываем" о текущем классе, так как мы из него вышли.
        # Это критически важно для правильной работы.
        self._current_class_data = None





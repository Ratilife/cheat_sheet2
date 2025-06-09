import sys
from antlr4 import *
from preparation.audit.parser.antlr4.Python3.PythonLexer import PythonLexer
from preparation.audit.parser.antlr4.Python3.PythonParser import PythonParser

def analyze_python_file(file_path: str) -> dict:
    """
        Главная функция-оркестратор.
        Выполняет полный цикл парсинга файла и возвращает собранные данные.
    """

    print(f"🚀 Анализ файла: {file_path}\n")
    try:
        # 1. Создание потока данных из файла
        input_stream = FileStream(file_path, encoding='utf-8')

        # 2. Создание лексера (разбивает код на токены)
        lexer = PythonLexer(input_stream)

        # 3. Создание потока токенов для парсера
        stream = CommonTokenStream(lexer)

        # 4. Создание парсера (строит синтаксическое дерево)
        parser = PythonParser(stream)

        # 5. Запуск парсинга с корневого правила 'file_input'
        tree = parser.file_input()

        # 6. Создание нашего сборщика данных
        collector = CodeCollector(file_path)

        # 8. Получение результатов из сборщика с помощью специальных методов
        results = {
            "module_info": collector.get_module_info(),
            "classes_list": collector.get_classes(),
            "full_structure": collector.get_methods_by_class()
        }
        return results


    except FileNotFoundError:
        print(f"Ошибка: Файл не найден по пути {file_path}")
        return {}
    except Exception as e:
        print(f"Произошла ошибка при анализе файла: {e}")
        return {}

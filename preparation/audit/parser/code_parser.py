import sys
from antlr4 import *
from preparation.audit.parser.antlr4.Python3.PythonLexer import PythonLexer
from preparation.audit.parser.antlr4.Python3.PythonParser import PythonParser
from preparation.audit.parser.code_collector import CodeCollector

def start_code_parser(target_file):
    analysis_results = analyze_python_file(target_file)

    if analysis_results:
        print_results(analysis_results)


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

def print_results(results: dict):
    """Функция для красивого вывода результатов в консоль."""
    if not results:
        return

    full_structure = results["full_structure"]
    if not full_structure:
        print("  Классы не найдены.")
    else:
        for cls in full_structure:
            print(f"\n  ▶️ Класс: '{cls['class_name']}' (строка: {cls['line_number']})")
            if not cls['methods']:
                print("    - Методы не найдены.")
            else:
                for method in cls['methods']:
                    print(f"    - Метод: '{method['method_name']}' (строка: {method['line_number']})")
                    print(f"      - Возвращаемый тип: {method['return_type']}")
    print("-" * 40)
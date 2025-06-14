"""
    Модуль md_file_parser.py

    Предназначен для парсинга Markdown-файлов и извлечения их структуры.
    Основные возможности:
        1. Чтение содержимого Markdown-файлов
        2. Формирование структуры документа
        3. Обработка ошибок чтения файлов
"""
import os

class MarkdownListener:
    """
        Класс для обработки и анализа Markdown-файлов.

        Содержит методы для:
        - чтения файлов
        - извлечения структуры
        - обработки ошибок
    """
    def __init__(self):
        """
            Инициализация объекта MarkdownListener.
            Создает пустой список для хранения структуры документа.
        """
        self.structure = [] # Список для хранения структуры документа

    def get_structure(self):
        """
            Возвращает текущую структуру документа.
            Возвращает:
            list: Список элементов структуры документа
        """
        return self.structure

    def parse_markdown_file(self, file_path):
        """
                Основной метод для парсинга Markdown-файла.

                Параметры:
                    file_path (str): Путь к Markdown-файлу

                Возвращает:
                    dict: Словарь с двумя ключами:
                        - 'structure': список элементов структуры
                        - 'root_name': имя файла без расширения

                Обрабатывает возможные ошибки чтения файла.
        """
        try:
            # Чтение содержимого файла с указанием кодировки UTF-8
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Получение имени файла без расширения
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            # Формирование структуры документа
            self.structure = [{
                'name': file_name,       # Имя документа
                'type': 'markdown',      # Тип документа
                'content': content       # Содержимое файла
            }]
            # Возвращаем структуру и имя корневого элемента
            return {
                'structure': self.structure,
                'root_name': file_name
            }
        except Exception as e:
            # Обработка ошибок при чтении файла
            print(f"Error parsing markdown file: {str(e)}")
            # Возвращаем пустую структуру в случае ошибки
            return {
                'structure': [],
                'root_name': "Error"
            }


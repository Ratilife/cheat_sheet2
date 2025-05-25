from PySide6.QtCore import Signal, QObject
from typing import Optional, Tuple
import logging
import os


class DeleteManager(QObject):
    """Универсальный менеджер для удаления элементов дерева.

    Отвечает за:
    - Удаление элементов разных типов (файлы, папки, шаблоны)
    - Централизованную обработку ошибок
    - Уведомление о результатах операций
    """

    # Сигнал завершения операции удаления:
    # bool - статус операции (True/False)
    # str - сообщение для пользователя
    removal_complete = Signal(bool, str)

    def __init__(self, tree_model, parser):
        """Инициализация менеджера удаления.

        Args:
            tree_model (STFileTreeModel): Модель данных дерева файлов
            parser (STFileParserWrapper): Парсер для работы с ST-файлами
        """
        super().__init__()  # Инициализация QObject
        self.tree_model = tree_model  # Модель дерева для операций с элементами
        self.parser = parser  # Парсер для работы с содержимым ST-файлов
        self.logger = logging.getLogger(self.__class__.__name__)  # Логгер для записи событий

    def execute_removal(self, index, delete_from_disk: bool = False) -> Tuple[bool, str]:
        """Основной метод для выполнения операции удаления.

        Args:
            index (QModelIndex): Индекс элемента в модели дерева
            delete_from_disk (bool): Флаг удаления файла с диска

        Returns:
            Tuple[bool, str]: Кортеж (статус операции, сообщение)

        Логика работы:
        1. Проверка валидности индекса
        2. Определение типа элемента
        3. Выбор стратегии удаления
        4. Обработка и логирование ошибок
        5. Отправка сигнала о результате
        """
        if not index.isValid():  # Проверка валидности индекса
            return False, "Неверный индекс элемента"

        item = index.internalPointer()  # Получаем объект элемента
        item_type = item.item_data[1]  # Тип элемента (второй элемент в item_data)

        try:
            if item_type in ['template', 'folder']:  # Для элементов ST-файлов
                success = self._remove_st_item(item.item_data)
                msg = (f"{item_type} успешно удален" if success
                       else f"Ошибка удаления {item_type}")
            else:  # Для обычных файлов и markdown
                success = self.tree_model.remove_item(index, delete_from_disk)
                msg = self._get_file_removal_msg(item.item_data[2], delete_from_disk, success)

            self.removal_complete.emit(success, msg)  # Отправка сигнала
            return success, msg

        except Exception as e:  # Обработка непредвиденных ошибок
            error_msg = f"Ошибка удаления: {str(e)}"
            self.logger.error(error_msg)  # Запись в лог
            self.removal_complete.emit(False, error_msg)  # Сигнал об ошибке
            return False, error_msg


    def _remove_st_item(self, item_data) -> bool:
        """Приватный метод для удаления элементов ST-файлов.

        Args:
            item_data (list): Данные элемента [name, type, path, ...]

        Returns:
            bool: Статус операции

        Примечания:
        - Для шаблонов вызывает parser.remove_template()
        - Для папок вызывает parser.remove_folder()
        - Все ошибки логируются и пробрасываются выше
        """
        try:
            if item_data[1] == 'template':  # Обработка шаблонов
                self.parser.remove_template(
                    item_data[2],  # Путь к файлу
                    item_data[0]  # Имя шаблона
                )
            elif item_data[1] == 'folder':  # Обработка папок
                self.parser.remove_folder(
                    item_data[2],  # Путь к файлу
                    item_data[0]  # Имя папки
                )
            return True  # Успешное завершение
        except Exception as e:
            self.logger.error(f"Ошибка удаления ST элемента: {e}")
            return False  # Ошибка операции

    def _get_file_removal_msg(self, path: str, from_disk: bool, success: bool) -> str:
        """Формирует пользовательское сообщение об удалении файла.

        Args:
            path (str): Полный путь к файлу
            from_disk (bool): Флаг удаления с диска
            success (bool): Статус операции

        Returns:
            str: Готовое сообщение для пользователя

        Примеры:
        - "Файл example.st удален полностью"
        - "Файл example.md удален из дерева"
        - "Не удалось удалить файл: example.txt"
        """
        action = "удален полностью" if from_disk else "удален из дерева"
        if not success:
            return f"Не удалось удалить файл: {os.path.basename(path)}"
        return f"Файл {os.path.basename(path)} {action}"
"""
 PySide6.QtCore.Signal - механизм сигналов Qt для реализации событийной модели
 PySide6.QtCore.QObject - базовый класс для всех объектов Qt, обеспечивает:
   - работу с сигналами/слотами
   - управление памятью (родитель-потомок)
   - интеграцию с event-loop

 typing.Optional - указание что значение может быть None или указанного типа
 typing.Tuple - аннотация для кортежей с указанием типов элементов

 logging - стандартная библиотека для логирования:
   - запись сообщений разного уровня (DEBUG, INFO, WARNING, ERROR)
   - настройка обработчиков вывода (консоль, файлы и др.)

 os - работа с операционной системой:
   - манипуляции с путями (os.path)
   - работа с файловой системой
   - доступ к переменным окружения
"""

from PySide6.QtCore import (Signal, QObject, QModelIndex)
from typing import Tuple, Optional
import logging
import os
import  json


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

    #TODO - разобраться
    def execute_removal(self, index, delete_from_disk=False) -> Tuple[bool, str]:
        """Унифицированный метод удаления с улучшенной обработкой типов."""
        if not index.isValid():
            return False, "Неверный индекс элемента"

        item = index.internalPointer()
        item_type = item.item_data[1]
        item_path = item.item_data[2] if len(item.item_data) > 2 else None

        try:
            # Удаление с диска для поддерживаемых типов
            if delete_from_disk and item_type in ['file', 'markdown'] and item_path:
                try:
                    os.remove(item_path)
                except OSError as e:
                    return False, f"Ошибка удаления файла: {e.strerror}"

            # Выбор стратегии удаления
            if item_type in ['template', 'folder']:
                success = self._remove_st_item(item.item_data)
            else:
                success = self.tree_model.removeRow(index.row(), index.parent())

            #TODO - тут ошибка

            # Унифицированное формирование сообщения
            msg = self._generate_removal_message(item_type, item_path, success, delete_from_disk)
            self.removal_complete.emit(success, msg)
            return success, msg

        except Exception as e:
            error_msg = f"Системная ошибка: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.removal_complete.emit(False, error_msg)
            return False, error_msg

    def _generate_removal_message(self, item_type: str, item_path: Optional[str], success: bool,
                                  delete_from_disk: bool) -> str:
        """Формирует сообщение о результате удаления.

        Args:
            item_type: Тип элемента ('file', 'markdown', 'template', 'folder')
            item_path: Путь к файлу (если есть)
            success: Статус операции
            delete_from_disk: Флаг удаления с диска

        Returns:
            Строка с сообщением для пользователя
        """
        if not success:
            return f"Не удалось удалить {item_type}"

        item_name = os.path.basename(item_path) if item_path else item_type

        if item_type in ['file', 'markdown']:
            action = "удален полностью" if delete_from_disk else "удален из дерева"
            return f"Файл {item_name} {action}"
        elif item_type == 'template':
            return f"Шаблон '{item_name}' успешно удален"
        elif item_type == 'folder':
            return f"Папка '{item_name}' успешно удалена"
        else:
            return f"Элемент '{item_name}' успешно удален"


    #TODO - устарел нужно будет удалить
    def execute_removal_old(self, index, delete_from_disk: bool = False) -> Tuple[bool, str]:
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

    #TODO - метод _get_file_removal_msg связан с методом execute_removal_old
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


    def remove_file(self, file_path):
        """Удаляет файл из дерева и из сохраненных данных"""
        # Находим индекс файла
        for i in range(len(self.tree_model.root_item.child_items)):
            item = self.tree_model.root_item.child_items[i]
            if item.item_data[2] == file_path:
                index = self.tree_model.index(i, 0, QModelIndex())
                self.tree_model.removeRow(i, QModelIndex())
                break

        # Удаляем из сохраненных данных
        self._remove_file_from_json(file_path)
        return True, f"Файл {os.path.basename(file_path)} удален"

    def _remove_file_from_json(self, file_path):
        """Удаляет файл из сохраненного списка"""
        save_path = os.path.join(os.path.dirname(__file__), "saved_files.json")
        if not os.path.exists(save_path):
            return

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                files = json.load(f)

            files = [f for f in files if f["path"] != file_path]

            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(files, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при удалении файла из сохраненных: {e}")
            return False, f"Ошибка при удалении файла из сохраненных: {e}"
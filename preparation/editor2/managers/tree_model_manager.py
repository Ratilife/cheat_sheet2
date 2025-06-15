import os
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import (QMenu, QMessageBox, QFileDialog, QInputDialog)
from PySide6.QtGui import QAction

from preparation.editor2.managers import file_manager
from preparation.editor2.models.st_file_tree_model import STFileTreeModel
from preparation.editor2.parsers.st_file_parser import STFileParserWrapper
from preparation.editor2.parsers.md_file_parser import MarkdownListener
from preparation.editor2.utils.delete_manager import DeleteManager
from preparation.editor2.managers.file_manager import FileManager

class TreeModelManager:
    """
    Фасад для работы с моделью дерева файлов. Инкапсулирует:
    - Добавление/удаление элементов
    - Парсинг файлов
    - Взаимодействие с DeleteManager
    """

    def __init__(self):
        self.tree_model = STFileTreeModel()
        self.st_parser = STFileParserWrapper()
        self.md_parser = MarkdownListener()
        self.delete_manager = DeleteManager(self.tree_model, self.st_parser)

        # Добавляем FileManager
        self.file_manager = FileManager()
        self.file_manager.tree_model = self.tree_model  # Передаем модель в FileManager


    # --- Методы для работы с данными ---
    def add_file(self, file_path: str) -> bool:
        """
        Добавляет файл в модель. Автоматически определяет тип (.st или .md).
        Возвращает True при успехе.
        """

        try:
            if file_path.endswith('.st'):
                result = self.st_parser.parse_st_file(file_path)
                self.tree_model.add_file(file_path)
            elif file_path.endswith('.md'):
                result = self.md_parser.parse_markdown_file(file_path)
                self.tree_model.add_markdown_file(file_path)
            return True
        except Exception as e:
            print(f"Ошибка добавления файла {file_path}: {str(e)}")
            return False

    def remove_item(self, index: QModelIndex, delete_from_disk: bool = False) -> tuple[bool, str]:
        """
        Удаляет элемент через DeleteManager.
        Возвращает (success, message).
        """
        return self.delete_manager.execute_removal(index, delete_from_disk)

    # --- Методы для доступа к данным ---
    def get_item_type(self, index: QModelIndex) -> str:
        """Возвращает тип элемента ('file', 'folder', 'markdown', etc.)."""
        if not index.isValid():
            return ""
        return self.tree_model.get_item_type(index)

    def get_item_path(self, index: QModelIndex) -> str | None:
        """Возвращает путь к файлу (для 'file' и 'markdown'), иначе None."""
        if self.get_item_type(index) not in ('file', 'markdown'):
            return None
        return self.tree_model.get_item_path(index)

    def get_item_level(self, index: QModelIndex) -> int:
        """Возвращает уровень вложенности элемента (0 для корня)."""
        return self.tree_model.get_item_level(index)

    def set_tree_model(self, model):
        """Установка модели для дерева"""
        self.tree_view.setModel(model)
        # Раскрываем все узлы дерева
        self.tree_view.expandAll()

    def remove_file(self, file_path):
        """Удаляет файл из дерева и из сохраненных данных"""
        # Находим индекс файла
        for i in range(len(self.tree_model.root_item.child_items)):
            item = self.tree_model.root_item.child_items[i]
            if item.item_data[2] == file_path:
                index = self.tree_model.index(i, 0, QModelIndex())
                self.tree_model.remove_item(index, False)  # Удаляем только из дерева
                break

        # Удаляем из сохраненных данных
        self._remove_file_from_json(file_path)

        # Если удаляемый файл был текущим, очищаем просмотр
        if self.current_file == file_path:
            self.markdown_viewer.set_content("")
            self.current_file = None

    def load_st_md_files(self):
        files = self.file_manager.load_st_md_files()
        for file in files:
            print(f"Загрузка файла: {file}")  # Логирование
            if file.endswith('.st'):
                self.tree_model.add_file(file)
            elif file.endswith('.md'):
                self.tree_model.add_markdown_file(file)
        self.file_manager.save_files_to_json()
        # Принудительное обновление вида

    def _show_tree_context_menu(self, pos):
        """Показывает контекстное меню для дерева файлов
            Args:
            pos: QPoint - позиция курсора мыши при вызове контекстного меню
        """
        # Получаем индекс элемента дерева по позиции клика
        index = self.tree_view.indexAt(pos)
        # Если индекс невалидный (клик мимо элементов), выходим из метода
        if not index.isValid():
            return

        # Получаем объект элемента дерева по индексу
        item = index.internalPointer()

        # Создаем объект контекстного меню
        menu = QMenu(self)

        # Определяем тип элемента
        item_type = item.item_data[1]

        if item_type in ['file', 'markdown']:
            # Для файлов создаем подменю с вариантами удаления
            delete_menu = menu.addMenu("Удалить")

            # Вариант 1: Удалить только из дерева
            delete_from_tree = delete_menu.addAction("Удалить из дерева")
            delete_from_tree.triggered.connect(
                lambda: self.delete_manager.execute_removal(index, False)  # delete_from_disk=False
            )

            # Вариант 2: Удалить полностью (с диска)
            delete_completely = delete_menu.addAction("Удалить полностью")
            delete_completely.triggered.connect(
                lambda: self.delete_manager.execute_removal(index, True)  # delete_from_disk=True
            )
        else:
            # Для других элементов (папки, шаблоны) простое удаление
            delete_action = menu.addAction("Удалить")
            delete_action.triggered.connect(
                lambda: self.delete_manager.execute_removal(index, False)
                # Для не-файлов delete_from_disk не применяется
            )

            # Проверяем тип элемента (не является ли он файлом)
        if item.item_data[1] != "file":
            # Действие для удаления файла
            remove_action = QAction("Удалить из списка", self)
            # Подключаем обработчик удаления файла
            remove_action.triggered.connect(
                lambda: self.remove_file(item.item_data[2]))
            # Добавляем действие в меню
            menu.addAction(remove_action)
        # Если элемент является папкой
        elif item.item_data[1] == "folder":
            # Действия для папок
            expand_action = QAction("Развернуть", self)
            # Подключаем обработчик разворачивания текущей папки
            expand_action.triggered.connect(lambda: self.tree_view.expand(index))
            # Добавляем действие в меню
            menu.addAction(expand_action)

            # Создаем действие "Свернуть"
            collapse_action = QAction("Свернуть", self)
            # Подключаем обработчик сворачивания текущей папки
            collapse_action.triggered.connect(lambda: self.tree_view.collapse(index))
            # Добавляем действие в меню
            menu.addAction(collapse_action)

            # Добавляем разделитель в меню
            menu.addSeparator()

            # Создаем действие "Развернуть все вложенные"
            expand_all_action = QAction("Развернуть все вложенные", self)
            # Подключаем обработчик рекурсивного разворачивания
            expand_all_action.triggered.connect(lambda: self._expand_recursive(index))
            # Добавляем действие в меню
            menu.addAction(expand_all_action)

            # Создаем действие "Свернуть все вложенные"
            collapse_all_action = QAction("Свернуть все вложенные", self)
            # Подключаем обработчик рекурсивного сворачивания
            collapse_all_action.triggered.connect(lambda: self._collapse_recursive(index))
            # Добавляем действие в меню
            menu.addAction(collapse_all_action)
        # Отображаем контекстное меню в позиции курсора
        menu.exec(self.tree_view.viewport().mapToGlobal(pos))

    def _new_st_file(self):
        """
        Создание нового ST файла.
        Открывает диалог сохранения файла и инициализирует базовую структуру.
            Основное назначение:
                1. Создание нового файла с расширением .st
                2. Инициализация базовой структуры файла
                3. Обновление состояния приложения после создания
         """

        path, _ = QFileDialog.getSaveFileName(
            self, "Создать ST файл", "", "ST Files (*.st)")
        # Открытие диалогового окна сохранения файла:
        # - Заголовок: "Создать ST файл"
        # - Начальная директория не указана (пустая строка)
        # - Фильтр файлов: только .st расширение
        # Возвращает путь к файлу и выбранный фильтр (который игнорируется)

        if path:
            # Проверка, что пользователь не отменил диалог (путь не пустой)
            # Добавляем расширение, если его нет
            if not path.endswith('.st'):
                path += '.st'
            # Гарантируем, что файл будет иметь правильное расширение
            # Добавляем .st, если его нет в конце пути
            try:
                # Создаем файл с корректной структурой
                with open(path, 'w', encoding='utf-8') as f:
                    # Открытие файла для записи в кодировке UTF-8
                    # Контекстный менеджер гарантирует закрытие файла

                    # Базовая структура нового ST файла
                    file_name = os.path.basename(path).replace('.st', '')
                    # Получаем имя файла без расширения:
                    # 1. os.path.basename() извлекает имя файла из пути
                    # 2. replace() удаляет .st, если есть
                    content = f"""{{1, {{"{file_name}", 1, 0, "", ""}}, []}}"""
                    # Формирование начальной структуры ST файла:
                    # - Корневой элемент с типом 1 (папка)
                    # - Имя папки совпадает с именем файла
                    # - Пустой список дочерних элементов
                    f.write(content)
                    # Запись сформированной структуры в файл

                # Обновляем текущий файл
                self.current_file_path = path
                # Сохраняем путь к новому файлу в атрибуте класса
                self._load_file_content(path)  # Загружаем содержимое файла
                # Вызов метода для загрузки содержимого только что созданного файла
                # в соответствующий редактор
                # Отправляем сигнал о создании файла
                self.file_created.emit(path)  # ?
                # Генерация сигнала с путем к созданному файлу
                # (подключенные слоты могут обновить дерево файлов и т.д.)

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать файл: {str(e)}")

    def _new_md_file(self):
        """
        Создание нового MD файла.
        Открывает диалог сохранения файла и инициализирует базовую структуру.
        """
        # Основное назначение:
        # 1. Создание нового Markdown-файла (.md)
        # 2. Инициализация файла с базовым заголовком
        # 3. Интеграция нового файла в систему

        # Открываем диалоговое окно сохранения файла
        path, _ = QFileDialog.getSaveFileName(
            self,                               # Родительское окно
            "Создать MD файл",           # Заголовок диалога
            "",                             # Начальная директория (пустая - текущая)
            "Markdown Files (*.md)")       # Фильтр по расширению

        if path:                                # Если пользователь не отменил диалог
            # Добавляем расширение, если его нет
            if not path.endswith('.md'):
                path += '.md'                   # Гарантируем наличие правильного расширения

            try:
                # Создаем файл с заголовком, соответствующим имени файла
                with open(path, 'w', encoding='utf-8') as f:        # Открытие для записи в UTF-8
                    # Запись заголовка первого уровня с именем файла
                    f.write(f"# {os.path.basename(path).replace('.md', '')}\n\n")
                    # Формат: # ИмяФайла + два перевода строки

                # Обновляем текущий файл и загружаем его содержимое
                self.current_file_path = path # Сохранение пути текущего файла
                self._load_file_content(path) # Загрузка содержимого в редактор
                # Отправляем сигнал о создании файла
                self.file_created.emit(path)  # Уведомление подписчиков о событии

                # Добавляем файл в дерево, если есть родительская панель
                if self.parent_panel:    # Проверка наличия родительской панели
                    # Добавление файла в модель дерева
                    self.parent_panel.tree_model.add_markdown_file(path)
                    # Сохранение состояния в JSON
                    self.parent_panel._save_files_to_json()

            except Exception as e:
                QMessageBox.critical(self,                                      # Родительское окно
                                     "Ошибка",                             # Заголовок
                                     f"Не удалось создать файл: {str(e)}") # Текст с описанием ошибки

    def _create_folder(self):
        """
        Создание новой папки в текущем ST файле.
        Запрашивает имя папки через диалоговое окно.
        """
        # Основное назначение:
        # 1. Добавление новой папки в структуру текущего ST-файла
        # 2. Взаимодействие с пользователем через диалоговое окно
        # 3. Сохранение изменений и обновление интерфейса

        # Проверка условий для создания папки
        if not self.current_file_path or not self.current_file_path.endswith('.st'):
            return
            # Выход если:
            # - нет текущего файла (current_file_path is None)
            # - текущий файл НЕ является ST-файлом (не оканчивается на .st)

        # Запрашиваем имя папки у пользователя
        name, ok = QInputDialog.getText(
            self,                       # Родительское окно
            "Создать папку",       # Заголовок диалога
            "Введите имя папки:") # Текст подсказки
        # Возвращает кортеж:
        # - name: введенное пользователем имя
        # - ok: True если нажата OK, False если Cancel

        # Проверка что пользователь ввел имя и подтвердил
        if ok and name:
            # Создаем структуру новой папки
            new_folder = {
                'type': 'folder',           # Тип элемента
                'name': name,               # Имя из диалога
                'children': []              # Пустой список для вложенных элементов
            }
            # Формат соответствует общей структуре ST-файла

            # Добавляем папку в корень (можно доработать для вложенных папок)
            self.current_structure['content']['children'].append(new_folder)
            # Добавляет новую папку в:
            # current_structure → content → children (список дочерних элементов)
            self._save_st_file()  # Сохраняем изменения
            # Вызов метода для сохранения обновленной структуры в файл
            self._update_tree_view()  # Обновляем отображение дерева
            # Перерисовка дерева для отображения новой папки

    def _create_template(self):
        """
        Создание нового шаблона в текущем ST файле.
        Запрашивает имя шаблона, использует текущий текст из редактора как содержимое.
        """
        # Основное назначение:
        # 1. Создание нового шаблона внутри открытого ST-файла
        # 2. Использование текущего содержимого редактора как тела шаблона
        # 3. Сохранение изменений в файловой системе и обновление интерфейса

        # Проверка условий для создания шаблона
        if not self.current_file_path or not self.current_file_path.endswith('.st'):
            return
            # Выход если:
            # - нет текущего открытого файла
            # - файл не является ST-файлом (расширение не .st)

        # Запрашиваем имя шаблона у пользователя
        name, ok = QInputDialog.getText(
            self,                               # Родительское окно
            "Создать шаблон",              # Заголовок диалога
            "Введите имя шаблона:")       # Текст подсказки
        # Возвращает:
        # - name: введенное пользователем имя шаблона
        # - ok: True если нажато OK, False если Cancel

        # Проверка что пользователь ввел имя и подтвердил
        if ok and name:
            # Создаем структуру нового шаблона
            new_template = {
                'type': 'template',                        # Тип элемента
                'name': name,                              # Введенное имя
                'content': self.text_editor.toPlainText()  # Текст из редактора
            }
            # Структура соответствует формату ST-файла:
            # - type: тип элемента (template)
            # - name: имя шаблона
            # - content: содержимое (текст из QTextEdit)

            # Добавляем шаблон в корень (можно доработать для вложенных папок)
            self.current_structure['content']['children'].append(new_template)
            # Добавление в:
            # current_structure → content → children (список дочерних элементов)
            self._save_st_file()  # Сохраняем изменения
            # Вызов метода для физического сохранения изменений на диск
            self._update_tree_view()  # Обновляем отображение дерева
            # Перерисовка дерева для отображения нового шаблона

    def _update_tree_view(self):
        """
        Обновление отображения дерева файлов.
        В текущей реализации не завершено - нужно подключить модель дерева.
        """
        if not self.current_structure:
            return

        # TODO: Реализовать через QStandardItemModel
        pass

    def _generate_st_content(self, structure):
        """
        Генерация содержимого ST файла согласно грамматике STFile.g4.
        """

        def build_folder(folder):
            children = []
            for child in folder.get('children', []):
                if child['type'] == 'folder':
                    children.append(
                        f'{{1, {{"{child["name"]}", 1, 0, "", ""}}, [\n'
                        f'{build_folder(child)}\n'
                        ']}'
                    )
                elif child['type'] == 'template':
                    children.append(
                        f'{{0, {{"{child["name"]}", 0, 1, "", "{child["content"]}"}}}}'
                    )
            return ',\n'.join(children)

        root_folder = structure['content']
        return (
            f'{{1, {{"{root_folder["name"]}", 1, 0, "", ""}}, [\n'
            f'{build_folder(root_folder)}\n'
            ']}'
        )
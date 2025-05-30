import json
from PySide6.QtWidgets import QFileIconProvider
from PySide6.QtCore import QAbstractItemModel, Qt, QModelIndex, QSize
from PySide6.QtGui import QIcon, QFont
from st_file_parser import STFileParserWrapper

from PySide6.QtGui import QColor
from md_file_parser import MarkdownListener
# ===================================================================
# КЛАССЫ ДЛЯ РАБОТЫ С ДАННЫМИ
# ===================================================================


# Элемент дерева (как ветка)
class STFileTreeItem:
    def __init__(self, data, parent=None):
        self.item_data = data  # [Имя, Тип, Контент]
        self.parent_item = parent  # Родительская ветка
        self.child_items = []  # Дочерние элементы
        # Cвойство для доступа к типу
        self.type = data[1] if len(data) > 1 else ""


# Модель данных для дерева

class STFileTreeModel(QAbstractItemModel):
    """Модель данных для отображения структуры ST-файлов в дереве"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = STFileTreeItem(["Root", "root", ""])  # Корневой элемент
        self.parser = STFileParserWrapper()  # Обертка для парсера
        self.md_parser = MarkdownListener()  # Добавляем парсер для MD
        self.icon_provider = QFileIconProvider()  # Провайдер иконок

    # Основные методы модели
    def index(self, row, column, parent=QModelIndex()):
        """Создает индекс для элемента"""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        child_item = parent_item.child_items[row]
        return self.createIndex(row, column, child_item)

    def parent(self, index):
        """Возвращает родителя элемента"""
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_item = child_item.parent_item

        if parent_item == self.root_item:
            return QModelIndex()

        return self.createIndex(parent_item.child_items.index(child_item), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        """Количество строк (дочерних элементов)"""
        parent_item = parent.internalPointer() if parent.isValid() else self.root_item
        return len(parent_item.child_items)

    def columnCount(self, parent=QModelIndex()):
        """Количество колонок (фиксировано: Имя и Тип)"""
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Возвращает данные для отображения"""
        if not index.isValid():
            return None

        item = index.internalPointer()
        column = index.column()

        if role == Qt.DisplayRole:
            return item.item_data[column]

        elif role == Qt.DecorationRole and column == 0:
            # Возвращаем иконки для разных типов элементов
            if item.item_data[1] == "file":
                return QIcon.fromTheme("text-x-generic")
            elif item.item_data[1] == "folder":
                return QIcon.fromTheme("folder")
            elif item.item_data[1] == "template":
                return QIcon.fromTheme("text-x-script")
            elif item.item_data[1] == "markdown":
                return QIcon.fromTheme("text-markdown")

        elif role == Qt.FontRole:
            # Жирный шрифт для файлов
            font = QFont()
            if item.item_data[1] in ["file", "markdown"]:
                font.setBold(False)
            elif item.item_data[1] == "folder":
                font.setBold(True)
            return font

        elif role == Qt.ForegroundRole:
            # Разные цвета для разных типов элементов
            if item.item_data[1] == "file":
                return QColor("#2a82da")
            elif item.item_data[1] == "folder":
                return QColor("#006400")  # Темно-зеленый для папок
            elif item.item_data[1] == "template":
                return QColor("#00008B")  # Темно-синий для шаблонов
            elif item.item_data[1] == "markdown":
                return QColor("#8B008B")  # Темно-пурпурный для markdown

        elif role == Qt.SizeHintRole:
            return QSize(0, 24)  # Фиксированная высота строк

        # Добавляем пользовательскую роль для определения уровня вложенности
        elif role == Qt.UserRole + 1:
            level = 0
            parent = item.parent_item
            while parent and parent != self.root_item:
                level += 1
                parent = parent.parent_item
            return level
        # Добавляем роль для установки типа элемента (для CSS селекторов)
        elif role == Qt.UserRole + 2:
            return item.item_data[1]  # Возвращаем тип элемента

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Заголовки колонок"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Имя"][section]
        return None

    def add_file(self, file_path):
        """Добавляет новый ST-файл в модель"""
        if any(item.item_data[2] == file_path for item in self.root_item.child_items):
            print(f"File {file_path} already exists in tree!")
            return

        # Получаем результат парсинга, который теперь содержит и структуру, и имя корневой папки
        result = self.parser.parse_st_file(file_path)

        print("Parsed structure:")
        print(json.dumps(result['structure'], indent=2, ensure_ascii=False))
        print(f"Root name: {result['root_name']}")  # Отладочный вывод

        # Извлекаем имя корневой папки (например, "Новый1")
        root_name = result['root_name']

        # Извлекаем структуру файла для построения дерева
        structure = result['structure']

        # Начинаем вставку данных в модель
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

        # Создаем элемент для корневой папки с именем из файла
        file_item = STFileTreeItem([root_name, "file", file_path], self.root_item)


        # Строим поддерево на основе структуры файла
        self._build_tree(structure, file_item)

        # Добавляем элемент в корневую папку модели
        self.root_item.child_items.append(file_item)

        # Завершаем вставку
        self.endInsertRows()
        # self.print_tree()
        print(f"Структура из парсера: {json.dumps(structure, indent=2)}")

    def _build_tree(self, nodes, parent):
        """Рекурсивно строит дерево из данных"""
        for node in nodes:
            item = STFileTreeItem([node['name'], node['type'], node.get('content', '')], parent)
            parent.child_items.append(item)
            if 'children' in node:
                self._build_tree(node['children'], item)

    def is_folder(self, index):
        """Проверяет, является ли элемент папкой"""
        if not index.isValid():
            return False
        item = index.internalPointer()
        return item.type == "folder"

    def add_markdown_file(self, file_path):
        """Добавляет Markdown файл в модель"""
        result = self.md_parser.parse_markdown_file(file_path)

        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

        # Создаем элемент для файла
        file_item = STFileTreeItem([result['root_name'], "markdown", file_path], self.root_item)

        # Строим структуру (для MD будет только один корневой элемент)
        #self._build_tree(result['structure'], file_item)

        self.root_item.child_items.append(file_item)
        self.endInsertRows()

    def has_children(self, parent=QModelIndex()):
        if not parent.isValid():
            return len(self.root_item.child_items) > 0
        item = parent.internalPointer()
        return len(item.child_items) > 0

    def canFetchMore(self, parent):
        """Проверяет, можно ли загрузить дочерние элементы"""
        if not parent.isValid():
            return False
        item = parent.internalPointer()
        return bool(item.child_items)

    # необезательный метод создан для проверки данных
    def print_tree(self, item=None, level=0):
        """Рекурсивная печать структуры дерева для отладки
        Args:
            item: STFileTreeItem - текущий элемент для печати (по умолчанию корневой)
            level: int - уровень вложенности (для отступов)
        """
        item = item or self.root_item
        print("  " * level + f"- {item.item_data[0]} ({item.type})")
        for child in item.child_items:
            self.print_tree(child, level + 1)

    def flags(self, index):
        """Возвращает флаги для элементов"""
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

        item = index.internalPointer()
        if item and item.type == "folder" and len(item.child_items) > 0:
            flags |= Qt.ItemIsAutoTristate | Qt.ItemIsUserCheckable

        return flags


    def removeRow(self, row, parent=QModelIndex()):
        """Удаляет строку из модели (стандартный метод QAbstractItemModel)

        Args:
            row: int - номер строки для удаления
            parent: QModelIndex - родительский индекс

        Returns:
            bool: True если удаление прошло успешно
        """
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        if row < 0 or row >= len(parent_item.child_items):
            return False

        self.beginRemoveRows(parent, row, row)
        parent_item.child_items.pop(row)
        self.endRemoveRows()
        return True

    def get_item_path(self, index):
        """Возвращает путь к файлу для элемента

        Args:
            index: QModelIndex - индекс элемента

        Returns:
            str: путь к файлу или None если элемент не файл
        """
        if not index.isValid():
            return None

        item = index.internalPointer()
        if item.item_data[1] in ['file', 'markdown']:
            return item.item_data[2]
        return None
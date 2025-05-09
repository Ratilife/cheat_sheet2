# -*- coding: utf-8 -*-
"""
Главный модуль приложения для работы с ST-файлами
"""

# Импорт необходимых модулей
import sys
import os
from PySide6.QtWidgets import (
    QSplitter, QTreeView, QTextEdit, QWidget, QVBoxLayout, 
    QApplication, QMenu, QHBoxLayout, QPushButton, 
    QSpacerItem, QSizePolicy, QFileDialog, QAbstractItemModel
)
from PySide6.QtCore import Qt, QFileSystemWatcher, Signal, QObject, QDir, QRect, QModelIndex
from PySide6.QtGui import QAction, QScreen

# Импорт компонентов ANTLR
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from ANTLR4.STFileLexer import STFileLexer
from ANTLR4.STFileParser import STFileParser, STFileListener

# ===================================================================
# КЛАССЫ ДЛЯ РАБОТЫ С ДАННЫМИ
# ===================================================================

class STFileTreeItem:
    """Элемент дерева для хранения данных ST-файла"""
    def __init__(self, data, parent=None):
        self.parent_item = parent  # Родительский элемент
        self.item_data = data      # Данные: [Имя, Тип, Контент]
        self.child_items = []      # Список дочерних элементов

class STFileTreeModel(QAbstractItemModel):
    """Модель данных для отображения структуры ST-файлов в дереве"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = STFileTreeItem(["Root", "root", ""])  # Корневой элемент
        self.parser = STFileParserWrapper()  # Обертка для парсера

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
        return 2

    def data(self, index, role=Qt.DisplayRole):
        """Возвращает данные для отображения"""
        if not index.isValid() or role != Qt.DisplayRole:
            return None
            
        item = index.internalPointer()
        return item.item_data[index.column()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Заголовки колонок"""
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return ["Имя", "Тип"][section]
        return None

    def add_file(self, file_path):
        """Добавляет новый ST-файл в модель"""
        structure = self.parser.parse_st_file(file_path)  # Парсим файл
        file_name = os.path.basename(file_path)
        
        # Начинаем вставку данных
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        file_item = STFileTreeItem([file_name, "file", file_path], self.root_item)
        self._build_tree(structure, file_item)  # Строим поддерево
        self.root_item.child_items.append(file_item)
        self.endInsertRows()

    def _build_tree(self, nodes, parent):
        """Рекурсивно строит дерево из данных"""
        for node in nodes:
            item = STFileTreeItem([node['name'], node['type'], node.get('content','')], parent)
            parent.child_items.append(item)
            if 'children' in node:
                self._build_tree(node['children'], item)

# ===================================================================
# КЛАССЫ ДЛЯ ПАРСИНГА ST-ФАЙЛОВ
# ===================================================================

class STFileParserWrapper:
    """Обертка для парсера ANTLR"""
    def parse_st_file(self, file_path):
        """Основной метод парсинга файла"""
        input_stream = FileStream(file_path, encoding="utf-8")
        lexer = STFileLexer(input_stream)        # Лексер
        token_stream = CommonTokenStream(lexer)  # Поток токенов
        parser = STFileParser(token_stream)      # Парсер
        tree = parser.fileStructure()            # Дерево разбора
        
        # Собираем структуру данных
        listener = StructureListener()
        ParseTreeWalker().walk(listener, tree)
        return listener.get_structure()

class StructureListener(STFileListener):
    """Слушатель для построения структуры данных из дерева разбора"""
    def __init__(self):
        self.stack = [{'children': []}]  # Стек для отслеживания вложенности
        self.result = self.stack[0]      # Корневой элемент

    def get_structure(self):
        """Возвращает собранную структуру"""
        return self.result['children']

    def enterEntry(self, ctx):
        """Обработка входа в элемент (папку)"""
        if ctx.getChildCount() > 3:  # Проверяем, что это папка
            name = ctx.STRING(0).getText()[1:-1]  # Извлекаем имя
            new_item = {
                'name': name,
                'type': 'folder',
                'children': []
            }
            self.stack[-1]['children'].append(new_item)
            self.stack.append(new_item)  # Переходим на уровень вложенности

    def exitEntry(self, ctx):
        """Выход из элемента (папки)"""
        if ctx.getChildCount() > 3:
            self.stack.pop()  # Возвращаемся на предыдущий уровень

    def enterTemplateHeader(self, ctx):
        """Обработка шаблона"""
        name = ctx.STRING(0).getText()[1:-1]  # Имя шаблона
        # Содержимое из 5-го параметра (индекс 4)
        content = ctx.STRING(4).getText()[1:-1] if len(ctx.STRING) > 4 else ""
        self.stack[-1]['children'].append({
            'name': name,
            'type': 'template',
            'content': content
        })

# ===================================================================
# ГРАФИЧЕСКИЙ ИНТЕРФЕЙС
# ===================================================================

class SidePanelSignals(QObject):
    """Сигналы панели (оставлены для совместимости)"""
    file_selected = Signal(str)
    file_changed = Signal(str)

class SidePanel(QWidget):
    """Главное окно приложения"""
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.signals = SidePanelSignals()
        self.file_watcher = QFileSystemWatcher()
        self.current_file = None
        self._init_ui()
        self._init_position_menu()
        self._setup_screen_edge_docking()

    def _init_ui(self):
        """Инициализация интерфейса"""
        self.setMinimumWidth(300)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Панель заголовка
        self.title_bar = QWidget()
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(5, 2, 5, 2)

        # Кнопки управления
        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setFixedSize(20, 20)
        self.minimize_btn.clicked.connect(self.showMinimized)

        # Кнопка загрузки файлов
        self.load_btn = QPushButton("📂")
        self.load_btn.setFixedSize(20, 20)
        self.load_btn.clicked.connect(self._load_st_files)

        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.close)

        title_layout.addWidget(self.minimize_btn)
        title_layout.addWidget(self.load_btn)  # Добавлена кнопка загрузки
        title_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        title_layout.addWidget(self.close_btn)

        main_layout.addWidget(self.title_bar)

        # Основная область
        self.splitter = QSplitter(Qt.Vertical)
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(False)  # Показываем заголовки
        self.tree_view.clicked.connect(self._on_tree_item_clicked)

        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)

        # Инициализация модели данных
        self.tree_model = STFileTreeModel()
        self.tree_view.setModel(self.tree_model)

        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.content_view)
        main_layout.addWidget(self.splitter)

    def _load_st_files(self):
        """Загрузка ST-файлов через диалог"""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Открыть ST-файлы", 
            "", 
            "ST Files (*.st)"
        )
        for file in files:
            self.tree_model.add_file(file)  # Добавляем файлы в модель

    def _on_tree_item_clicked(self, index):
        """Обработка клика по элементу дерева"""
        item = index.internalPointer()
        if item.item_data[1] == 'template':
            self.content_view.setPlainText(item.item_data[2])  # Показываем контент

    # Остальные методы остаются без изменений
    def mousePressEvent(self, event): ...
    def mouseMoveEvent(self, event): ...
    def mouseReleaseEvent(self, event): ...
    def _init_position_menu(self): ...
    def _setup_screen_edge_docking(self): ...
    def update_dock_position(self): ...
    def contextMenuEvent(self, event): ...

# ===================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ===================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    panel = SidePanel()
    panel.setWindowTitle("ST File Viewer")
    panel.show()
    sys.exit(app.exec())
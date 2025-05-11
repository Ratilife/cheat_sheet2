import sys
import os
import json
from PySide6.QtWidgets import (QSplitter, QTreeView, QTextEdit, QWidget,
                               QVBoxLayout, QApplication, QMenu,
                               QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QFileDialog,
                               QFileIconProvider, QStyledItemDelegate, QStyleOptionButton, QStyle)
from PySide6.QtCore import (Qt, QFileSystemWatcher, Signal, QObject, QRect, QSize,
                            QAbstractItemModel, QModelIndex, QEvent)
from PySide6.QtGui import QAction, QIcon, QFont, QColor, QCursor, QPen, QPainter

# Импорт компонентов ANTLR
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr4.error.ErrorListener import ErrorListener
from ANTLR4.st_Files.STFileLexer import STFileLexer
from ANTLR4.st_Files.STFileParser import STFileParser
from ANTLR4.st_Files.STFileListener import STFileListener


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

        elif role == Qt.FontRole:
            # Жирный шрифт для файлов
            font = QFont()
            if item.item_data[1] == "file":
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

    '''def has_children(self, index):
        """Проверяет, есть ли у элемента дети"""
        if not index.isValid():
            return False
        item = index.internalPointer()
        return bool(item.child_items)'''

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


# ===================================================================
# КЛАССЫ ДЛЯ ПАРСИНГА ST-ФАЙЛОВ
# ===================================================================

class STFileParserWrapper:
    def parse_st_file(self, file_path):
        input_stream = FileStream(file_path, encoding="utf-8")
        lexer = STFileLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = STFileParser(tokens)

        # Устанавливаем обработчик ошибок
        parser.removeErrorListeners()
        parser.addErrorListener(ExceptionErrorListener())

        tree = parser.fileStructure()
        listener = StructureListener()
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        listener.root_name = file_name  # ИЗМЕНЕНИЕ: Имя файла в listener
        ParseTreeWalker().walk(listener, tree)

        return {
            'structure': listener.get_structure(),
            'root_name': listener.root_name
        }


class ExceptionErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Exception(f"Ошибка парсинга в строке {line}:{column} - {msg}")

class StructureListener(STFileListener):
    def __init__(self):
        self.stack = [{'children': []}]
        self.current_parent = self.stack[0]
        self.root_name = "Unnamed"
        self.found_root = False


    def get_structure(self):
        return self.stack[0]['children']

    '''def enterFileStructure(self, ctx):
        """
        Обрабатывает вход в корневую структуру ST-файла.

        Этот метод вызывается при входе в корневой элемент файла. Он ищет первый
        элемент folderHeader, чтобы определить имя корневой папки.

        Args:
            ctx: Контекст парсера для корневой структуры файла
        """
        # Обработка корневого уровня файла
        if not self.found_root:
            # Ищем первый folderHeader для определения имени корня
            # ИЗМЕНЕНИЕ: Более надежная проверка структуры контекста
            if hasattr(ctx, 'children') and ctx.children:
                for child in ctx.children:
                    # ИЗМЕНЕНИЕ: Добавлена проверка на наличие entry
                    if hasattr(child, 'entry') and child.entry():
                        entry = child.entry()
                        # ИЗМЕНЕНИЕ: Проверяем folderHeader через entry
                        if hasattr(entry, 'folderHeader') and entry.folderHeader():
                            folder_ctx = entry.folderHeader()
                            if folder_ctx and folder_ctx.STRING():
                                self.root_name = folder_ctx.STRING(0).getText()[1:-1]
                                self.found_root = True
                                break'''



    def enterEntry(self, ctx):
        if ctx.folderHeader():
            # Обработка папки
            header = ctx.folderHeader()
            name = header.STRING(0).getText()[1:-1]

            new_item = {
                'name': name,
                'type': 'folder',
                'children': []
            }
            self.current_parent['children'].append(new_item)
            self.stack.append(new_item)
            self.current_parent = new_item



        elif ctx.templateHeader():
            # Обработка шаблона
            header = ctx.templateHeader()
            name = header.STRING(0).getText()[1:-1]
            content = header.STRING(2).getText()[1:-1] if len(header.STRING()) > 1 else ""
            self.current_parent['children'].append({
                'name': name,
                'type': 'template',
                'content': content
            })

    def exitEntry(self, ctx):
        if ctx.folderHeader() and len(self.stack) > 1:
            self.stack.pop()
            self.current_parent = self.stack[-1]

# ===================================================================
# ГРАФИЧЕСКИЙ ИНТЕРФЕЙС
# ===================================================================

# Добавляем после создания tree_view, но до установки модели
class TreeItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_view = parent  # Сохраняем ссылку на tree_view
        # Добавляем иконки для кнопок
        self.expand_icon = QIcon.fromTheme("list-add")
        self.collapse_icon = QIcon.fromTheme("list-remove")
        self.button_size = 15
        self.fixed_indent = 20  # <-- Добавляем фиксированный отступ для кнопки


    def editorEvent(self, event, model, option, index):
        item = index.internalPointer()
        if not item or item.type != "folder" or not item.child_items:
            return super().editorEvent(event, model, option, index)

        # Получаем уровень вложенности
        level = index.data(Qt.UserRole + 1) or 0
        if level == 0:  # Пропускаем корневой элемент
            return super().editorEvent(event, model, option, index)

        # Рассчитываем позицию кнопки с учетом уровня вложенности
        #indent = (level - 1) * self.tree_view.indentation()
        button_rect = QRect(
            option.rect.left() + self.fixed_indent,  # <-- Используем фиксированный отступ,
            option.rect.top() ,
            self.button_size,
            option.rect.height()
        )

        # Обрабатываем клик
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if button_rect.contains(event.position().toPoint()):
                if self.tree_view.isExpanded(index):
                    self.tree_view.collapse(index)
                else:
                    self.tree_view.expand(index)
                return True

        return super().editorEvent(event, model, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        item = index.internalPointer()
        if item and item.type == "folder" and (index.data(Qt.UserRole + 1) or 0) > 0:
            size.setWidth(size.width() + 22)  # Добавляем место для кнопки
        return size

    # неактуально. Возможно вдальнейшем удаление. Неспользуется

    def paint(self, painter, option, index):
        item = index.internalPointer()
        if not item:
            return super().paint(painter, option, index)

        original_rect = option.rect
        level = index.data(Qt.UserRole + 1) or 0
        base_indent = (level - 1) * self.tree_view.indentation() if level > 0 else 0 # ?

        # Сдвигаем все элементы согласно уровню
        option.rect = original_rect.adjusted(base_indent, 0, 0, 0)

        # Рисуем кнопку только для папок (кроме корневого уровня)
        if item.type == "folder" and item.child_items and level > 0:
            button_rect = QRect(
                original_rect.left() + self.fixed_indent,
                original_rect.top()+ (original_rect.height() - self.button_size) // 2,  # Центрируем по вертикали
                self.button_size,
                original_rect.height()
            )

            button_option = QStyleOptionButton()
            button_option.rect = button_rect
            button_option.state = QStyle.State_Enabled
            button_option.icon = self.collapse_icon if self.tree_view.isExpanded(index) else self.expand_icon
            button_option.iconSize = QSize(10, 10)

            QApplication.style().drawControl(QStyle.CE_PushButton, button_option, painter)
            option.rect.adjust(self.fixed_indent + self.button_size + 4, 0, 0, 0)  # Сдвигаем текст после кнопки

        # Дополнительный отступ для шаблонов
        if item.type == "template":
            option.rect.adjust(15, 0, 0, 0)

        super().paint(painter, option, index)
        option.rect = original_rect


# Класс для обработки сигналов панели
class SidePanelSignals(QObject):
    # Сигнал при выборе файла (передает путь к файлу)
    file_selected = Signal(str)
    # Сигнал при изминении файла(передает путь к измененному файлу)
    file_changed = Signal(str)


# Основной класс боковой панели
class SidePanel(QWidget):
    def __init__(self, parent=None):

        # Инициализация QWidget с параметрами:
        # - Без рамки (FramelessWindowHint)
        # - Всегда поверх других окон (WindowStaysOnTopHint)
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Создаем экземпляр класса для сигналов
        self.signals = SidePanelSignals()
        self.file_watcher = QFileSystemWatcher()  # Инициализация наблюдателя
        self.file_watcher.fileChanged.connect(self._on_file_changed)  # Подключение сигнала
        # Инициализация пользовательского интерфейса
        self._init_ui()
        # Инициализация контекстного меню для управления позицией
        self._init_position_menu()
        # Настройка прикрепления к краям экрана
        self._setup_screen_edge_docking()
        # Текущий выбранный файл (хранит путь)
        self.current_file = None  # Инициализация переменной

        self._update_menu_checks()

        # Загружаем сохраненные файлы при старте
        self._load_saved_files()

        # Для изменения размеров
        self.resize_area = 5  # Ширина области захвата для изменения размеров
        self.resize_direction = None
        self.drag_start_position = None
        self.drag_window_position = None
        self.drag_window_size = None

        # Гарантируем, что окно будет видимым
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.show()

    # Метод инициализации пользовательского интерфейса
    def _init_ui(self):
        # Устанавливаем минимальную ширину панели
        self.setMinimumWidth(300)

        # Создаем основной вертикальный layout
        main_layout = QVBoxLayout(self)
        # Убираем отступы у layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Панель заголовка
        self.title_bar = QWidget()
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(5, 2, 5, 2)

        # Создаем панель заголовка с кнопками управления
        self.title_bar = QWidget()
        # Горизонтальный layout для панели заголовка
        title_layout = QHBoxLayout(self.title_bar)
        # Устанавливаем небольшие отступы для панели заголовка
        title_layout.setContentsMargins(5, 2, 5, 2)

        # Кнопка сворачивания
        self.minimize_btn = QPushButton("—")
        # Фиксированный размер кнопки
        self.minimize_btn.setFixedSize(20, 20)
        # Подключаем действие сворачивания окна
        self.minimize_btn.clicked.connect(self.showMinimized)

        # Кнопка закрытия
        self.close_btn = QPushButton("×")
        # Фиксированный размер кнопки
        self.close_btn.setFixedSize(20, 20)
        # Подключаем действие закрытия окна
        self.close_btn.clicked.connect(self.close)

        # Кнопка загрузки файлов
        self.load_btn = QPushButton("📂")
        self.load_btn.setFixedSize(20, 20)
        self.load_btn.clicked.connect(self._load_st_files)

        # Добавляем кнопки сворачивания/разворачивания
        self.collapse_btn = QPushButton("−")
        self.collapse_btn.setFixedSize(20, 20)
        self.collapse_btn.setToolTip("Свернуть все")
        self.collapse_btn.clicked.connect(self.collapse_all)

        self.expand_btn = QPushButton("+")
        self.expand_btn.setFixedSize(20, 20)
        self.expand_btn.setToolTip("Развернуть все")
        self.expand_btn.clicked.connect(self.expand_all)

        # Растягивающийся элемент между кнопками и заголовком
        # Добавляем кнопки в layout заголовка:
        # 1. Кнопка сворачивания
        title_layout.addWidget(self.minimize_btn)
        # 2 Добавлена кнопка загрузки
        title_layout.addWidget(self.load_btn)
        # 3 Добавляем кнопку сворачивания
        title_layout.addWidget(self.collapse_btn)
        # 4 Добавляем кнопку разворачивания
        title_layout.addWidget(self.expand_btn)
        # 5. Растягивающийся элемент (пустое пространство)
        title_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # 6. Кнопка закрытия
        title_layout.addWidget(self.close_btn)

        # Добавляем панель заголовка в основной layout
        main_layout.addWidget(self.title_bar)

        # Создаем разделитель с вертикальной ориентацией
        self.splitter = QSplitter(Qt.Vertical)

        self.splitter.setSizes([300, 100])  # 300px для дерева, 100px для текста
        self.splitter.setHandleWidth(5)  # Ширина разделителя
        self.splitter.setStyleSheet("QSplitter::handle { background: #ccc; }")

        # Создаем дерево для отображения файловой системы
        self.tree_view = QTreeView()
        # Показываем заголовки у дерева
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setIndentation(10)  # Увеличьте это значение
        self.tree_view.setAnimated(True)  # Анимация раскрытия
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setRootIsDecorated(True)  # Показываем декор для корневых элементов
        self.tree_view.setExpandsOnDoubleClick(True)  # Включаем разворачивание по двойному клику
        self.tree_view.setSortingEnabled(False)

        # Устанавливаем делегат с правильной ссылкой на tree_view
        self.delegate = TreeItemDelegate(self.tree_view)
        self.tree_view.setItemDelegate(self.delegate)

        # Подключаем обработчик двойного клика
        self.tree_view.doubleClicked.connect(self._on_tree_item_double_clicked)

        # Устанавливаем делегат
        # self.tree_view.setItemDelegate(TreeItemDelegate(self.tree_view))
        # Настройка стиля дерева
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: white;
                border: 1px solid #ddd;
            }
            QTreeView::item {
                padding: 2px;
                margin: 0px;
                height: 20px;
            }
            /* Убираем стандартные треугольники */
            QTreeView::branch {
                background: transparent;
                border: 0px;
            }
            QTreeView::branch:has-siblings:!adjoins-item {
                border-image: none;
                image: none;
            }
            QTreeView::branch:has-siblings:adjoins-item {
                border-image: none;
                image: none;
            }
            QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                border-image: none;
                image: none;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: none;
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                border-image: none;
                image: none;
            }
        """)

        # Подключаем обработчик клика по элементам дерева
        self.tree_view.clicked.connect(self._on_tree_item_clicked)

        # Создаем текстовое поле для отображения содержимого файлов
        self.content_view = QTextEdit()
        # Делаем текстовое поле только для чтения
        self.content_view.setReadOnly(True)

        # Инициализация модели данных
        self.tree_model = STFileTreeModel()
        self.tree_view.setModel(self.tree_model)
        # Добавляем виджеты в разделитель:
        # 1. Дерево файлов (верхняя часть)
        self.splitter.addWidget(self.tree_view)
        # 2. Текстовое поле (нижняя часть)
        self.splitter.addWidget(self.content_view)
        # 3. Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)

        # Настраиваем контекстное меню для дерева
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self._show_tree_context_menu)

    # Обработка сохраненя и загрузки файлов st
    def _get_save_path(self):
        """Возвращает путь к файлу сохранения"""
        return os.path.join(os.path.dirname(__file__), "saved_files.json")

    def _save_files_to_json(self):
        """Сохраняет список загруженных файлов в JSON"""
        save_path = self._get_save_path()
        files = []

        # Собираем пути всех загруженных файлов
        for i in range(len(self.tree_model.root_item.child_items)):
            item = self.tree_model.root_item.child_items[i]
            if item.item_data[1] == "file":
                files.append(item.item_data[2])  # Путь к файлу

        # Сохраняем в JSON
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=4)

    def _load_saved_files(self):
        """Загружает сохраненные файлы из JSON"""
        save_path = self._get_save_path()
        if not os.path.exists(save_path):
            return

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                files = json.load(f)
                for file_path in files:
                    if os.path.exists(file_path):
                        self.tree_model.add_file(file_path)
            # Раскрываем все узлы после загрузки
            self.tree_view.expandAll()
        except Exception as e:
            print(f"Ошибка при загрузке сохраненных файлов: {e}")

    def _remove_file_from_json(self, file_path):
        """Удаляет файл из сохраненного списка"""
        save_path = self._get_save_path()
        if not os.path.exists(save_path):
            return

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                files = json.load(f)

            # Удаляем файл из списка
            if file_path in files:
                files.remove(file_path)

                # Сохраняем обновленный список
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(files, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при удалении файла из сохраненных: {e}")

    def _load_st_files(self):
        """Загрузка ST-файлов через диалог"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Открыть ST-файлы", "", "ST Files (*.st)"
        )
        for file in files:
            print(f"Загрузка файла: {file}")  # Логирование
            self.tree_model.add_file(file)
            self.tree_model.print_tree()  # Вывод структуры в консоль
            self._save_files_to_json()

        # Принудительное обновление вида
        self.tree_view.expandAll()
        self.tree_view.update()

    def _on_tree_item_clicked(self, index):
        """Обработка клика по элементу дерева"""
        item = index.internalPointer()
        if not item:
            return

        # Тест
        if item.item_data[1] == 'template' or item.item_data[1] == 'folder':
            parent = item.parent_item
            if parent:
                print(
                    f"Элемент: {item.item_data[0]}, тип: {item.item_data[1]}, Родитель: {parent.item_data[0]}, тип: {parent.item_data[1]}")
            else:
                print(f"Элемент: {item.item_data[0]}, Родитель: None")

        # Для шаблонов показываем контент
        if item.item_data[1] == 'template':
            self.content_view.setPlainText(item.item_data[2])

        # Для файлов добавляем в наблюдатель
        if item.item_data[1] == 'file':
            file_path = item.item_data[2]
            self.current_file = file_path
            self.signals.file_selected.emit(file_path)

            # Обновляем наблюдатель файлов
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())
            self.file_watcher.addPath(file_path)

    # Обработчик нажатия кнопки мыши (для перемещения окна)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.dock_position == "float":
                # Проверяем, находится ли курсор в области изменения размеров
                rect = self.rect()
                self.resize_direction = self._get_resize_direction(event.position().toPoint(), rect)

                if self.resize_direction:
                    # Начинаем изменение размера
                    self.drag_start_position = event.globalPosition().toPoint()
                    self.drag_window_position = self.pos()
                    self.drag_window_size = self.size()
                    event.accept()
                    return

            # Обычное перемещение окна
            if event.position().y() < 30:  # Только в заголовке
                self.drag_start_position = event.globalPosition().toPoint()
                self.drag_window_position = self.pos()
                event.accept()

    # Обработчик перемещения мыши (для перемещения окна)
    def mouseMoveEvent(self, event):
        if self.dock_position == "float" and hasattr(self, 'drag_start_position'):
            if self.resize_direction:
                # Изменение размера окна
                delta = event.globalPosition().toPoint() - self.drag_start_position
                new_rect = QRect(self.drag_window_position, self.drag_window_size)

                if "left" in self.resize_direction:
                    new_rect.setLeft(new_rect.left() + delta.x())
                if "right" in self.resize_direction:
                    new_rect.setRight(new_rect.right() + delta.x())
                if "top" in self.resize_direction:
                    new_rect.setTop(new_rect.top() + delta.y())
                if "bottom" in self.resize_direction:
                    new_rect.setBottom(new_rect.bottom() + delta.y())

                # Применяем новые размеры и позицию
                if new_rect.width() > self.minimumWidth() and new_rect.height() > self.minimumHeight():
                    self.setGeometry(new_rect)
                event.accept()
            # Если начата операция перетаскивания
            elif hasattr(self, 'drag_start_position'):
                # Вычисляем смещение курсора
                delta = event.globalPosition().toPoint() - self.drag_start_position
                # Перемещаем окно на вычисленное смещение
                self.move(self.drag_window_position + delta)
                # Принимаем событие
                event.accept()

    # Обработчик отпускания кнопки мыши (завершение перемещения)
    def mouseReleaseEvent(self, event):
        # Если была операция перетаскивания
        if hasattr(self, 'drag_start_position'):
            # Удаляем временные данные
            del self.drag_start_position
            self.resize_direction = None
            # Принимаем событие
            event.accept()

    # Обработчик клика по элементу дерева
    '''def _on_tree_item_clicked(self, index):
        """Обработка клика по элементу дерева"""
        # Получаем модель данных
        model = index.model()
        # Проверяем, есть ли у модели метод filePath
        if hasattr(model, 'filePath'):
            # Получаем путь к выбранному файлу
            file_path = model.filePath(index)
            # Сохраняем текущий файл
            self.current_file = file_path
            # Отправляем сигнал о выборе файла
            self.signals.file_selected.emit(file_path)

            # Добавляем файл в наблюдатель
            # Если есть наблюдаемые файлы, очищаем список
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())
            # Добавляем новый файл в наблюдатель
            self.file_watcher.addPath(file_path)'''

    def _get_resize_direction(self, pos, rect):
        """Определяет направление изменения размера"""
        directions = []
        if pos.x() <= self.resize_area:
            directions.append("left")
        elif pos.x() >= rect.width() - self.resize_area:
            directions.append("right")
        if pos.y() <= self.resize_area:
            directions.append("top")
        elif pos.y() >= rect.height() - self.resize_area:
            directions.append("bottom")

        return "_".join(directions) if directions else None

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.dock_position == "float":
            # Подсветка границ для визуального обозначения области изменения размеров
            painter = QPainter(self)
            painter.setPen(QPen(QColor(100, 100, 100, 100), self.resize_area))
            painter.drawRect(self.rect())

    # Обработчик изменения файла
    def _on_file_changed(self, path):
        """Обработка изменения файла"""
        # Если измененный файл - текущий выбранный файл
        if path == self.current_file:
            # Отправляем сигнал об изменении файла
            self.signals.file_changed.emit(path)

    # Метод для установки модели данных в дерево
    def set_tree_model(self, model):
        """Установка модели для дерева"""
        self.tree_view.setModel(model)
        # Раскрываем все узлы дерева
        self.tree_view.expandAll()

    # Метод для установки текстового содержимого
    def set_content(self, text):
        """Установка текстового содержимого"""
        self.content_view.setPlainText(text)

    # Метод для установки Markdown содержимого
    def set_markdown_content(self, markdown_text):
        """Установка Markdown содержимого"""
        self.content_view.setMarkdown(markdown_text)

    # Метод для очистки панели
    def clear(self):
        """Очистка панели"""
        # Очищаем модель дерева
        self.tree_view.setModel(None)
        # Очищаем текстовое поле
        self.content_view.clear()
        # Если есть наблюдаемые файлы, очищаем список
        if self.file_watcher.files():
            self.file_watcher.removePaths(self.file_watcher.files())
        # Сбрасываем текущий файл
        self.current_file = None

    # Метод удаления файла
    def remove_file(self, file_path):
        """Удаляет файл из дерева и из сохраненных данных"""
        # Находим и удаляем файл из модели
        for i in range(len(self.tree_model.root_item.child_items)):
            item = self.tree_model.root_item.child_items[i]
            if item.item_data[2] == file_path:
                self.tree_model.beginRemoveRows(QModelIndex(), i, i)
                self.tree_model.root_item.child_items.pop(i)
                self.tree_model.endRemoveRows()
                break
        # Удаляем из сохраненных данных
        self._remove_file_from_json(file_path)

        # Если удаляемый файл был текущим, очищаем просмотр
        if self.current_file == file_path:
            self.content_view.clear()
            self.current_file = None

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
        # Проверяем тип элемента (не является ли он файлом)
        if item.item_data[1] != "file":
            # Действие для удаления файла
            remove_action = QAction("Удалить из списка", self)
            # Подключаем обработчик удаления файла
            remove_action.triggered.connect(lambda: self.remove_file(item.item_data[2]))
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

    # Метод настройки прикрепления к краям экрана
    def _setup_screen_edge_docking(self):
        """Настройка прикрепления к краям экрана"""
        # Позиция по умолчанию - справа
        self.dock_position = "right"  # left/right/float
        # Отступ от края экрана
        self.dock_margin = 5
        # Обновляем позицию
        self.update_dock_position()
        # Устанавливаем прозрачность окна
        self.setWindowOpacity(0.9)

    # Метод обновления позиции панели
    def update_dock_position(self):
        """Обновление позиции относительно края экрана"""
        # Получаем геометрию экрана
        screen = QApplication.primaryScreen().availableGeometry()
        # Если панель должна быть слева
        if self.dock_position == "left":
            self.setGeometry(QRect(
                screen.left() + self.dock_margin,  # X координата
                screen.top(),  # Y координата
                300,  # Ширина
                screen.height()  # Высота
            ))
            self.setFixedWidth(300)  # Фиксируем ширину в закрепленном режиме
            self.setFixedHeight(screen.height())  # Фиксируем высоту
        # Если панель должна быть справа
        elif self.dock_position == "right":
            self.setGeometry(QRect(
                screen.right() - 300 - self.dock_margin,  # X координата
                screen.top(),  # Y координата
                300,  # Ширина
                screen.height()  # Высота
            ))
            self.setFixedWidth(300)  # Фиксируем ширину в закрепленном режиме
            self.setFixedHeight(screen.height())  # Фиксируем высоту
        # Для режима float не устанавливаем фиксированные размеры
        elif self.dock_position == "float":
            self.setMinimumSize(200, 200)
            self.setMaximumSize(16777215, 16777215)
            self.setFixedSize(QSize())  # Снимаем фиксированные размеры

    # Метод инициализации контекстного меню
    def _init_position_menu(self):
        # Создаем меню с заголовком
        self.position_menu = QMenu("Позиция панели", self)

        # Создаем действие "Закрепить слева"
        self.pin_left_action = QAction("Закрепить слева", self, checkable=True)
        # Подключаем обработчик
        self.pin_left_action.triggered.connect(self._dock_to_left)

        # Создаем действие "Закрепить справа"
        self.pin_right_action = QAction("Закрепить справа", self, checkable=True)
        # Подключаем обработчик
        self.pin_right_action.triggered.connect(self._dock_to_right)

        # Создаем действие "Свободное перемещение"
        self.float_action = QAction("Свободное перемещение", self, checkable=True)
        # Подключаем обработчик
        self.float_action.triggered.connect(self._enable_floating)

        # Добавляем действия в меню
        self.position_menu.addActions([self.pin_left_action, self.pin_right_action, self.float_action])
        # Устанавливаем политику контекстного меню
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # Подключаем обработчик показа контекстного меню
        self.customContextMenuRequested.connect(self.show_context_menu)

    # Метод для закрепления панели слева
    def _dock_to_left(self):
        self.dock_position = "left"
        self.update_dock_position()
        self._update_menu_checks()

    # Метод для закрепления панели справа
    def _dock_to_right(self):
        self.dock_position = "right"
        self.update_dock_position()
        self._update_menu_checks()

    # Метод для включения свободного перемещения
    def _enable_floating(self):
        self.dock_position = "float"
        #self.update_dock_position()  # Обновляем геометрию
        # Устанавливаем начальные размеры и позицию
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(QRect(
            screen.right() - 350,  # X координата (немного левее правого края)
            screen.top() + 100,  # Y координата (немного ниже верхнего края)
            300,  # Ширина
            screen.height() - 200  # Высота (меньше высоты экрана)
        ))
        self._update_menu_checks()

    # Метод обновления состояния пунктов меню
    def _update_menu_checks(self):
        self.pin_left_action.setChecked(self.dock_position == "left")
        self.pin_right_action.setChecked(self.dock_position == "right")
        self.float_action.setChecked(self.dock_position == "float")

    # Метод показа контекстного меню
    def show_context_menu(self, pos):
        # Показываем меню в указанной позиции
        self.position_menu.exec(self.mapToGlobal(pos))

    # Добавляем  методы сворачивание/разворачиване:
    def collapse_all(self):
        """Сворачивает все узлы дерева (рекурсивно)"""
        root = self.tree_model.root_item
        for i in range(len(root.child_items)):
            index = self.tree_model.index(i, 0, QModelIndex())
            self._collapse_recursive(index)

    def expand_all(self):
        """Разворачивает все узлы дерева (рекурсивно)"""
        root = self.tree_model.root_item
        for i in range(len(root.child_items)):
            index = self.tree_model.index(i, 0, QModelIndex())
            self._expand_recursive(index)

    def _on_tree_item_double_clicked(self, index):
        """Обработка двойного клика по элементу дерева"""
        if not index.isValid():
            return

        item = index.internalPointer()
        if not item:
            return

        if item.type == "folder":
            # Игнорируем двойной клик, если он был на кнопке
            pos = self.tree_view.viewport().mapFromGlobal(QCursor.pos())
            button_rect = QRect(self.tree_view.visualRect(index).left(),
                                self.tree_view.visualRect(index).top(),
                                20,
                                self.tree_view.visualRect(index).height())
            if not button_rect.contains(pos):
                if self.tree_view.isExpanded(index):
                    self.tree_view.collapse(index)
                else:
                    self.tree_view.expand(index)

    def _expand_recursive(self, index):
        """Рекурсивно разворачивает папку и все подпапки"""
        if not index.isValid():
            return

        self.tree_view.expand(index)
        model = index.model()
        for i in range(model.rowCount(index)):
            child_index = model.index(i, 0, index)
            if model.is_folder(child_index):
                self._expand_recursive(child_index)

    def _collapse_recursive(self, index):
        """Рекурсивно сворачивает папку и все подпапки"""
        self.tree_view.collapse(index)
        model = index.model()
        for i in range(model.rowCount(index)):
            child_index = model.index(i, 0, index)
            if model.is_folder(child_index):
                self._collapse_recursive(child_index)

    def hasChildren(self, parent=QModelIndex()):
        """Переопределяем метод для корректного отображения треугольников раскрытия"""
        if not parent.isValid():
            return len(self.root_item.child_items) > 0
        item = parent.internalPointer()
        return len(item.child_items) > 0


# ===================================================================
# ЗАПУСК ПРИЛОЖЕНИЯ
# ===================================================================

if __name__ == "__main__":
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Создаем экземпляр боковой панели
    panel = SidePanel()
    # Устанавливаем заголовок окна
    panel.setWindowTitle("Системная боковая панель")

    # Показываем панель
    panel.show()
    # Запускаем цикл обработки событий
    sys.exit(app.exec())
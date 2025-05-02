import sys
import os
import json
from PySide6.QtWidgets import (QSplitter, QTreeView, QTextEdit, QWidget, 
                              QVBoxLayout, QApplication, QMenu,
                              QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QFileDialog,
                              QFileIconProvider, QStyledItemDelegate, QStyleOptionViewItem, QStyle)
from PySide6.QtCore import (Qt, QFileSystemWatcher, Signal, QObject,  QRect, QSize,
                            QAbstractItemModel, QModelIndex)
from PySide6.QtGui import QAction, QIcon, QFont, QColor

# Импорт компонентов ANTLR
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from ANTLR4.st_Files.STFileLexer import STFileLexer
from ANTLR4.st_Files.STFileParser import STFileParser
from ANTLR4.st_Files.STFileListener import  STFileListener

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
        return 2

    '''def data(self, index, role=Qt.DisplayRole):
        """Возвращает данные для отображения"""
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        item = index.internalPointer()
        return item.item_data[index.column()]'''

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
                return QColor("#006400")            # Темно-зеленый для папок
            elif item.item_data[1] == "template":
                return QColor("#00008B")            # Темно-синий для шаблонов

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
            return ["Имя", "Тип"][section]
        return None

    def add_file(self, file_path):
        """Добавляет новый ST-файл в модель"""
        # Получаем результат парсинга, который теперь содержит и структуру, и имя корневой папки
        result = self.parser.parse_st_file(file_path)

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

    def _build_tree(self, nodes, parent):
        """Рекурсивно строит дерево из данных"""
        for node in nodes:
            item = STFileTreeItem([node['name'], node['type'], node.get('content', '')], parent)
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
        lexer = STFileLexer(input_stream)  # Лексер
        token_stream = CommonTokenStream(lexer)  # Поток токенов
        parser = STFileParser(token_stream)  # Парсер
        tree = parser.fileStructure()  # Дерево разбора

        listener = StructureListener()  # Создаем listener здесь
        ParseTreeWalker().walk(listener, tree)

        # Возвращаем и структуру, и имя корневой папки
        return {
            'structure': listener.get_structure(),
            'root_name': listener.root_name
        }


class StructureListener(STFileListener):
    """Слушатель для построения структуры данных из дерева разбора"""
    def __init__(self):
        self.stack = [{'children': []}]  # Стек для отслеживания вложенности
        self.result = self.stack[0]  # Корневой элемент
        self.root_name = "Root"  # Добавляем поле для имени корневой папки
        self.found_first_folder = False

    def get_structure(self):
        """Возвращает собранную структуру"""
        return self.result['children']


    def enterTemplateHeader(self, ctx):
        """Обработка шаблона"""

        if not self.stack:  # Если стек пуст, выходим
            return

        # Получаем все строковые токены
        strings = [s.getText()[1:-1] for s in ctx.STRING()]
        name = strings[0] if strings else ""  # Имя из первого токена
        content = strings[4] if len(strings) > 4 else ""  # Контент из пятого токена

        self.stack[-1]['children'].append({
            'name': name,
            'type': 'template',
            'content': content
            })

    def enterFolderHeader(self, ctx):
        """Обработка входа в папку"""
        name = ctx.STRING(0).getText()[1:-1]  # Получаем имя папки (первый STRING)

        # Если это первая папка, сохраняем её имя
        if not self.found_first_folder:
            self.root_name = name
            self.found_first_folder = True
            return  # Выходим, не добавляя в структуру

        new_item = {
            'name': name,
            'type': 'folder',
            'children': []
        }
        self.stack[-1]['children'].append(new_item)
        self.stack.append(new_item)

    def exitFolderHeader(self, ctx):
        """Выход из папки"""
        if len(self.stack) > 1:
            self.stack.pop()

    # Добавляем обработку корневой папки (rootContent)
''' def enterRootContent(self, ctx):
        """Обработка корневой папки (правило rootContent из STFile.g4)"""
        # Получаем имя корневой папки (если есть)
        name = "Root"  # Значение по умолчанию
        if ctx.int_value():  # Если есть числовое значение (например, ID папки)
            pass  # Можно добавить логику обработки

        # Создаем элемент корневой папки
        root_item = {
            'name': name,
            'type': 'folder',  # Или другой тип, если нужно
            'children': []
        }
        self.stack[-1]['children'].append(root_item)
        self.stack.append(root_item)

    def exitRootContent(self, ctx):
        """Выход из корневой папки"""
        if len(self.stack) > 1:
            self.stack.pop()
'''
# ===================================================================
# ГРАФИЧЕСКИЙ ИНТЕРФЕЙС
# ===================================================================

# Добавляем после создания tree_view, но до установки модели
class TreeItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        # Получаем тип элемента и уровень вложенности из модели
        item_type = index.data(Qt.UserRole + 2)
        level = index.data(Qt.UserRole + 1)

        # Сохраняем оригинальные параметры отрисовки
        original_padding = option.rect.left()

        # Увеличиваем отступ в зависимости от уровня вложенности
        if level is not None and level > 0:
            indent = level * 15  # 15 пикселей на каждый уровень вложенности
            option.rect.adjust(indent, 0, 0, 0)

        # Устанавливаем разные стили для разных типов элементов
        if item_type == "template":
            # Дополнительный отступ для шаблонов
            option.rect.adjust(15, 0, 0, 0)

        # Вызываем оригинальный метод paint
        super().paint(painter, option, index)

        # Восстанавливаем оригинальные параметры
        option.rect.adjust(-option.rect.left() + original_padding, 0, 0, 0)

#Класс для обработки сигналов панели
class SidePanelSignals(QObject):
    #Сигнал при выборе файла (передает путь к файлу)
    file_selected = Signal(str)
    #Сигнал при изминении файла(передает путь к измененному файлу)
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
        self.current_file = None # Инициализация переменной

        self._update_menu_checks()

        # Загружаем сохраненные файлы при старте
        self._load_saved_files()


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

        # Растягивающийся элемент между кнопками и заголовком
        # Добавляем кнопки в layout заголовка:
        # 1. Кнопка сворачивания
        title_layout.addWidget(self.minimize_btn)
        # 2 Добавлена кнопка загрузки
        title_layout.addWidget(self.load_btn)
        # 3. Растягивающийся элемент (пустое пространство)
        title_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # 4. Кнопка закрытия
        title_layout.addWidget(self.close_btn)

        # Добавляем панель заголовка в основной layout
        main_layout.addWidget(self.title_bar)

        # Создаем разделитель с вертикальной ориентацией
        self.splitter = QSplitter(Qt.Vertical)

        # Создаем дерево для отображения файловой системы
        self.tree_view = QTreeView()
        # Показываем заголовки у дерева
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setIndentation(12)  # Уменьшаем отступ
        self.tree_view.setAnimated(True)  # Анимация раскрытия
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setRootIsDecorated(True)  # Показываем декор для корневых элементов
        self.tree_view.setSortingEnabled(False)
        # Устанавливаем делегат
        self.tree_view.setItemDelegate(TreeItemDelegate(self.tree_view))
        # Настройка стиля дерева
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: #f5f5f5;
                border: none;
                outline: 0;
                font-size: 12px;
            }
            QTreeView::item {
                padding: 4px 1px;
                border: none;
            }
            QTreeView::item:hover {
                background-color: #e0e0e0;
            }
            QTreeView::item:selected {
                background-color: #d0e3ff;
                color: #000000;
                border-radius: 2px;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: none;
                font-size: 11px;
            }
            QTreeView::branch {
                margin-right: 5px;
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

    #Обработка сохраненя и загрузки файлов st
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
            self,
            "Открыть ST-файлы",
            "",
            "ST Files (*.st)"
        )
        for file in files:
            self.tree_model.add_file(file)  # Добавляем файлы в модель

            # Сохраняем список файлов
            self._save_files_to_json()

    def _on_tree_item_clicked(self, index):
        """Обработка клика по элементу дерева"""
        item = index.internalPointer()
        if item.item_data[1] == 'template':
            self.content_view.setPlainText(item.item_data[2])  # Показываем контент
    # Обработчик нажатия кнопки мыши (для перемещения окна)
    def mousePressEvent(self, event):
        # Если нажата левая кнопка мыши в области заголовка (верхние 30 пикселей)
        if event.button() == Qt.LeftButton and event.position().y() < 30:
            # Запоминаем начальную позицию курсора
            self.drag_start_position = event.globalPosition().toPoint()
            # Запоминаем текущую позицию окна
            self.drag_window_position = self.pos()
            # Принимаем событие
            event.accept()

    # Обработчик перемещения мыши (для перемещения окна)
    def mouseMoveEvent(self, event):
        # Если начата операция перетаскивания
        if hasattr(self, 'drag_start_position'):
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
            # Принимаем событие
            event.accept()

    # Обработчик клика по элементу дерева
    def _on_tree_item_clicked(self, index):
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
            self.file_watcher.addPath(file_path)

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

    #Метод удаления файла
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
        """Показывает контекстное меню для дерева файлов"""
        index = self.tree_view.indexAt(pos)
        if not index.isValid():
            return

        item = index.internalPointer()
        if item.item_data[1] != "file":
            return  # Показываем меню только для файлов

        menu = QMenu(self)

        # Действие для удаления файла
        remove_action = QAction("Удалить из списка", self)
        remove_action.triggered.connect(lambda: self.remove_file(item.item_data[2]))
        menu.addAction(remove_action)

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
                screen.left() + self.dock_margin, # X координата
                screen.top(),                     # Y координата
                300,                              # Ширина
                screen.height()                   # Высота
            ))
        # Если панель должна быть справа
        elif self.dock_position == "right":
            self.setGeometry(QRect(
                screen.right() - 300 - self.dock_margin,    # X координата
                screen.top(),                               # Y координата
                300,                                        # Ширина
                screen.height()                             # Высота
            ))

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
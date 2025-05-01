import sys
import os
from PySide6.QtWidgets import (QSplitter, QTreeView, QTextEdit, QWidget, 
                              QVBoxLayout, QApplication, QFileSystemModel, QMenu,
                              QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QFileDialog
                              )
from PySide6.QtCore import (Qt, QFileSystemWatcher, Signal, QObject, QDir, QRect,
                            QAbstractItemModel, QModelIndex)
from PySide6.QtGui import QAction, QScreen

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


# Модель данных для дерева

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

        # Собираем структуру данных
        listener = StructureListener()
        ParseTreeWalker().walk(listener, tree)
        return listener.get_structure()


class StructureListener(STFileListener):
    """Слушатель для построения структуры данных из дерева разбора"""

    def __init__(self):
        self.stack = [{'children': []}]  # Стек для отслеживания вложенности
        self.result = self.stack[0]  # Корневой элемент

    def get_structure(self):
        """Возвращает собранную структуру"""
        return self.result['children']

    def enterEntry(self, ctx):
        """Обработка входа в элемент (папку)"""
        try:
            # Проверяем наличие строковых токенов
            strings = [s for s in dir(ctx) if 'STRING' in s]
            if not strings:
                return

            # Более безопасный способ получить имя
            name = ""
            if hasattr(ctx, 'STRING') and ctx.STRING():
                name = ctx.STRING(0).getText()[1:-1]  # Удаляем кавычки
            elif hasattr(ctx, 'templateHeader') and ctx.templateHeader():
                # Обработка шаблона
                return

            new_item = {
                'name': name,
                'type': 'folder',
                'children': []
            }
            self.stack[-1]['children'].append(new_item)
            self.stack.append(new_item)
        except Exception as e:
            print(f"Ошибка при обработке entry: {str(e)}")
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
        # Инициализация пользовательского интерфейса
        self._init_ui()
        # Инициализация контекстного меню для управления позицией
        self._init_position_menu()
        # Настройка прикрепления к краям экрана
        self._setup_screen_edge_docking()
        # Текущий выбранный файл (хранит путь)
        self.current_file = None # Инициализация переменной

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
    # Обработчик нажатия кнопки мыши (для перемещения окна)
    def mousePressEvent(self, event):
        # Если нажата левая кнопка мыши в области заголовка (верхние 30 пикселей)
        if event.button() == Qt.LeftButton and event.y() < 30:  # Проверяем клик в области заголовка
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

    # Метод настройки прикрепления к краям экрана
    def _setup_screen_edge_docking(self):
        """Настройка прикрепления к краям экрана"""
        # Позиция по умолчанию - слева
        self.dock_position = "left"  # left/right/float
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
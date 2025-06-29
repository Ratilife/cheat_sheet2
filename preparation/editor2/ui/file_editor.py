# file_editor.py
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTextEdit, QTreeView, QFileDialog,
                               QMessageBox, QSplitter, QStyle, QInputDialog, QApplication, QButtonGroup, QRadioButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from preparation.editor2.widgets.delegates import TreeItemDelegate
from preparation.editor2.observers.my_base_observer import MyBaseObserver
from preparation.editor2.managers.context_menu_manager import ContextMenuHandler


class FileEditorWindowObserver(MyBaseObserver):
    def __init__(self):
        super().__init__()
class FileEditorWindow(QMainWindow):
    """
        Главное окно редактора файлов с поддержкой форматов .st и .md.
        Обеспечивает создание, редактирование и сохранение файлов.
    """

    def __init__(self, tree_model_manager=None, toolbar_manager=None):

        super().__init__()
        self.tree_view = QTreeView()
        #Создаем экземпляр класса для сигналов
        self.observer = FileEditorWindowObserver()


        self.setWindowTitle("Редактор файлов")
        self.setMinimumSize(600, 500)  # Минимальные размеры окна

        # TODO NOTE - код нужно проверить на использование
        # 1. Делегат с кастомизацией (пример)
        delegate_config = {
            'indent': 25,  # Увеличенный отступ
            'button_size': 18,
            'icons': {
                'folder': QIcon.fromTheme("folder-documents"),  # Своя иконка
                'file': QIcon(":/icons/custom_file.png")  # Кастомная иконка
            }
        }
        self.delegate = TreeItemDelegate(parent=self.tree_view, config=delegate_config)  # ← Конфиг
        self.tree_view.setItemDelegate(self.delegate)
        #self._init_ui()  # Инициализация интерфейса
        # Инициализация UI, если менеджеры переданы
        if tree_model_manager and toolbar_manager:
            self._setup_managers(tree_model_manager, toolbar_manager)


    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        if not hasattr(self, 'parent_toolbar'):
            raise RuntimeError("toolbar_manager не установлен. Вызовите setup_managers()")
        # Основной виджет и layout
        main_widget = QWidget()                     # Создаем центральный виджет окна
        self.setCentralWidget(main_widget)          # Устанавливаем его как центральный виджет окна
        main_layout = QVBoxLayout(main_widget)      # Создаем вертикальный layout для основного виджета
        main_layout.setContentsMargins(5, 5, 5, 5)  # Устанавливаем минимальные отступы layout


        # Разделитель для дерева и редактора
        self.splitter = QSplitter(Qt.Vertical)  # Вертикальный разделитель

        # Текстовый редактор
        self.text_editor = QTextEdit()  # Основной текстовый редактор для ST файлов
        self.text_editor.setAcceptRichText(False)  # Режим plain text  Отключаем форматированный текст

        #Создаем панель инструментов над деревом
        toolbar_to_tree_layout = self.parent_toolbar.get_above_tree_toolbar_editor()
        main_layout.addWidget(toolbar_to_tree_layout)


        # Контейнер для редактора и кнопок
        editor_container = QWidget()  # Контейнерный виджет
        editor_layout = QVBoxLayout(editor_container)  # Вертикальный layout
        editor_layout.setContentsMargins(0, 0, 0, 0)  # Без отступов
        editor_layout.setSpacing(0)  # Без промежутков
        # Создаем панель инструментов над редактаром
        editor_toolbar = self.parent_toolbar.get_editor_toolbar()
        # Добавляем кнопки над редактором
        editor_layout.addWidget(editor_toolbar)
        editor_layout.addWidget(self.text_editor)
        #Добавляем разделтель
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(editor_container)
        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)

        # Подключаем сигналы дерева файлов
        self.tree_view.doubleClicked.connect(self._on_tree_item_double_clicked)  #TODO - доработать

        # Добавьте в метод _init_ui класса FileEditorWindow после создания tree_view:
        self.tree_view.setHeaderHidden(False)  # Показываем заголовки
        self.tree_view.setIndentation(10)  # Отступ для вложенных элементов
        self.tree_view.setAnimated(True)  # Анимация раскрытия
        self.tree_view.setUniformRowHeights(True)  # Одинаковая высота строк
        self.tree_view.setRootIsDecorated(True)  # Показываем корневой элемент
        self.tree_view.setExpandsOnDoubleClick(True)  # Раскрытие двойным кликом
        self.tree_view.setSortingEnabled(False)  # Сортировка отключена

        # Устанавливаем политику контекстного меню для tree_view на "CustomContextMenu",
        # чтобы обработка вызова контекстного меню происходила вручную.
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)  #TODO - доработать

        # Подключаем сигнал customContextMenuRequested к методу _show_tree_context_menu,
        # чтобы при вызове контекстного меню отобразить пользовательское меню.
        self.tree_view.customContextMenuRequested.connect(self._show_tree_context_menu) #TODO - доработать



        # Установите делегат (если он используется)
        if hasattr(self.tree_model, 'delegate'):
            # Создаем новый делегат на основе родительского, но для текущего tree_view
            self.delegate = TreeItemDelegate(self.tree_view)
            self.tree_view.setItemDelegate(self.delegate)
        #Подключение контекстного меню к tree_view
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(
        self.context_menu_handler.show_tree_context_menu)

        # Настройте стиль (можно скопировать из панели)
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
    def center_window(self):
        """Центрирует окно на экране"""
        frame_geometry = self.frameGeometry()  # Получаем геометрию окна с учетом рамок
        screen_center = QApplication.primaryScreen().availableGeometry().center()  # Центр экрана
        frame_geometry.moveCenter(screen_center)  # Совмещаем центры
        self.move(frame_geometry.topLeft())  # Перемещаем окно

    def _setup_managers(self, tree_model_manager, toolbar_manager):
        """Устанавливает менеджеры и инициализирует интерфейс"""
        # ✅ Реализовано: 29.06.2025
        if not tree_model_manager or not toolbar_manager:
            raise ValueError("tree_model_manager и toolbar_manager обязательны")
        self.tree_model = tree_model_manager.get_model()
        self.parent_toolbar = toolbar_manager
        #Подключение контекстного меню к tree_view
        self.context_menu_handler = ContextMenuHandler(
            tree_view=self.tree_view,
            delete_manager=tree_model_manager.delete_manager
        )
        self._init_ui()
        self.tree_view.setModel(self.tree_model)


    #---- Нужно проверить методы -------
    def _on_tree_item_double_clicked(self, index):
        """
        Обработка двойного клика по элементу дерева

        Args:
            index: Индекс элемента в дереве
        """
        if not index.isValid():
            return

        item = index.internalPointer()
        if not item:
            return

        # Загружаем содержимое файла или шаблона
        if item.item_data[1] in ['file', 'markdown']:
            file_path = item.item_data[2]
            self._load_file_content(file_path)
        elif item.item_data[1] == 'template':
            self.current_file_path = None
            self.text_editor.setPlainText(item.item_data[2])

    def _show_tree_context_menu(self, pos):
        """Показывает контекстное меню для дерева файлов"""
        # ✅ Реализовано: 29.06.2025
        self.context_menu_handler.show_tree_context_menu(pos)

    def _remove_item(self, index, delete_from_disk=False):
        if self.delete_manager.execute_removal(index, delete_from_disk):
            self.toolbar_manager.save_files_to_json()
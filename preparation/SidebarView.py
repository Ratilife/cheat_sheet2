import sys

from PySide6.QtWidgets import (QDockWidget, QSplitter, QTreeView, QMenu,
                               QTextEdit, QWidget, QVBoxLayout, QApplication, QFileSystemModel)
from PySide6.QtCore import Qt, QFileSystemWatcher, Signal, QObject, QDir

from PySide6.QtGui import QAction

class SidePanelSignals(QObject):
    """Сигналы боковой панели"""
    file_selected = Signal(str)  # Сигнал при выборе файла
    file_changed = Signal(str)  # Сигнал при изменении файла


class SidePanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Боковая панель", parent) #инициализируется родительский класс
        self.signals = SidePanelSignals() #создается экземпляр сигналов

        # Инициализация UI
        self._init_ui()

        # Настройки позиционирования
        self._init_dock_settings()

        # Меню для управления позиционированием
        self._init_position_menu()

        # Наблюдатель за изменениями файлов
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self._on_file_changed)

        # Текущий выбранный файл
        self.current_file = None

    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""

        # Основной виджет и компоновка
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Разделитель для двух областей
        self.splitter = QSplitter(Qt.Vertical)
        
        # Верхняя часть - дерево файлов
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.clicked.connect(self._on_tree_item_clicked)
        
        # Нижняя часть - просмотр содержимого
        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        
        # Добавляем виджеты в разделитель
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.content_view)
        self.splitter.setStretchFactor(0, 2)  # Дерево занимает 2/3 пространства
        self.splitter.setStretchFactor(1, 1)  # Контент 1/3
        
        # Добавляем разделитель в компоновку
        self.layout.addWidget(self.splitter)
        self.setWidget(self.main_widget)
    def _init_dock_settings(self):
        """Настройка поведения dock-виджета"""
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)

        # По умолчанию прикрепляем слева
        self.default_dock_area = Qt.LeftDockWidgetArea
        self.dock_area = self.default_dock_area
        self.setFloating(False)

    def _init_position_menu(self):
        """Создание меню для управления позицией"""
        self.position_menu = QMenu("Позиция панели", self)

        # Действия меню
        self.pin_left_action = QAction("Закрепить слева", self)
        self.pin_left_action.triggered.connect(lambda: self.set_dock_position(Qt.LeftDockWidgetArea))

        self.pin_right_action = QAction("Закрепить справа", self)
        self.pin_right_action.triggered.connect(lambda: self.set_dock_position(Qt.RightDockWidgetArea))

        self.float_action = QAction("Свободное перемещение", self)
        self.float_action.triggered.connect(self.toggle_floating)

        self.position_menu.addAction(self.pin_left_action)
        self.position_menu.addAction(self.pin_right_action)
        self.position_menu.addAction(self.float_action)

        # Добавляем меню в контекстное меню виджета
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """Показ контекстного меню"""
        self.position_menu.exec_(self.mapToGlobal(pos))

    def set_dock_position(self, area):
        """Установка позиции панели (левый/правый край)"""
        if area in (Qt.LeftDockWidgetArea, Qt.RightDockWidgetArea):
            self.dock_area = area
            self.setFloating(False)
            if self.parent() is not None:
                self.parent().addDockWidget(area, self)

            # Обновляем состояние действий меню
            self.pin_left_action.setChecked(area == Qt.LeftDockWidgetArea)
            self.pin_right_action.setChecked(area == Qt.RightDockWidgetArea)
            self.float_action.setChecked(False)

    def toggle_floating(self):
        """Переключение режима свободного перемещения"""
        is_floating = not self.isFloating()
        self.setFloating(is_floating)

        # Обновляем состояния действий меню
        self.float_action.setChecked(is_floating)
        self.pin_left_action.setChecked(False)
        self.pin_right_action.setChecked(False)

    def set_tree_model(self, model):
        """Установка модели данных для дерева"""
        self.tree_view.setModel(model)
        self.tree_view.expandAll()

    def set_content(self, text):
        """Установка содержимого для просмотра"""
        self.content_view.setPlainText(text)

    def set_markdown_content(self, markdown_text):
        """Установка Markdown содержимого (можно добавить рендеринг)"""
        self.content_view.setMarkdown(markdown_text)

    def _on_tree_item_clicked(self, index):
        """Обработка выбора элемента в дереве"""
        model = index.model()
        if hasattr(model, 'filePath'):
            file_path = model.filePath(index)
            self.current_file = file_path
            self.signals.file_selected.emit(file_path)
            
            # Добавляем файл в наблюдатель
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())
            self.file_watcher.addPath(file_path)

    def _on_file_changed(self, path):
        """Обработка изменения файла"""
        if path == self.current_file:
            self.signals.file_changed.emit(path)

    def clear(self):
        """Очистка панели"""
        self.tree_view.setModel(None)
        self.content_view.clear()
        if self.file_watcher.files():
            self.file_watcher.removePaths(self.file_watcher.files())
        self.current_file = None


if __name__ == "__main__":
    # Создаем приложение
    app = QApplication(sys.argv)

    # Создаем и настраиваем боковую панель
    panel = SidePanel()
    panel.setWindowTitle("Тест боковой панели")
    panel.resize(800, 600)

    # Создаем тестовую модель для дерева (используем QFileSystemModel для демонстрации)
    model = QFileSystemModel()
    model.setRootPath(QDir.currentPath())

    # Устанавливаем модель в дерево
    panel.set_tree_model(model)
    panel.tree_view.setRootIndex(model.index(QDir.currentPath()))

    # Устанавливаем тестовое содержимое
    panel.set_content("Выберите файл в дереве для просмотра содержимого")
    # Или для Markdown:
    # panel.set_markdown_content("# Тестовая панель\n\nВыберите файл в дереве")

    # Показываем панель
    panel.show()

    # Запускаем приложение
    sys.exit(app.exec())
# file_editor.py
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTextEdit, QTreeView, QFileDialog,
                               QMessageBox, QSplitter, QStyle, QInputDialog, QApplication, QButtonGroup, QRadioButton)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction, QIcon
from preparation.editor2.widgets.delegates import TreeItemDelegate


class FileEditorWindow(QMainWindow):
    """
        Главное окно редактора файлов с поддержкой форматов .st и .md.
        Обеспечивает создание, редактирование и сохранение файлов.
    """

    def __init__(self, parent=None):

        super().__init__(parent)
        self.tree_view = QTreeView()
        self.parent_panel = parent  # Ссылка на родительскую панель
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
        #------- код нужно проверить на использование
        # 2. Установка модели
        self.tree_view.setModel(self.tree_model)
        self._init_ui()  # Инициализация интерфейса

    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""


    def center_window(self):
        """Центрирует окно на экране"""
        frame_geometry = self.frameGeometry()  # Получаем геометрию окна с учетом рамок
        screen_center = QApplication.primaryScreen().availableGeometry().center()  # Центр экрана
        frame_geometry.moveCenter(screen_center)  # Совмещаем центры
        self.move(frame_geometry.topLeft())  # Перемещаем окно

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
        self.context_menu_handler.show_tree_context_menu(pos)

    def _remove_item(self, index, delete_from_disk=False):
        if self.delete_manager.execute_removal(index, delete_from_disk):
            self._save_files_to_json()
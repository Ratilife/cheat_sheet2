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

    def __init__(self):
        # В методе _init_ui():
        self.tree_view = QTreeView()

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

        # 2. Установка модели
        self.tree_view.setModel(self.tree_model)

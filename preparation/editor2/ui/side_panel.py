import sys
import os
import json
from PySide6.QtWidgets import (QSplitter, QTreeView, QWidget,
                               QVBoxLayout, QApplication, QMenu,
                               QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QFileDialog, QMessageBox)
from PySide6.QtCore import (Qt, QFileSystemWatcher, Signal, QObject, QRect, QSize,
                             QModelIndex)
from PySide6.QtGui import QAction,  QColor, QCursor, QPen, QPainter
from preparation.editor2.ui.file_editor import FileEditorWindow
from preparation.editor2.widgets.delegates import TreeItemDelegate


# Класс для обработки сигналов панели
class SidePanelSignals(QObject):
    # Сигнал при выборе файла (передает путь к файлу)
    file_selected = Signal(str)
    # Сигнал при изминении файла(передает путь к измененному файлу)
    file_changed = Signal(str)


# Основной класс боковой панели
class SidePanel(QWidget):

    def __init__(self):

        self.tree_view = QTreeView()  # Создание дерева

        # 1. Инициализация делегата (минимальная настройка)

        self.delegate = TreeItemDelegate(parent=self.tree_view)  # ← Делегат привязан к tree_view
        self.tree_view.setItemDelegate(self.delegate)  # ← Установка делегата

        # 2. Установка модели (ПОСЛЕ делегата!)
        self.tree_view.setModel(self.tree_model)


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
import os
from PySide6.QtCore import (QModelIndex)
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from preparation.editor2.ui.file_editor import FileEditorWindow  # Для аннотаций
    from preparation.editor2.ui.side_panel import SidePanel
class TreeManager:
    """
        Класс для управления деревом (разворачиванием/сворачиванием узлов).
        Обеспечивает функциональность работы с древовидными структурами в GUI.
    """
    def __init__(self, tree_view):
        """
                Инициализация менеджера дерева.

                Args:
                    tree_view: Объект представления дерева (QTreeView или аналогичный),
                              с которым будет работать менеджер.
        """
        self.tree_view = tree_view          # Сохраняем ссылку на виджет дерева


    def expand_all(self):
        """
                Разворачивает все узлы дерева.
                Использует встроенную функцию expandAll() виджета дерева.
        """
        self.tree_view.expandAll()   # Вызываем метод разворачивания всех узлов

    def collapse_all(self):
        """
                Сворачивает все узлы дерева.
                Использует встроенную функцию collapseAll() виджета дерева.
        """
        self.tree_view.collapseAll()    # Вызываем метод сворачивания всех узлов

    def expand_recursive(self, index):
        """
                Рекурсивно разворачивает узел и все его подузлы (только для папок).

                Args:
                    index: Индекс модели, представляющий узел, который нужно развернуть.
        """
        if not index.isValid():                     # Проверяем, является ли индекс допустимым
            return                                  # Если индекс недопустим, прекращаем выполнение
        self.tree_view.expand(index)                # Разворачиваем текущий узел
        model = index.model()                       # Получаем модель данных для текущего индекса
        # Рекурсивно обрабатываем все дочерние элементы
        for i in range(model.rowCount(index)):      # Для каждого дочернего элемента
            child_index = model.index(i, 0, index)  # Получаем индекс дочернего элемента
            # Проверяем, является ли дочерний элемент папкой
            if model.is_folder(child_index):
                self.expand_recursive(child_index)  # Рекурсивный вызов для папок

    def collapse_recursive(self, index):
        """
                Рекурсивно сворачивает узел и все его подузлы (только для папок).

                Args:
                    index: Индекс модели, представляющий узел, который нужно свернуть.
        """
        self.tree_view.collapse(index)               # Сворачиваем текущий узел
        model = index.model()                        # Получаем модель данных для текущего индекса
        # Рекурсивно обрабатываем все дочерние элементы
        for i in range(model.rowCount(index)):       # Для каждого дочернего элемента
            child_index = model.index(i, 0, index)   # Получаем индекс дочернего элемента
            # Проверяем, является ли дочерний элемент папкой
            if model.is_folder(child_index):
                self.collapse_recursive(child_index) # Рекурсивный вызов для папок

    def setup_double_click_handler(self, context: Union["FileEditorWindow", "SidePanel"]) -> None:
        """Подключает обработчик двойного клика к дереву."""
        self.tree_view.doubleClicked.connect(
            lambda idx: self._on_tree_item_double_clicked(idx, context)
        )

    def _on_tree_item_double_clicked(self, index: QModelIndex, context) -> None:
        """
        Общий метод для обработки двойного клика.
        context: объект FileEditorWindow или SidePanel, где есть:
          - _load_file_content(file_path)
          - text_editor
          - current_file_path
        """
        if not index.isValid():
            return

        item = index.internalPointer()
        if not item:
            return

        if item.item_data[1] in ['file', 'markdown']:
            file_path = item.item_data[2]
            context._load_file_content(file_path) # TODO изменить код взять из другого модуля
        elif item.item_data[1] == 'template':
            context.current_file_path = None   # TODO разобраться нужно менять или оставить как есть
            context.text_editor.setPlainText(item.item_data[2])

    def _update_tree_view(self):
        """
        Обновление отображения дерева файлов.
        В текущей реализации не завершено - нужно подключить модель дерева.
        """
        if not self.current_structure:
            return

        # TODO: Реализовать через QStandardItemModel
        pass
    def hasChildren(self, parent=QModelIndex()):
        """Переопределяем метод для корректного отображения треугольников раскрытия"""
        if not parent.isValid():
            return len(self.root_item.child_items) > 0
        item = parent.internalPointer()
        return len(item.child_items) > 0


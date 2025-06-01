# context_menu.py
from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction

class ContextMenuHandler:
    def __init__(self, tree_view, delete_manager):
        self.tree_view = tree_view
        self.delete_manager = delete_manager

    def show_tree_context_menu(self, pos):
        """Показывает контекстное меню для дерева файлов"""
        index = self.tree_view.indexAt(pos)
        if not index.isValid():
            return

        item = index.internalPointer()
        menu = QMenu(self.tree_view)

        item_type = item.item_data[1]

        if item_type in ['file', 'markdown']:
            delete_menu = menu.addMenu("Удалить")

            delete_from_tree = delete_menu.addAction("Удалить из дерева")
            delete_from_tree.triggered.connect(
                lambda: self.delete_manager.execute_removal(index, False))

            delete_completely = delete_menu.addAction("Удалить полностью")
            delete_completely.triggered.connect(
                lambda: self.delete_manager.execute_removal(index, True))
        else:
            delete_action = menu.addAction("Удалить")
            delete_action.triggered.connect(
                lambda: self.delete_manager.execute_removal(index, False))

        if item.item_data[1] != "file":
            remove_action = QAction("Удалить из списка", self.tree_view)
            remove_action.triggered.connect(
                lambda: self.delete_manager.remove_file(item.item_data[2]))
            menu.addAction(remove_action)
        elif item.item_data[1] == "folder":
            expand_action = QAction("Развернуть", self.tree_view)
            expand_action.triggered.connect(lambda: self.tree_view.expand(index))
            menu.addAction(expand_action)

            collapse_action = QAction("Свернуть", self.tree_view)
            collapse_action.triggered.connect(lambda: self.tree_view.collapse(index))
            menu.addAction(collapse_action)

            menu.addSeparator()

            expand_all_action = QAction("Развернуть все вложенные", self.tree_view)
            expand_all_action.triggered.connect(lambda: self._expand_recursive(index))
            menu.addAction(expand_all_action)

            collapse_all_action = QAction("Свернуть все вложенные", self.tree_view)
            collapse_all_action.triggered.connect(lambda: self._collapse_recursive(index))
            menu.addAction(collapse_all_action)

        menu.exec(self.tree_view.viewport().mapToGlobal(pos))

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
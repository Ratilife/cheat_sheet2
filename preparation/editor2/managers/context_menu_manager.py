from PySide6.QtWidgets import QMenu
from PySide6.QtGui import QAction
#TODO - пересмотреть методику удаления
# TODO - участвует в удалении
class ContextMenuHandler:
    def __init__(self, tree_view, delete_manager):
        self.tree_view = tree_view
        self.delete_manager = delete_manager

    def show_tree_context_menu(self, pos):
        """Показывает контекстное меню для дерева файловДобавить комментарийБольше действий
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
        menu = QMenu(self.tree_view)
        # Определяем тип элемента
        item_type = item.item_data[1]

        if item_type in ['file', 'markdown']:
            # Для файлов создаем подменю с вариантами удаления
            delete_menu = menu.addMenu("Удалить")

            # Вариант 1: Удалить только из дерева
            delete_from_tree = delete_menu.addAction("Удалить из дерева")
            delete_from_tree.triggered.connect(
                lambda: self.delete_manager.execute_removal(index, False))
            # Вариант 2: Удалить полностью (с диска)
            delete_completely = delete_menu.addAction("Удалить полностью")
            delete_completely.triggered.connect(
                lambda: self.delete_manager.execute_removal(index, True))
        else:
            # Для других элементов (папки, шаблоны) простое удаление
            delete_action = menu.addAction("Удалить")
            delete_action.triggered.connect(
                lambda: self.delete_manager.execute_removal(index, False))
                # Для не-файлов delete_from_disk не применяется
        # Проверяем тип элемента (не является ли он файлом)
        if item.item_data[1] != "file":
            # Действие для удаления файла
            remove_action = QAction("Удалить из списка", self.tree_view)
            # Подключаем обработчик удаления файла
            remove_action.triggered.connect(
                lambda: self.delete_manager.remove_file(item.item_data[2]))
            # Добавляем действие в меню
            menu.addAction(remove_action)
        # Если элемент является папкой
        elif item.item_data[1] == "folder":
            # Действия для папок
            expand_action = QAction("Развернуть", self.tree_view)
            # Подключаем обработчик разворачивания текущей папки
            expand_action.triggered.connect(lambda: self.tree_view.expand(index))
            # Добавляем действие в меню
            menu.addAction(expand_action)
            # Создаем действие "Свернуть"
            collapse_action = QAction("Свернуть", self.tree_view)
            # Подключаем обработчик сворачивания текущей папки
            collapse_action.triggered.connect(lambda: self.tree_view.collapse(index))
            # Добавляем действие в меню
            menu.addAction(collapse_action)
            # Добавляем разделитель в меню
            menu.addSeparator()
            # Создаем действие "Развернуть все вложенные"
            expand_all_action = QAction("Развернуть все вложенные", self.tree_view)
            # Подключаем обработчик рекурсивного разворачивания
            expand_all_action.triggered.connect(lambda: self._expand_recursive(index))
            # Добавляем действие в меню
            menu.addAction(expand_all_action)
            # Создаем действие "Свернуть все вложенные"
            collapse_all_action = QAction("Свернуть все вложенные", self.tree_view)
            # Подключаем обработчик рекурсивного сворачивания
            collapse_all_action.triggered.connect(lambda: self._collapse_recursive(index))
            # Добавляем действие в меню
            menu.addAction(collapse_all_action)
        # Отображаем контекстное меню в позиции курсора
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
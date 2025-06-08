import os
from PySide6.QtCore import (QModelIndex)
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

    def _on_tree_item_clicked(self, index):
        """Обработка клика по элементу дерева"""
        item = index.internalPointer()
        if not item:
            return

        # Очищаем предыдущее содержимое
        #self.content_view.clear()

        # Очищаем предыдущее содержимое
        self.content_viewer.set_content("")  # используем метод MarkdownViewer

        # Обработка разных типов элементов
        if item.item_data[1] == 'template':
            #self.content_view.setPlainText(item.item_data[2])
            self.content_viewer.set_content(item.item_data[2])
            self.content_viewer.set_view_mode("text") # <-- Устанавливаем текстовый режим для шаблонов

        elif item.item_data[1] == 'file':  # <-- Обработка ST файлов
            file_path = item.item_data[2]
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        self.content_viewer.set_content(content)
                        self.content_viewer.set_view_mode("text")  # <-- Устанавливаем текстовый режим для ST файлов
                else:
                    self.content_viewer.set_content(f"Файл не найден: {file_path}")
            except Exception as e:
                self.content_viewer.set_content(f"Ошибка загрузки файла: {str(e)}")


        elif item.item_data[1] == 'markdown':
            file_path = item.item_data[2]
            try:
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        #self.content_view.setMarkdown(content)
                        self.content_viewer.set_content(content)
                        self.content_viewer.set_view_mode("markdown")  # <-- Устанавливаем markdown режим для MD файлов
                else:
                    #self.content_view.setPlainText(f"Файл не найден: {file_path}")
                    self.content_viewer.set_content(f"Файл не найден: {file_path}")
            except Exception as e:
                #self.content_view.setPlainText(f"Ошибка загрузки файла: {str(e)}")
                self.content_viewer.set_content(f"Ошибка загрузки файла: {str(e)}")

        # Для файлов добавляем в наблюдатель
        if item.item_data[1] in ['file', 'markdown']:
            file_path = item.item_data[2]
            self.current_file = file_path
            self.signals.file_selected.emit(file_path)

            # Обновляем наблюдатель файлов
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())
            self.file_watcher.addPath(file_path)
    def _on_item_double_clicked(self, index):
        """
        Обработчик двойного клика по элементу дерева.
        Должен загружать содержимое элемента в текстовый редактор.

        Args:
            index: Индекс элемента в дереве
        """
        # TODO: Реализовать загрузку содержимого
        pass
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

    def _on_tree_item_clicked_Определить_Нужен_Метод(self, index):
        """Обработка клика по элементу дерева"""
        item = index.internalPointer()
        if not item:
            return
from PySide6.QtWidgets import (QStyledItemDelegate, QStyleOptionButton, QStyle, QApplication)
from PySide6.QtCore import QEvent, Qt, QRect, QSize
from PySide6.QtGui import  QIcon

# Добавляем после создания tree_view, но до установки модели
class TreeItemDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tree_view = parent  # Сохраняем ссылку на tree_view
        # Добавляем иконки для кнопок
        self.expand_icon = QIcon.fromTheme("list-add")
        self.collapse_icon = QIcon.fromTheme("list-remove")
        self.button_size = 15
        self.fixed_indent = 20  # <-- Добавляем фиксированный отступ для кнопки


    def editorEvent(self, event, model, option, index):
        item = index.internalPointer()
        if not item or item.type != "folder" or not item.child_items:
            return super().editorEvent(event, model, option, index)

        # Получаем уровень вложенности
        level = index.data(Qt.UserRole + 1) or 0
        if level == 0:  # Пропускаем корневой элемент
            return super().editorEvent(event, model, option, index)

        # Рассчитываем позицию кнопки с учетом уровня вложенности
        #indent = (level - 1) * self.tree_view.indentation()
        button_rect = QRect(
            option.rect.left() + self.fixed_indent,  # <-- Используем фиксированный отступ,
            option.rect.top() ,
            self.button_size,
            option.rect.height()
        )

        # Обрабатываем клик
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if button_rect.contains(event.position().toPoint()):
                if self.tree_view.isExpanded(index):
                    self.tree_view.collapse(index)
                else:
                    self.tree_view.expand(index)
                return True

        return super().editorEvent(event, model, option, index)

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        item = index.internalPointer()
        if item and item.type == "folder" and (index.data(Qt.UserRole + 1) or 0) > 0:
            size.setWidth(size.width() + 22)  # Добавляем место для кнопки
        return size

    # неактуально. Возможно вдальнейшем удаление. Неспользуется

    def paint(self, painter, option, index):
        item = index.internalPointer()
        if not item:
            return super().paint(painter, option, index)

        original_rect = option.rect
        level = index.data(Qt.UserRole + 1) or 0
        base_indent = (level - 1) * self.tree_view.indentation() if level > 0 else 0 # ?

        # Сдвигаем все элементы согласно уровню
        option.rect = original_rect.adjusted(base_indent, 0, 0, 0)

        # Рисуем кнопку только для папок (кроме корневого уровня)
        if item.type == "folder" and item.child_items and level > 0:
            button_rect = QRect(
                original_rect.left() + self.fixed_indent,
                original_rect.top()+ (original_rect.height() - self.button_size) // 2,  # Центрируем по вертикали
                self.button_size,
                original_rect.height()
            )

            button_option = QStyleOptionButton()
            button_option.rect = button_rect
            button_option.state = QStyle.State_Enabled
            button_option.icon = self.collapse_icon if self.tree_view.isExpanded(index) else self.expand_icon
            button_option.iconSize = QSize(10, 10)

            QApplication.style().drawControl(QStyle.CE_PushButton, button_option, painter)
            option.rect.adjust(self.fixed_indent + self.button_size + 4, 0, 0, 0)  # Сдвигаем текст после кнопки

        # Дополнительный отступ для шаблонов
        if item.type == "template":
            option.rect.adjust(15, 0, 0, 0)

        super().paint(painter, option, index)
        option.rect = original_rect

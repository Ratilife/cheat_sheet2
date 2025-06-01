from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionButton, QStyle
from PySide6.QtCore import QEvent, Qt, QRect, QSize
from PySide6.QtGui import QIcon, QPainter, QPen, QColor, QFont


class TreeItemDelegate(QStyledItemDelegate):
    """
    Кастомизированный делегат для дерева файлов с:
    - Иконками для разных типов элементов
    - Кнопками раскрытия/сворачивания папок
    - Гибкими отступами и настройками
    """

    def __init__(self, parent=None, config=None):
        """
        :param parent: Родительский виджет (обычно QTreeView)
        :param config: Словарь с настройками {
            'indent': 20,          # Базовый отступ уровня
            'button_size': 16,     # Размер кнопки раскрытия
            'icons': {             # Кастомизированные иконки
                'folder': QIcon(...),
                'file': QIcon(...),
                ...
            }
        }
        """
        super().__init__(parent)

        # Конфигурация по умолчанию
        self._default_config = {
            'indent': 20,
            'button_size': 16,
            'icons': {
                'folder': QIcon.fromTheme("folder"),
                'file': QIcon.fromTheme("text-x-generic"),
                'template': QIcon.fromTheme("text-x-script"),
                'markdown': QIcon.fromTheme("text-markdown")
            }
        }

        # Применение пользовательских настроек
        self.config = {**self._default_config, **(config or {})}

        # Инициализация стилей
        self._init_styles()

    def _init_styles(self):
        """Инициализация стилей для разных типов элементов"""
        self._font = QFont()
        self._font.setBold(False)

        self._styles = {
            'folder': {
                'font': QFont(self._font),
                'color': QColor("#006400"),  # Темно-зелёный
                'font-weight': QFont.Bold
            },
            'file': {
                'color': QColor("#2a82da")  # Синий
            }
            # ... другие стили
        }

    def paint(self, painter, option, index):
        """
        Отрисовка элемента дерева с:
        - Фоном
        - Кнопкой раскрытия (для папок)
        - Иконкой
        - Текстом
        """
        # Получаем тип элемента и уровень вложенности
        item_type = index.data(Qt.UserRole + 2)  # 'folder', 'file' и т.д.
        level = index.data(Qt.UserRole + 1) or 0  # Уровень вложенности

        # 1. Рисуем стандартный фон
        option.widget.style().drawControl(
            QStyle.CE_ItemViewItem,
            option,
            painter,
            option.widget
        )

        # 2. Рисуем кнопку раскрытия (только для папок с вложенными элементами)
        if item_type == 'folder' and index.model().hasChildren(index):
            self._draw_expand_button(painter, option, index, level)

        # 3. Рисуем иконку и текст
        self._draw_icon_and_text(painter, option, index, item_type, level)

    def _draw_expand_button(self, painter, option, index, level):
        """Отрисовка кнопки раскрытия/сворачивания"""
        btn_rect = QRect(
            option.rect.left() + level * self.config['indent'],
            option.rect.top(),
            self.config['button_size'],
            option.rect.height()
        )

        btn_option = QStyleOptionButton()
        btn_option.rect = btn_rect
        btn_option.state = QStyle.State_Enabled

        # Выбираем иконку в зависимости от состояния
        is_expanded = option.widget.isExpanded(index)
        icon = QIcon.fromTheme("arrow-right") if is_expanded else QIcon.fromTheme("arrow-down")
        btn_option.icon = icon
        btn_option.iconSize = QSize(12, 12)

        option.widget.style().drawControl(
            QStyle.CE_PushButton,
            btn_option,
            painter
        )

    def _draw_icon_and_text(self, painter, option, index, item_type, level):
        """Отрисовка иконки и текста элемента"""
        # Настройки стиля для типа элемента
        style = self._styles.get(item_type, {})

        # Позиционирование
        icon_size = QSize(16, 16)
        text_offset = level * self.config['indent'] + self.config['button_size'] + 4

        # 1. Рисуем иконку
        icon = self.config['icons'].get(item_type, QIcon())
        icon_rect = QRect(
            option.rect.left() + text_offset,
            option.rect.top() + (option.rect.height() - icon_size.height()) // 2,
            icon_size.width(),
            icon_size.height()
        )
        painter.drawPixmap(icon_rect, icon.pixmap(icon_size))

        # 2. Рисуем текст
        text_rect = QRect(
            icon_rect.right() + 4,
            option.rect.top(),
            option.rect.width() - text_offset - icon_size.width() - 4,
            option.rect.height()
        )

        # Применяем стиль
        if 'color' in style:
            painter.setPen(style['color'])
        if 'font' in style:
            painter.setFont(style['font'])

        painter.drawText(
            text_rect,
            Qt.AlignLeft | Qt.AlignVCenter,
            index.data(Qt.DisplayRole)
        )

    def sizeHint(self, option, index):
        """Расчёт размера элемента с учётом отступов"""
        base_size = super().sizeHint(option, index)
        level = index.data(Qt.UserRole + 1) or 0

        # Увеличиваем ширину для кнопки и отступов
        base_size.setWidth(
            base_size.width() +
            level * self.config['indent'] +
            self.config['button_size']
        )
        return base_size

    def editorEvent(self, event, model, option, index):
        """
        Обработка кликов по кнопкам раскрытия
        """
        item_type = index.data(Qt.UserRole + 2)

        # Только для папок с детьми
        if (event.type() == QEvent.MouseButtonRelease and
                event.button() == Qt.LeftButton and
                item_type == 'folder' and
                model.hasChildren(index)):

            # Проверяем, был ли клик по кнопке
            level = index.data(Qt.UserRole + 1) or 0
            btn_rect = QRect(
                option.rect.left() + level * self.config['indent'],
                option.rect.top(),
                self.config['button_size'],
                option.rect.height()
            )

            if btn_rect.contains(event.pos()):
                option.widget.setExpanded(index, not option.widget.isExpanded(index))
                return True

        return super().editorEvent(event, model, option, index)
from PySide6.QtWidgets import QToolBar, QPushButton, QHBoxLayout, QWidget, QSplitter, QSizePolicy, QSpacerItem
from PySide6.QtCore import Qt
from typing import Union, List, Dict, Tuple

class UIManager:
    def __init__(self):
        self.buttons = {}
        self.panels = {}

    def create_button(self, name, text, icon=None, tooltip="", fixed_width=None, fixed_height=None):
        """Создает кнопку с настройками.

        Args:
            name (str): Идентификатор кнопки
            text (str): Текст кнопки
            icon (QIcon, optional): Иконка кнопки
            tooltip (str, optional): Всплывающая подсказка
            fixed_width (int, optional): Фиксированная ширина кнопки
            fixed_height (int, optional): Фиксированная высота кнопки
        """
        btn = QPushButton(text)
        if icon:
            btn.setIcon(icon)

        if tooltip:
            btn.setToolTip(tooltip)

        if fixed_width is not None and fixed_height is not None:
            btn.setFixedSize(fixed_width, fixed_height)

        self.buttons[name] = btn
        return btn

    def create_toolbar(self,
                  name: str,
                  buttons: List[Union[str, Dict[str, Tuple[int, int, QSizePolicy.Policy, QSizePolicy.Policy]]]],
                  margins: Tuple[int, int, int, int] = (5, 2, 5, 2)) -> QToolBar:
        """Создает панель инструментов с кнопками и настраиваемыми спейсерами.

        Args:
            name: Название панели инструментов
            buttons: Список элементов:
                - строка с именем кнопки ("open_btn")
                - словарь {"spacer": (width, height, hPolicy, vPolicy)}
            margins: Отступы содержимого (left, top, right, bottom)

        Returns:
        Созданная панель инструментов
        """
        toolbar = QToolBar(name)
        # Устанавливаем отступы
        toolbar.setContentsMargins(*margins)
        # Добавляем кнопки
        for item in buttons:
            if isinstance(item, dict) and "spacer" in item:
                # Настраиваемый спейсер
                width, height, h_policy, v_policy = item["spacer"]
                spacer = QSpacerItem(width, height, h_policy, v_policy)
                toolbar.addSpacerItem(spacer)
            elif item == "spacer":
                # Спейсер по умолчанию
                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
                toolbar.addSpacerItem(spacer)
            elif item in self.buttons:
                # Обычная кнопка
                toolbar.addWidget(self.buttons[item])

        self.panels[name] = toolbar
        return toolbar

    def create_horizontal_panel(self, name, buttons):
        """Создает горизонтальную панель с кнопками (для SidePanel)."""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        for btn_name in buttons:
            if btn_name in self.buttons:
                layout.addWidget(self.buttons[btn_name])
        self.panels[name] = panel
        return panel

    def create_splitter(self, orientation=Qt.Vertical, sizes=None, handle_width=5, handle_style="background: #ccc;"):
        """Создает и настраивает разделитель.

        Args:
            orientation (Qt.Orientation): Вертикальный (Qt.Vertical) или горизонтальный (Qt.Horizontal)
            sizes (list[int]): Размеры областей (например, [300, 100])
            handle_width (int): Ширина разделителя в пикселях
            handle_style (str): CSS-стиль для ручки разделителя
        """
        splitter = QSplitter(orientation)

        if sizes:
            splitter.setSizes(sizes)

        splitter.setHandleWidth(handle_width)

        if handle_style:
            splitter.setStyleSheet(f"QSplitter::handle {{ {handle_style} }}")

        self.panels[f"splitter_{len(self.panels)}"] = splitter  # Сохраняем в общий словарь
        return splitter
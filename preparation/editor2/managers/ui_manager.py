from PySide6.QtWidgets import QToolBar, QPushButton, QHBoxLayout, QWidget
from PySide6.QtCore import Signal

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

    def create_toolbar(self, name, buttons):
        """Создает панель инструментов с кнопками."""
        toolbar = QToolBar(name)
        for btn_name in buttons:
            if btn_name in self.buttons:
                toolbar.addWidget(self.buttons[btn_name])
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
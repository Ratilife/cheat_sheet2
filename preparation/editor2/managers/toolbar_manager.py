from PySide6.QtWidgets import QToolBar, QPushButton, QButtonGroup
from PySide6.QtCore import Signal


class ToolbarManager:
    """Управляет панелями инструментов и их действиями."""

    # Сигналы для внешних обработчиков
    load_requested = Signal()  # Загрузка файлов
    editor_toggled = Signal(bool)  # Открытие/закрытие редактора
    format_action = Signal(str)  # Форматирование текста (например, "bold")

    def __init__(self):
        self.toolbar = QToolBar()
        self._init_main_toolbar()
        self._init_format_toolbar()

    def _init_main_toolbar(self):
        """Кнопки: открыть, сохранить, свернуть и т.д."""
        self.load_btn = QPushButton("📂")
        self.load_btn.clicked.connect(self.load_requested.emit)

        self.edit_btn = QPushButton("✏️")
        self.edit_btn.clicked.connect(lambda: self.editor_toggled.emit(True))

    def _init_format_toolbar(self):
        """Панель форматирования текста (для редактора)."""
        self.bold_btn = QPushButton("B")
        self.bold_btn.clicked.connect(lambda: self.format_action.emit("bold"))

    def set_buttons_visible(self, visible: bool):
        """Показ/скрытие панели (например, для режима preview)."""
        self.toolbar.setVisible(visible)
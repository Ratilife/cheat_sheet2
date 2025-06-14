"""Что делает этот модуль?"""
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolBar, QPushButton, QButtonGroup
from PySide6.QtCore import Signal
from preparation.editor2.managers.ui_manager import UIManager


class ToolbarManager:
    """Управление панелями инструментов с использованием UIManager."""

    # Сигналы для внешних обработчиков
    load_requested = Signal()  # Загрузка файлов
    editor_toggled = Signal(bool)  # Открытие/закрытие редактора
    format_action = Signal(str)  # Форматирование текста (например, "bold")

    collapse_all = Signal()
    expand_all = Signal()
    collapse_panel = Signal()
    close_panel = Signal()
    new_st_file = Signal()
    new_md_file = Signal()
    new_folder = Signal()
    new_template = Signal()
    save_file = Signal()
    save_file_as = Signal()
    delete_action = Signal()
    cut_action = Signal()
    copy_action = Signal()
    paste_action = Signal()

    def __init__(self):
        self.ui = UIManager()  # Создаем экземпляр UIManager
        self._setup_buttons()
        self._setup_toolbars()


    def _setup_buttons(self):
        """Создает кнопки и привязывает сигналы."""
        # Кнопка свернуть все
        self.ui.create_button(
            name="collapse_btn",
            text="+",
            tooltip="Свернуть все"
        )
        self.ui.buttons["collapse_btn"].clicked.connect(self.collapse_all.emit)

        # Кнопка развернуть все
        self.ui.create_button(
            name="expand_btn",
            text="-",
            tooltip="Развернуть все",
            fixed_width= 20,
            fixed_height=20

        )
        self.ui.buttons["expand_btn"].clicked.connect(self.expand_all.emit)

        # Кнопка свернуть панель
        self.ui.create_button(
            name="collapse_panel_btn",
            text="—",
            tooltip="Свернуть панель",
            fixed_width= 20,
            fixed_height=20
        )
        self.ui.buttons["collapse_panel_btn"].clicked.connect(self.collapse_panel.emit)

        # Кнопка закрыть панель
        self.ui.create_button(
            name="close_panel_btn",
            text="Х",
            tooltip="Закрыть панель",
            fixed_width= 20,
            fixed_height=20
        )
        self.ui.buttons["close_panel_btn"].clicked.connect(self.close_panel.emit)

        # Кнопка открыть окно редактора
        self.ui.create_button(
            name="edit_btn",
            text="✏️",
            tooltip="Открыть редактор",
            fixed_width= 20,
            fixed_height=20
        )
        self.ui.buttons["edit_btn"].clicked.connect(
            lambda: self.editor_toggled.emit(True)
        )
        # Кнопка загрузить файл
        self.ui.create_button(
            name="load_btn",
            text="📥",
            tooltip="Загрузить файл",
            fixed_width= 20,
            fixed_height=20
        )
        self.ui.buttons["load_btn"].clicked.connect(self.load_requested.emit)

        # Кнопка Создать st-файл
        self.ui.create_button(
            name="new_st_btn",
            text="📄",
            tooltip="Создать ST-файл"
        )
        self.ui.buttons["new_st_btn"].clicked.connect(self.new_st_file.emit)

        # Кнопка Создать md-файл
        self.ui.create_button(
            name="new_md_btn",
            text="📝",
            tooltip="Создать MD-файл"
        )
        self.ui.buttons["new_md_btn"].clicked.connect(self.new_md_file.emit)

        # Кнопка Создать папку
        self.ui.create_button(
            name="new_folder_btn",
            text="📂",
            tooltip="Создать папку"
        )
        self.ui.buttons["new_folder_btn"].clicked.connect(self.new_folder.emit)

        # Кнопка Создать шаблон
        self.ui.create_button(
            name="new_template_btn",
            text="🖼️",
            tooltip="Создать шаблон"
        )
        self.ui.buttons["new_template_btn"].clicked.connect(self.new_template.emit)

        # Кнопка Сохранить
        self.ui.create_button(
            name="new_save_btn",
            text="💾",
            tooltip="Сохранить"
        )
        self.ui.buttons["new_save_btn"].clicked.connect(self.save_file.emit)

        # Кнопка Сохранить как
        self.ui.create_button(
            name="new_save_as_btn",
            text="💽",
            tooltip="Сохранить как"
        )
        self.ui.buttons["new_save_as_btn"].clicked.connect(self.save_file_as.emit)

        # Кнопка Удалть редактор
        self.ui.create_button(
            name="delete_btn",
            text=QIcon.fromTheme("edit-delete"),
            tooltip="Удалть"
        )
        self.ui.buttons["delete_btn"].clicked.connect(self.delete_action.emit)

        # Кнопка Вырезать редактор
        self.ui.create_button(
            name="cut_btn",
            text=QIcon.fromTheme("edit-cut"),
            tooltip="вырезать"
        )
        self.ui.buttons["cut_btn"].clicked.connect(self.cut_action.emit)

        # Кнопка Копировать редактор
        self.ui.create_button(
            name="new_copy_btn",
            text=QIcon.fromTheme("edit-copy"),
            tooltip="Копировать"
        )
        self.ui.buttons["new_copy_btn"].clicked.connect(self.copy_action.emit)

        # Кнопка Вставить редактор
        self.ui.create_button(
            name="new_paste_btn",
            text=QIcon.fromTheme("edit-paste"),
            tooltip="Вставить"
        )
        self.ui.buttons["paste_btn"].clicked.connect(self.paste_action.emit)

    def _setup_toolbars(self):
        """Создает панели инструментов."""
        self.above_tree_toolbar = self.ui.create_toolbar(
            name="above_tree_toolbar",
            buttons=["collapse_btn", "expand_btn", "load_btn", "edit_btn",
                     "collapse_panel_btn", "close_panel_btn"]
        )

        self.above_tree_toolbar_editor = self.ui.create_toolbar(
            name="above_tree_toolbar_editor",
            buttons=["new_st_btn", "new_md_btn", "new_folder_btn", "new_template_btn", "new_save_as_btn"]
        )

    def get_above_tree_toolbar(self):
        return self.above_tree_toolbar

    def get_above_tree_toolbar_editor(self):
        return self.above_tree_toolbar_editor





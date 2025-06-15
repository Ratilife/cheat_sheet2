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

    def __init__(self,tree_manager=None, close=None, showMinimized = None ):
        self.ui = UIManager()  # Создаем экземпляр UIManager
        self.tree_manager = tree_manager
        self.close = close
        self.showMinimized = showMinimized
        self.tree_model = None
        self._setup_buttons()
        self._setup_toolbars()
        self._connect_tree_manager()

    def _connect_tree_manager(self):
        """Подключает методы TreeManager к кнопкам."""
        if self.tree_manager:
            # Подключаем кнопки к методам TreeManager
            self.ui.buttons["collapse_btn"].clicked.connect(self.tree_manager.collapse_all)
            self.ui.buttons["expand_btn"].clicked.connect(self.tree_manager.expand_all)
    def _setup_buttons(self):
        """Создает кнопки и привязывает сигналы."""
        # Кнопка свернуть все
        self.ui.create_button(
            name="collapse_btn",
            text="+",
            tooltip="Свернуть все"
        )
        #self.ui.buttons["collapse_btn"].clicked.connect(self.collapse_all.emit)

        # Кнопка развернуть все
        self.ui.create_button(
            name="expand_btn",
            text="-",
            tooltip="Развернуть все",
            fixed_width= 20,
            fixed_height=20

        )
        #self.ui.buttons["expand_btn"].clicked.connect(self.expand_all.emit())

        # Кнопка свернуть панель
        self.ui.create_button(
            name="collapse_panel_btn",
            text="—",
            tooltip="Свернуть панель",
            fixed_width= 20,
            fixed_height=20
        )
        self.ui.buttons["collapse_panel_btn"].clicked.connect(self.showMinimized)

        # Кнопка закрыть панель
        self.ui.create_button(
            name="close_panel_btn",
            text="Х",
            tooltip="Закрыть панель",
            fixed_width= 20,
            fixed_height=20
        )
        self.ui.buttons["close_panel_btn"].clicked.connect(self.close)

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
        #self.ui.buttons["load_btn"].clicked.connect(self.tree_model.load_st_md_files)

        # Кнопка Создать st-файл
        self.ui.create_button(
            name="new_st_btn",
            text="📄",
            tooltip="Создать ST-файл"
        )
        self.ui.buttons["new_st_btn"].clicked.connect(self.new_st_file)

        # Кнопка Создать md-файл
        self.ui.create_button(
            name="new_md_btn",
            text="📝",
            tooltip="Создать MD-файл"
        )
        self.ui.buttons["new_md_btn"].clicked.connect(self.new_md_file)

        # Кнопка Создать папку
        self.ui.create_button(
            name="new_folder_btn",
            text="📂",
            tooltip="Создать папку"
        )
        self.ui.buttons["new_folder_btn"].clicked.connect(self.new_folder)

        # Кнопка Создать шаблон
        self.ui.create_button(
            name="new_template_btn",
            text="🖼️",
            tooltip="Создать шаблон"
        )
        self.ui.buttons["new_template_btn"].clicked.connect(self.new_template)

        # Кнопка Сохранить
        self.ui.create_button(
            name="save_btn",
            text="💾",
            tooltip="Сохранить"
        )
        self.ui.buttons["save_btn"].clicked.connect(self.save_file)

        # Кнопка Сохранить как
        self.ui.create_button(
            name="new_save_as_btn",
            text="💽",
            tooltip="Сохранить как"
        )
        self.ui.buttons["new_save_as_btn"].clicked.connect(self.save_file_as)

        # Кнопка Удалть редактор
        self.ui.create_button(
            name="delete_btn",
            icon=QIcon.fromTheme("edit-delete"),
            text="",
            tooltip="Удалть"
        )
        self.ui.buttons["delete_btn"].clicked.connect(self.delete_action)

        # Кнопка Вырезать редактор
        self.ui.create_button(
            name="cut_btn",
            icon= QIcon.fromTheme("edit-cut"),
            text="",
            tooltip="вырезать"
        )
        self.ui.buttons["cut_btn"].clicked.connect(self.cut_action)

        # Кнопка Копировать редактор
        self.ui.create_button(
            name="copy_btn",
            icon=QIcon.fromTheme("edit-copy"),
            text="",
            tooltip="Копировать"
        )
        self.ui.buttons["copy_btn"].clicked.connect(self.copy_action)

        # Кнопка Вставить редактор
        self.ui.create_button(
            name="paste_btn",
            icon=QIcon.fromTheme("edit-paste"),
            text="",
            tooltip="Вставить"
        )
        self.ui.buttons["paste_btn"].clicked.connect(self.paste_action)

    def _setup_toolbars(self):
        """Создает панели инструментов."""
        self._title_layout = self.ui.create_toolbar(
            name="title_layout",
            buttons=["collapse_btn", "expand_btn", "load_btn", "edit_btn",
                     "spacer",
                     "collapse_panel_btn", "close_panel_btn"]
        )

        self._above_tree_toolbar_editor = self.ui.create_toolbar(
            name="above_tree_toolbar_editor",
            buttons=["new_st_btn", "new_md_btn", "new_folder_btn", "new_template_btn", "new_save_as_btn"],
        )

        self._editor_toolbar = self.ui.create_toolbar(
            name="editor_toolbar",
            buttons=["cut_btn", "copy_btn", "delete_btn", "paste_btn", "save_btn"]
        )

    def set_tree_model(self, tree_model=None):
        """
            Устанавливает модель дерева для ToolbarManager и настраивает связанные сигналы.

            Этот метод выполняет две основные функции:
            1. Сохраняет переданную модель дерева для последующего использования
            2. Если модель существует и содержит метод load_st_md_files, автоматически
             связывает кнопку загрузки (load_btn) с этим методом

            Параметры:
              tree_model: Модель дерева, реализующая интерфейс работы с файлами.
                         Должна содержать метод load_st_md_files() для корректной работы
                         кнопки загрузки. Может быть None для сброса текущей модели.

          Примечание:
              - Метод безопасно обрабатывает случай, когда tree_model=None
              - Проверка наличия метода load_st_md_files выполняется динамически,
                что делает код более гибким к изменениям в интерфейсе модели
          """
        self.tree_model = tree_model
        if self.tree_model and hasattr(self.tree_model, 'load_st_md_files'):
            self.ui.buttons["load_btn"].clicked.connect(self.tree_model.load_st_md_files)

    def get_title_layout(self):
        return self._title_layout

    def get_above_tree_toolbar_editor(self):
        return self._above_tree_toolbar_editor

    def get_editor_toolbar(self):
        return self._editor_toolbar
import sys
import os
from PySide6.QtWidgets import (QTreeView, QWidget,
                               QVBoxLayout, QApplication, QMenu,
                               QMessageBox)
from PySide6.QtCore import Qt, Signal, QObject, QRect, QSize
from PySide6.QtGui import QAction
from preparation.editor2.ui.file_editor import FileEditorWindow
from preparation.editor2.managers.tree_model_manager import TreeModelManager
from preparation.editor2.widgets.markdown_viewer import MarkdownViewer
from preparation.editor2.managers.file_watcher import FileWatcher


# Класс для обработки сигналов панели
class SidePanelSignals(QObject):
    # Сигнал при выборе файла (передает путь к файлу)
    file_selected = Signal(str)
    # Сигнал при изминении файла(передает путь к измененному файлу)
    file_changed = Signal(str)


# Основной класс боковой панели
class SidePanel(QWidget):

    def __init__(self, parent=None):
        # - Всегда поверх других окон (WindowStaysOnTopHint)
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # 1. Создаем экземпляр класса для сигналов
        self.signals = SidePanelSignals()

        # 2.  Инициализация модели и менеджеров
        self.tree_model_manager = TreeModelManager()  # Подключаем менеджер
        self.tree_model_manager.delete_manager.removal_complete.connect(self._handle_removal_result)

        #3. # Инициализация наблюдателя
        self.file_watcher = FileWatcher()
        self.file_watcher.file_updated.connect(self._on_file_updated)
        self.file_watcher.file_deleted.connect(self._on_file_deleted)

        self.content_viewer = MarkdownViewer()

        # 4. Инициализация пользовательского интерфейса
        self._init_ui()

        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.show()

    # 1. Инициализация и базовый UI
    def _init_ui(self):

        self.ui_manager = UIManager()
        # Устанавливаем минимальную ширину панели
        self.setMinimumWidth(300)

        # Создаем основной вертикальный layout
        main_layout = QVBoxLayout(self)
        # Убираем отступы у layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем дерево для отображения файловой системы
        self.tree_view = QTreeView()
        # Показываем заголовки у дерева
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setIndentation(10)  # Увеличьте это значение
        self.tree_view.setAnimated(True)  # Анимация раскрытия
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setRootIsDecorated(True)  # Показываем декор для корневых элементов
        self.tree_view.setExpandsOnDoubleClick(True)  # Включаем разворачивание по двойному клику
        self.tree_view.setSortingEnabled(False)
        #---Тут изменить-----
        #Оформляем горизонтальную панель над деревом с кнопками
        # Кнопки для панели над деревом
        self.ui_manager.create_button()
        self.ui_manager.create_button()
        self.ui_manager.create_button()
        self.ui_manager.create_button()

        # Горизонтальная панель над деревом
        btn_panel = self.ui_manager.create_horizontal_panel(
            "tree_controls",
            ["add_file", "add_folder"]
        )
        # ---Конец Тут изменить-----
        # Добавляем панель кнопок над деревом
        main_layout.addWidget(btn_panel)
        # Добавляем само дерево файлов
        main_layout.addWidget(self.tree_view)


    # 2. Позиционирование/размеры
    # Метод настройки прикрепления к краям экрана
    def _setup_screen_edge_docking(self):
        """Настройка прикрепления к краям экрана"""
        # Позиция по умолчанию - справа
        self.dock_position = "right"  # left/right/float
        # Отступ от края экрана
        self.dock_margin = 5

        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)  # <- ОТКЛЮЧАЕМ поверх всех окон
        # Обновляем позицию
        self.update_dock_position()
        # Устанавливаем прозрачность окна
        self.setWindowOpacity(0.9)

    # Метод обновления позиции панели
    def update_dock_position(self):
        """Обновление позиции относительно края экрана"""
        # Получаем геометрию экрана
        screen = QApplication.primaryScreen().availableGeometry()
        # Если панель должна быть слева
        if self.dock_position == "left":
            self.setGeometry(QRect(
                screen.left() + self.dock_margin,  # X координата
                screen.top(),  # Y координата
                300,  # Ширина
                screen.height()  # Высота
            ))
            self.setFixedWidth(300)  # Фиксируем ширину в закрепленном режиме
            self.setFixedHeight(screen.height())  # Фиксируем высоту
            # Если панель должна быть справа
        elif self.dock_position == "right":
            self.setGeometry(QRect(
                screen.right() - 300 - self.dock_margin,  # X координата
                screen.top(),  # Y координата
                300,  # Ширина
                screen.height()  # Высота
            ))
            self.setFixedWidth(300)  # Фиксируем ширину в закрепленном режиме
            self.setFixedHeight(screen.height())  # Фиксируем высоту
            # Для режима float не устанавливаем фиксированные размеры
        elif self.dock_position == "float":
            self.setMinimumSize(200, 200)
            self.setMaximumSize(16777215, 16777215)
            self.setFixedSize(QSize())  # Снимаем фиксированные размеры

    # Метод инициализации контекстного меню
    def _init_position_menu(self):
        # Создаем меню с заголовком
        self.position_menu = QMenu("Позиция панели", self)

        # Создаем действие "Закрепить слева"
        self.pin_left_action = QAction("Закрепить слева", self, checkable=True)
        # Подключаем обработчик
        self.pin_left_action.triggered.connect(self._dock_to_left)

        # Создаем действие "Закрепить справа"
        self.pin_right_action = QAction("Закрепить справа", self, checkable=True)
        # Подключаем обработчик
        self.pin_right_action.triggered.connect(self._dock_to_right)

        # Создаем действие "Свободное перемещение"
        self.float_action = QAction("Свободное перемещение", self, checkable=True)
        # Подключаем обработчик
        self.float_action.triggered.connect(self._enable_floating)

        # Добавляем действия в меню
        self.position_menu.addActions([self.pin_left_action, self.pin_right_action, self.float_action])
        # Устанавливаем политику контекстного меню
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # Подключаем обработчик показа контекстного меню
        self.customContextMenuRequested.connect(self.show_context_menu)

    # Метод для закрепления панели слева
    def _dock_to_left(self):
        self.dock_position = "left"
        self.update_dock_position()
        self._update_menu_checks()

    # Метод для закрепления панели справа
    def _dock_to_right(self):
        self.dock_position = "right"
        self.update_dock_position()
        self._update_menu_checks()

        # Метод обновления состояния пунктов меню
    def _update_menu_checks(self):
        self.pin_left_action.setChecked(self.dock_position == "left")
        self.pin_right_action.setChecked(self.dock_position == "right")
        self.float_action.setChecked(self.dock_position == "float")

    def _handle_removal_result(self, success, message):
        """Обработчик результата удаления."""
        if success:
            self.tree_model_manager.file_manager.save_files_to_json()
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Ошибка", message)

    def _open_editor(self):
        """Открыть окно редактора файла"""
        if not hasattr(self, 'editor_window'):
            self.editor_window = FileEditorWindow(self)
            # Подключаем сигналы редактора к панели
            self.editor_window.file_created.connect(self._on_file_created)
        self.editor_window.show()

    def _on_file_created(self, file_path):
        """Обработчик сигнала о создании файла"""
        try:
            if file_path.endswith('.st'):
                self.tree_model_manager.tree_model.add_file(file_path)
            elif file_path.endswith('.md'):
                self.tree_model_manager.tree_model.add_markdown_file(file_path)
            self.tree_model_manager.file_manager.save_files_to_json()
            self.tree_view.expandAll()  # зменить код
        except Exception as e:
            print(f"Ошибка при добавлении файла в дерево: {e}")
            # Можно добавить QMessageBox для показа ошибки пользователю
            QMessageBox.warning(self, "Ошибка", f"Не удалось добавить файл в дерево: {str(e)}")

    def _on_tree_item_clicked(self, index):
        """Обработка клика по элементу дерева с корректной работой FileWatcher"""
        item = index.internalPointer()
        if not item:
            return

        # Очищаем предыдущее содержимое
        self.content_viewer.set_content("")

        # Обработка разных типов элементов
        item_type = item.item_data[1]
        item_content = item.item_data[2]

        if item_type == 'template':
            self.content_viewer.set_content(item_content)
            self.content_viewer.set_view_mode("text")

        elif item_type in ['file', 'markdown']:
            file_path = item_content
            self.current_file = file_path
            self.signals.file_selected.emit(file_path)

            # Обновляем FileWatcher
            self._update_file_watcher(file_path)

            # Загружаем содержимое файла
            self._update_file_content(file_path, item_type)

    def _update_file_watcher(self, file_path):
        """Обновляет отслеживаемые файлы в FileWatcher"""
        # Удаляем все текущие пути (если есть)
        self.file_watcher.clear_watched_files()  # Очищаем наблюдаемые файлы
        self.file_watcher.watch_file(file_path)  # Добавляем новый файл


    def _update_file_content(self, file_path, file_type):
        """Загружает и отображает содержимое файла с учетом его типа"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.content_viewer.set_content(content)
                    # Устанавливаем режим просмотра в зависимости от типа файла
                    self.content_viewer.set_view_mode("text" if file_type == 'file' else "markdown")
            else:
                self.content_viewer.set_content(f"Файл не найден: {file_path}")
        except Exception as e:
            self.content_viewer.set_content(f"Ошибка загрузки файла: {str(e)}")
    def _on_file_updated(self, path):
        """Обработчик обновления файла."""
        if path == self.current_file:
            self.signals.file_changed.emit(path)  # Уведомляем о изменении
            # Можно также обновить содержимое просмотра:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.content_viewer.set_content(content)
            except Exception as e:
                self.content_viewer.set_content(f"Ошибка загрузки файла: {str(e)}")

    def _on_file_deleted(self, path):
        """Обработчик удаления файла."""
        if path == self.current_file:
            self.content_viewer.set_content(f"Файл удалён: {path}")
            # Дополнительные действия, например, убрать файл из tree_view


if __name__ == "__main__":
    # Создаем экземпляр приложения
    app = QApplication(sys.argv)

    # Создаем экземпляр боковой панели
    panel = SidePanel()
    # Устанавливаем заголовок окна
    panel.setWindowTitle("Системная боковая панель")

    # Показываем панель
    panel.show()
    # Запускаем цикл обработки событий
    sys.exit(app.exec())
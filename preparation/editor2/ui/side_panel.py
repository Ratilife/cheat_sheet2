import sys
import os
import json
from PySide6.QtWidgets import (QSplitter, QTreeView, QWidget,
                               QVBoxLayout, QApplication, QMenu,
                               QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QFileDialog, QMessageBox)
from PySide6.QtCore import (Qt, QFileSystemWatcher, Signal, QObject, QRect, QSize,
                             QModelIndex)
from PySide6.QtGui import QAction,  QColor, QCursor, QPen, QPainter
from preparation.editor2.ui.file_editor import FileEditorWindow
from preparation.editor2.widgets.delegates import TreeItemDelegate
from preparation.editor2.utils.tree_manager import TreeManager
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


    # 1. Инициализация и базовый UI
    def _init_ui(self):
        # Устанавливаем минимальную ширину панели
        self.setMinimumWidth(300)

        # Создаем основной вертикальный layout
        main_layout = QVBoxLayout(self)
        # Убираем отступы у layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Панель заголовка
        self.title_bar = QWidget()
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(5, 2, 5, 2)

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
        """Обработка клика по элементу дерева"""
        """
              Кратко по логике метода:
              Метод вызывается при клике по элементу в дереве.
              Получает соответствующий объект и очищает содержимое просмотра.
              В зависимости от типа элемента (template, file, markdown) разным образом обрабатывает содержимое:
                  Для template — показывает текст шаблона.
                  Для file — читает файл, отображает его как текст.
                  Для markdown — читает файл, отображает его как markdown.
                  Для файлов (file и markdown) настраивает наблюдение за изменениями файла через file_watcher.
        """
        item = index.internalPointer()      # Получаем объект элемента дерева из индекса
        if not item:                        # Если элемент отсутствует, выходим из метода
            return

        # Очищаем предыдущее содержимое
        self.content_viewer.set_content("")  # используем метод MarkdownViewer

        # Обработка разных типов элементов
        if item.item_data[1] == 'template':  # Если элемент — шаблон

            self.content_viewer.set_content(item.item_data[2])  # Устанавливаем содержимое шаблона
            self.content_viewer.set_view_mode("text") # <-- Устанавливаем текстовый режим для шаблонов

        elif item.item_data[1] == 'file':  # <-- Обработка ST файлов
            file_path = item.item_data[2]  # Получаем путь к файлу
            try:
                if os.path.exists(file_path): # Проверяем, существует ли файл
                    with open(file_path, 'r', encoding='utf-8') as f: # Открываем файл для чтения
                        content = f.read()      # Читаем содержимое файла
                        self.content_viewer.set_content(content) # Отправляем содержимое на просмотр
                        self.content_viewer.set_view_mode("text")  # <-- Устанавливаем текстовый режим для ST файлов
                else:
                    self.content_viewer.set_content(f"Файл не найден: {file_path}")  # Сообщаем, что файл не найден
            except Exception as e:
                self.content_viewer.set_content(f"Ошибка загрузки файла: {str(e)}")  # Сообщаем об ошибке загрузки


        elif item.item_data[1] == 'markdown':        # Если элемент — markdown файл
            file_path = item.item_data[2]            # Получаем путь к файлу
            try:
                if os.path.exists(file_path):        # Проверяем, существует ли файл
                    with open(file_path, 'r', encoding='utf-8') as f:  # Открываем файл для чтения
                        content = f.read()  # Читаем содержимое файла
                        #self.content_view.setMarkdown(content)
                        self.content_viewer.set_content(content) # Отправляем содержимое на просмотр
                        self.content_viewer.set_view_mode("markdown")  # <-- Устанавливаем markdown режим для MD файлов
                else:
                    #self.content_view.setPlainText(f"Файл не найден: {file_path}")
                    self.content_viewer.set_content(f"Файл не найден: {file_path}")  # Сообщаем, что файл не найден
            except Exception as e:
                #self.content_view.setPlainText(f"Ошибка загрузки файла: {str(e)}")
                self.content_viewer.set_content(f"Ошибка загрузки файла: {str(e)}")  # Сообщаем об ошибке загрузки

        # Для файлов добавляем в наблюдатель
        if item.item_data[1] in ['file', 'markdown']:   # Если выбран файл или markdown, добавляем в FileWatcher
            file_path = item.item_data[2]               # Получаем путь к файлу
            self.current_file = file_path               # Сохраняем путь к текущему файлу
            self.signals.file_selected.emit(file_path)  # Отправляем сигнал о выборе файла

            # Обновляем наблюдатель файлов (удаляем старые файлы из наблюдения и добавляем текущий)
            if self.file_watcher.files():  # Если есть отслеживаемые файлы
                self.file_watcher.removePaths(self.file_watcher.files()) # Удаляем их из наблюдения
            self.file_watcher.addPath(file_path)  # Добавляем текущий файл в наблюдение

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
import sys
import os
from PySide6.QtWidgets import (QTreeView, QWidget,
                               QVBoxLayout, QApplication, QMenu,
                               QMessageBox)
from PySide6.QtCore import Qt, Signal, QObject, QRect, QSize
from PySide6.QtGui import QAction
from preparation.editor2.ui.file_editor import FileEditorWindow
from preparation.editor2.managers.tree_model_manager import TreeModelManager
#from preparation.editor2.widgets.markdown_viewer_old import MarkdownViewer
from preparation.editor2.widgets.markdown_viewer_widget import MarkdownViewer
from preparation.editor2.observers.file_watcher import FileWatcher
from preparation.editor2.managers.toolbar_manager import ToolbarManager
from preparation.editor2.managers.ui_manager import UIManager
from preparation.editor2.widgets.delegates import TreeItemDelegate
from preparation.editor2.utils.tree_manager import TreeManager
from preparation.editor2.operation.file_operations import FileOperations
from preparation.editor2.observers.my_base_observer import MyBaseObserver


# Класс для обработки сигналов панели
class SidePanelObserver(MyBaseObserver):
    def __init__(self):
        super().__init__()


# Основной класс боковой панели
class SidePanel(QWidget):

    def __init__(self, parent=None):
        # - Всегда поверх других окон (WindowStaysOnTopHint)
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # 1. Создаем экземпляр класса для сигналов
        self.observer = SidePanelObserver()

        # 2.  Инициализация модели и менеджеров
        #TODO переписать сам tree_model_manager и обращение к нему
        self.tree_model_manager = TreeModelManager()  # Подключаем менеджер
        self.tree_model_manager.delete_manager.removal_complete.connect(self._handle_removal_result)


        self.file_operations = FileOperations()

        #3. # Инициализация наблюдателя
        self.file_watcher = FileWatcher()
        self.file_watcher.file_updated.connect(self._on_file_updated)
        self.file_watcher.file_deleted.connect(self._on_file_deleted)



        #нижняя панель (отображение данных)
        self.content_viewer = MarkdownViewer()

        # 4. Инициализация пользовательского интерфейса
        self._init_ui()

        #Подключение сигнала
        self.toolbar_manager.editor_toggled.connect(self._open_editor)


        # Инициализация контекстного меню для управления позицией
        self._init_position_menu()
        # Настройка прикрепления к краям экрана
        self._setup_screen_edge_docking()

        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.show()

    # 1. Инициализация и базовый UI
    def _init_ui(self):

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

        self.ui = UIManager()
        self.tree_manager = TreeManager(self.tree_view)
        self.toolbar_manager = ToolbarManager(self.tree_manager,self.close,self.showMinimized)
        self.toolbar_manager.set_tree_model(self.tree_model_manager)

        # Устанавливаем минимальную ширину панели
        self.setMinimumWidth(300)

        # Создаем основной вертикальный layout
        main_layout = QVBoxLayout(self)
        # Убираем отступы у layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем панель заголовка с кнопками управления
        title_layout = self.toolbar_manager.get_title_layout()
        main_layout.addWidget(title_layout)  # Добавляем панель инструментов в основной layout(макет)

        # Создаем разделитель с вертикальной ориентацией
        self.splitter = self.ui.create_splitter(Qt.Vertical,
                                                sizes=[300, 100],
                                                handle_width=5,
                                                handle_style="QSplitter::handle { background: #ccc; }")



        # Устанавливаем делегат с правильной ссылкой на tree_view
        self.delegate = TreeItemDelegate(self.tree_view)
        self.tree_view.setItemDelegate(self.delegate)

        # Подключаем обработчик двойного клика
        #self.tree_view.doubleClicked.connect(self._on_tree_item_double_clicked)
        self.tree_manager.setup_double_click_handler(self)

        # Настройка стиля дерева
        self.tree_view.setStyleSheet("""
                    QTreeView {
                        background-color: white;
                        border: 1px solid #ddd;
                    }
                    QTreeView::item {
                        padding: 2px;
                        margin: 0px;
                        height: 20px;
                    }
                    /* Убираем стандартные треугольники */
                    QTreeView::branch {
                        background: transparent;
                        border: 0px;
                    }
                    QTreeView::branch:has-siblings:!adjoins-item {
                        border-image: none;
                        image: none;
                    }
                    QTreeView::branch:has-siblings:adjoins-item {
                        border-image: none;
                        image: none;
                    }
                    QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                        border-image: none;
                        image: none;
                    }
                    QTreeView::branch:has-children:!has-siblings:closed,
                    QTreeView::branch:closed:has-children:has-siblings {
                        border-image: none;
                        image: none;
                    }
                    QTreeView::branch:open:has-children:!has-siblings,
                    QTreeView::branch:open:has-children:has-siblings {
                        border-image: none;
                        image: none;
                    }
                """)

        # Добавляем само дерево файлов
        main_layout.addWidget(self.tree_view)
        #Текстовое поле (нижняя часть)
        self.splitter.addWidget(self.content_viewer)
        #Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)

        # Настраиваем контекстное меню для дерева


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

        # Метод для включения свободного перемещения

    def _enable_floating(self):
        self.dock_position = "float"
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  # <- ВКЛЮЧАЕМ поверх окон
        self.show()
        # self.update_dock_position()  # Обновляем геометрию
        # Устанавливаем начальные размеры и позицию
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(QRect(
            screen.right() - 350,  # X координата (немного левее правого края)
            screen.top() + 100,  # Y координата (немного ниже верхнего края)
            300,  # Ширина
            screen.height() - 200  # Высота (меньше высоты экрана)
        ))
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
            self.file_operations.add_file_to_tree(file_path)
            self.tree_model_manager.file_manager.save_files_to_json() #TODO присмотрться
            self.tree_view.expandAll()  # заменить код
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
            self.observer.file_selected.emit(file_path)

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
            self.observer.file_changed.emit(path)  # Уведомляем о изменении
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

    # Метод показа контекстного меню
    def show_context_menu(self, pos):
        # Показываем меню в указанной позиции
        self.position_menu.exec(self.mapToGlobal(pos))

    def _open_editor(self):
        """Открыть окно редактора файла"""
        if not hasattr(self, 'editor_window'):
            self.editor_window = FileEditorWindow()
            self.editor_window.receive_tree(self.tree_model_manager, self.toolbar_manager)
            # Подключаем сигналы редактора к панели
            self.editor_window.file_created.connect(self._on_file_created)
        self.editor_window.show()


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
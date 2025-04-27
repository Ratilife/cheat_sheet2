import sys
from PySide6.QtWidgets import (QSplitter, QTreeView, QTextEdit, QWidget, 
                              QVBoxLayout, QApplication, QFileSystemModel, QMenu,
                              QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QFileSystemWatcher, Signal, QObject, QDir, QRect
from PySide6.QtGui import QAction, QScreen

#Класс для обработки сигналов панели
class SidePanelSignals(QObject):
    #Сигнал при выборе файла (передает путь к файлу)
    file_selected = Signal(str)
    #Сигнал при изминении файла(передает путь к измененному файлу)
    file_changed = Signal(str)

# Основной класс боковой панели
class SidePanel(QWidget):
    def __init__(self, parent=None):
        # Инициализация QWidget с параметрами:
        # - Без рамки (FramelessWindowHint)
        # - Всегда поверх других окон (WindowStaysOnTopHint)
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Создаем экземпляр класса для сигналов
        self.signals = SidePanelSignals()

        # Инициализация пользовательского интерфейса
        self._init_ui()

        # Инициализация контекстного меню для управления позицией
        self._init_position_menu()

        # Настройка прикрепления к краям экрана
        self._setup_screen_edge_docking()

        # Наблюдатель за изменениями файлов
        self.file_watcher = QFileSystemWatcher()
        # Подключаем обработчик изменений файлов
        self.file_watcher.fileChanged.connect(self._on_file_changed)
        # Текущий выбранный файл (хранит путь)
        self.current_file = None # Инициализация переменной

    # Метод инициализации пользовательского интерфейса
    def _init_ui(self):
        # Устанавливаем минимальную ширину панели
        self.setMinimumWidth(300)

        # Создаем основной вертикальный layout
        main_layout = QVBoxLayout(self)
        # Убираем отступы у layout
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Создаем панель заголовка с кнопками управления
        self.title_bar = QWidget()
        # Горизонтальный layout для панели заголовка
        title_layout = QHBoxLayout(self.title_bar)
        # Устанавливаем небольшие отступы для панели заголовка
        title_layout.setContentsMargins(5, 2, 5, 2)

        # Кнопка сворачивания
        self.minimize_btn = QPushButton("—")
        # Фиксированный размер кнопки
        self.minimize_btn.setFixedSize(20, 20)
        # Подключаем действие сворачивания окна
        self.minimize_btn.clicked.connect(self.showMinimized)

        # Кнопка закрытия
        self.close_btn = QPushButton("×")
        # Фиксированный размер кнопки
        self.close_btn.setFixedSize(20, 20)
        # Подключаем действие закрытия окна
        self.close_btn.clicked.connect(self.close)

        # Растягивающийся элемент между кнопками и заголовком
        # Добавляем кнопки в layout заголовка:
        # 1. Кнопка сворачивания
        title_layout.addWidget(self.minimize_btn)
        # 2. Растягивающийся элемент (пустое пространство)
        title_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # 3. Кнопка закрытия
        title_layout.addWidget(self.close_btn)

        # Добавляем панель заголовка в основной layout
        main_layout.addWidget(self.title_bar)

        # Создаем разделитель с вертикальной ориентацией
        self.splitter = QSplitter(Qt.Vertical)

        # Создаем дерево для отображения файловой системы
        self.tree_view = QTreeView()
        # Скрываем заголовки у дерева
        self.tree_view.setHeaderHidden(True)
        # Подключаем обработчик клика по элементам дерева
        self.tree_view.clicked.connect(self._on_tree_item_clicked)

        # Создаем текстовое поле для отображения содержимого файлов
        self.content_view = QTextEdit()
        # Делаем текстовое поле только для чтения
        self.content_view.setReadOnly(True)

        # Добавляем виджеты в разделитель:
        # 1. Дерево файлов (верхняя часть)
        self.splitter.addWidget(self.tree_view)
        # 2. Текстовое поле (нижняя часть)
        self.splitter.addWidget(self.content_view)
        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)

    # Обработчик нажатия кнопки мыши (для перемещения окна)
    def mousePressEvent(self, event):
        # Если нажата левая кнопка мыши в области заголовка (верхние 30 пикселей)
        if event.button() == Qt.LeftButton and event.y() < 30:  # Проверяем клик в области заголовка
            # Запоминаем начальную позицию курсора
            self.drag_start_position = event.globalPosition().toPoint()
            # Запоминаем текущую позицию окна
            self.drag_window_position = self.pos()
            # Принимаем событие
            event.accept()

    # Обработчик перемещения мыши (для перемещения окна)
    def mouseMoveEvent(self, event):
        # Если начата операция перетаскивания
        if hasattr(self, 'drag_start_position'):
            # Вычисляем смещение курсора
            delta = event.globalPosition().toPoint() - self.drag_start_position
            # Перемещаем окно на вычисленное смещение
            self.move(self.drag_window_position + delta)
            # Принимаем событие
            event.accept()

    # Обработчик отпускания кнопки мыши (завершение перемещения)
    def mouseReleaseEvent(self, event):
        # Если была операция перетаскивания
        if hasattr(self, 'drag_start_position'):
            # Удаляем временные данные
            del self.drag_start_position
            # Принимаем событие
            event.accept()

    # Обработчик клика по элементу дерева
    def _on_tree_item_clicked(self, index):
        """Обработка клика по элементу дерева"""
        # Получаем модель данных
        model = index.model()
        # Проверяем, есть ли у модели метод filePath
        if hasattr(model, 'filePath'):
            # Получаем путь к выбранному файлу
            file_path = model.filePath(index)
            # Сохраняем текущий файл
            self.current_file = file_path
            # Отправляем сигнал о выборе файла
            self.signals.file_selected.emit(file_path)
            
            # Добавляем файл в наблюдатель
            # Если есть наблюдаемые файлы, очищаем список
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())
            # Добавляем новый файл в наблюдатель
            self.file_watcher.addPath(file_path)

    # Обработчик изменения файла
    def _on_file_changed(self, path):
        """Обработка изменения файла"""
        # Если измененный файл - текущий выбранный файл
        if path == self.current_file:
            # Отправляем сигнал об изменении файла
            self.signals.file_changed.emit(path)

    # Метод для установки модели данных в дерево
    def set_tree_model(self, model):
        """Установка модели для дерева"""
        self.tree_view.setModel(model)
        # Раскрываем все узлы дерева
        self.tree_view.expandAll()

    # Метод для установки текстового содержимого
    def set_content(self, text):
        """Установка текстового содержимого"""
        self.content_view.setPlainText(text)

    # Метод для установки Markdown содержимого
    def set_markdown_content(self, markdown_text):
        """Установка Markdown содержимого"""
        self.content_view.setMarkdown(markdown_text)

    # Метод для очистки панели
    def clear(self):
        """Очистка панели"""
        # Очищаем модель дерева
        self.tree_view.setModel(None)
        # Очищаем текстовое поле
        self.content_view.clear()
        # Если есть наблюдаемые файлы, очищаем список
        if self.file_watcher.files():
            self.file_watcher.removePaths(self.file_watcher.files())
        # Сбрасываем текущий файл
        self.current_file = None

    # Метод настройки прикрепления к краям экрана
    def _setup_screen_edge_docking(self):
        """Настройка прикрепления к краям экрана"""
        # Позиция по умолчанию - слева
        self.dock_position = "left"  # left/right/float
        # Отступ от края экрана
        self.dock_margin = 5
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
                screen.left() + self.dock_margin, # X координата
                screen.top(),                     # Y координата
                300,                              # Ширина
                screen.height()                   # Высота
            ))
        # Если панель должна быть справа
        elif self.dock_position == "right":
            self.setGeometry(QRect(
                screen.right() - 300 - self.dock_margin,    # X координата
                screen.top(),                               # Y координата
                300,                                        # Ширина
                screen.height()                             # Высота
            ))

    # Метод инициализации контекстного меню
    def _init_position_menu(self):
        self.position_menu = QMenu("Позиция панели", self)
        
        self.pin_left_action = QAction("Закрепить слева", self, checkable=True)
        self.pin_left_action.triggered.connect(self._dock_to_left)
        
        self.pin_right_action = QAction("Закрепить справа", self, checkable=True)
        self.pin_right_action.triggered.connect(self._dock_to_right)
        
        self.float_action = QAction("Свободное перемещение", self, checkable=True)
        self.float_action.triggered.connect(self._enable_floating)
        
        self.position_menu.addActions([self.pin_left_action, self.pin_right_action, self.float_action])
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def _dock_to_left(self):
        self.dock_position = "left"
        self.update_dock_position()
        self._update_menu_checks()

    def _dock_to_right(self):
        self.dock_position = "right"
        self.update_dock_position()
        self._update_menu_checks()

    def _enable_floating(self):
        self.dock_position = "float"
        self._update_menu_checks()

    def _update_menu_checks(self):
        self.pin_left_action.setChecked(self.dock_position == "left")
        self.pin_right_action.setChecked(self.dock_position == "right")
        self.float_action.setChecked(self.dock_position == "float")

    def show_context_menu(self, pos):
        self.position_menu.exec(self.mapToGlobal(pos))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    panel = SidePanel()
    panel.setWindowTitle("Системная боковая панель")
    
    model = QFileSystemModel()
    model.setRootPath(QDir.currentPath())
    panel.set_tree_model(model)
    panel.set_content("Выберите файл в дереве")
    
    panel.show()
    sys.exit(app.exec())
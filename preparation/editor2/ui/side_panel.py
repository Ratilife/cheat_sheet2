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
from preparation.editor2.models.st_file_tree_model import STFileTreeModel


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

        # Создаем экземпляр класса для сигналов
        self.signals = SidePanelSignals()

        # Инициализация модели данных
        self.tree_model = STFileTreeModel()
        self.tree_view = QTreeView()  # Создание дерева

        # 1. Инициализация делегата (минимальная настройка)

        self.delegate = TreeItemDelegate(parent=self.tree_view)  # ← Делегат привязан к tree_view
        self.tree_view.setItemDelegate(self.delegate)  # ← Установка делегата

        # 2. Установка модели (ПОСЛЕ делегата!)
        self.tree_view.setModel(self.tree_model)

        # Инициализация пользовательского интерфейса
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
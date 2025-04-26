import sys
from PySide6.QtWidgets import (QSplitter, QTreeView, QTextEdit, QWidget, 
                              QVBoxLayout, QApplication, QFileSystemModel, QMenu,
                              QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, QFileSystemWatcher, Signal, QObject, QDir, QRect
from PySide6.QtGui import QAction, QScreen

class SidePanelSignals(QObject):
    file_selected = Signal(str)
    file_changed = Signal(str)

class SidePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.signals = SidePanelSignals()
        self._init_ui()
        self._init_position_menu()
        self._setup_screen_edge_docking()
        
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.fileChanged.connect(self._on_file_changed)
        self.current_file = None

    def _init_ui(self):
        self.setMinimumWidth(300)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # NEW: Добавляем панель с кнопками управления
        self.title_bar = QWidget()
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(5, 2, 5, 2)

        # NEW: Кнопка сворачивания
        self.minimize_btn = QPushButton("—")
        self.minimize_btn.setFixedSize(20, 20)
        self.minimize_btn.clicked.connect(self.showMinimized)

        # NEW: Кнопка закрытия
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.close)

        # NEW: Добавляем растягивающийся элемент между кнопками и заголовком
        title_layout.addWidget(self.minimize_btn)
        title_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        title_layout.addWidget(self.close_btn)

        self.splitter = QSplitter(Qt.Vertical)
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.clicked.connect(self._on_tree_item_clicked)
        
        self.content_view = QTextEdit()
        self.content_view.setReadOnly(True)
        
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.content_view)
        self.layout.addWidget(self.splitter)

        # NEW: Добавляем обработку перемещения окна за заголовок
        def mousePressEvent(self, event):
            if event.button() == Qt.LeftButton and event.y() < 30:  # Проверяем клик в области заголовка
                self.drag_start_position = event.globalPosition().toPoint()
                self.drag_window_position = self.pos()
                event.accept()

        def mouseMoveEvent(self, event):
            if hasattr(self, 'drag_start_position'):
                delta = event.globalPosition().toPoint() - self.drag_start_position
                self.move(self.drag_window_position + delta)
                event.accept()

        def mouseReleaseEvent(self, event):
            if hasattr(self, 'drag_start_position'):
                del self.drag_start_position
                event.accept()

    def _on_tree_item_clicked(self, index):
        """Обработка клика по элементу дерева"""
        model = index.model()
        if hasattr(model, 'filePath'):
            file_path = model.filePath(index)
            self.current_file = file_path
            self.signals.file_selected.emit(file_path)
            
            # Добавляем файл в наблюдатель
            if self.file_watcher.files():
                self.file_watcher.removePaths(self.file_watcher.files())
            self.file_watcher.addPath(file_path)

    def _on_file_changed(self, path):
        """Обработка изменения файла"""
        if path == self.current_file:
            self.signals.file_changed.emit(path)

    def set_tree_model(self, model):
        """Установка модели для дерева"""
        self.tree_view.setModel(model)
        self.tree_view.expandAll()

    def set_content(self, text):
        """Установка текстового содержимого"""
        self.content_view.setPlainText(text)

    def set_markdown_content(self, markdown_text):
        """Установка Markdown содержимого"""
        self.content_view.setMarkdown(markdown_text)

    def clear(self):
        """Очистка панели"""
        self.tree_view.setModel(None)
        self.content_view.clear()
        if self.file_watcher.files():
            self.file_watcher.removePaths(self.file_watcher.files())
        self.current_file = None

    def _setup_screen_edge_docking(self):
        """Настройка прикрепления к краям экрана"""
        self.dock_position = "left"  # left/right/float
        self.dock_margin = 5
        self.update_dock_position()
        self.setWindowOpacity(0.9)
        
    def update_dock_position(self):
        """Обновление позиции относительно края экрана"""
        screen = QApplication.primaryScreen().availableGeometry()
        if self.dock_position == "left":
            self.setGeometry(QRect(
                screen.left() + self.dock_margin,
                screen.top(),
                300,
                screen.height()
            ))
        elif self.dock_position == "right":
            self.setGeometry(QRect(
                screen.right() - 300 - self.dock_margin,
                screen.top(),
                300,
                screen.height()
            ))

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
        self.position_menu.exec_(self.mapToGlobal(pos))

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
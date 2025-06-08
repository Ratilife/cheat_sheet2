# managers/file_watcher.py
import os
from PySide6.QtCore import QFileSystemWatcher, Signal, QObject

class FileWatcher(QObject):
    """Отслеживает изменения файлов и уведомляет подписчиков."""

    file_updated = Signal(str)  # Файл изменён (путь)
    file_deleted = Signal(str)  # Файл удалён (путь)

    def __init__(self):
        super().__init__()
        self.watcher = QFileSystemWatcher()
        self.watcher.fileChanged.connect(self._handle_file_change)

    def add_path(self, path: str) -> bool:
        """Добавляет путь в наблюдатель."""
        if os.path.exists(path) and path not in self.watcher.files():
            return self.watcher.addPath(path)
        return False

    def remove_path(self, path: str) -> None:
        """Удаляет путь из наблюдателя."""
        if path in self.watcher.files():
            self.watcher.removePath(path)

    def _handle_file_change(self, path: str) -> None:
        """Обрабатывает изменение файла."""
        if os.path.exists(path):
            self.file_updated.emit(path)
        else:
            self.file_deleted.emit(path)
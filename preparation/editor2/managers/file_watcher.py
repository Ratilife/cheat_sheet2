# managers/file_watcher.py
import os
from PySide6.QtCore import QFileSystemWatcher, Signal, QObject

class FileWatcher(QObject):
    """Отслеживает изменения файлов и уведомляет подписчиков."""

    file_updated = Signal(str)  # Файл изменён (путь)
    file_deleted = Signal(str)  # Файл удалён (путь)

    def __init__(self):
        # Вызываем конструктор базового класса QObject, чтобы корректно инициализировать объект с поддержкой сигналов/слотов Qt
        super().__init__()
        # Создаём экземпляр QFileSystemWatcher, который будет следить за изменениями файлов и директорий в файловой системе
        self.watcher = QFileSystemWatcher()
        # Подключаем собственный метод _handle_file_change к сигналу fileChanged:
        # это значит, что когда отслеживаемый файл изменится, будет автоматически вызван _handle_file_change с путём к файлу
        self.watcher.fileChanged.connect(self._handle_file_change)

    def add_path(self, path: str) -> bool:
        """Добавляет путь в наблюдатель."""
        # Проверяет, существует ли указанный путь в файловой системе
        if os.path.exists(path) and path not in self.watcher.files():
            # Если путь существует и ещё не отслеживается, добавляет его в наблюдатель и возвращает результат
            return self.watcher.addPath(path)
        # Если путь не существует или уже отслеживается, возвращает False
        return False

    def remove_path(self, path: str) -> None:
        """Удаляет путь из наблюдателя."""
        # Проверяет, находится ли указанный путь среди отслеживаемых наблюдателем файлов/путей
        if path in self.watcher.files():
            # Если путь отслеживается, удаляет его из наблюдателя с помощью removePath
            self.watcher.removePath(path)

    def _handle_file_change(self, path: str) -> None:
        """Обрабатывает изменение файла."""
        # Проверяет, существует ли указанный путь (файл или директория) в файловой системе
        if os.path.exists(path):
            # Если путь существует, генерирует (вызывает) сигнал/событие о том, что файл был обновлён
            self.file_updated.emit(path)
        else:
            # Если путь не существует (файл был удалён), генерирует (вызывает) сигнал/событие о том, что файл был удалён
            self.file_deleted.emit(path)

    def get_watched_files(self) -> list:
        """Возвращает список отслеживаемых файлов"""
        return self.watcher.files()

    def clear_watched_files(self) -> None:
        """Очищает список отслеживаемых файлов"""
        if self.watcher.files():
            self.watcher.removePaths(self.watcher.files())

    def watch_file(self, path: str) -> bool:
        """Добавляет файл для отслеживания"""
        return self.add_path(path)  # Используем уже существующий метод
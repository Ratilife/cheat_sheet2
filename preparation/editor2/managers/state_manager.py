#TODO NOTE - этот модуль под вопросом нужен ли он класс FileStateManager похож на FileWatcher
from PySide6.QtCore import Signal


class FileStateManager:
    def __init__(self):
        self.current_file_path = None    #  текущий открытый файл
        self.file_created = Signal(str)  # Путь к созданному файлу
        # Сигналы для обновления дерева файлов в родительском окне
        self.file_saved = Signal(str)  # Путь к сохраненному файлу
        self.file_deleted = Signal(str)  # Путь к удаленному файлу


    def set_current_file(self, path: str) -> None:
        """Обновляет текущий файл и отправляет сигнал"""
        self.current_file_path = path
        self.file_created.emit(path)
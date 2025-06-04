from PySide6.QtCore import QModelIndex, Qt
from preparation.editor2.models.st_file_tree_model import STFileTreeModel
from preparation.editor2.parsers.st_file_parser import STFileParserWrapper
from preparation.editor2.parsers.md_file_parser import MarkdownListener
from preparation.editor2.utils.delete_manager import DeleteManager


class TreeModelManager:
    """
    Фасад для работы с моделью дерева файлов. Инкапсулирует:
    - Добавление/удаление элементов
    - Парсинг файлов
    - Взаимодействие с DeleteManager
    """

    def __init__(self):
        self.tree_model = STFileTreeModel()
        self.st_parser = STFileParserWrapper()
        self.md_parser = MarkdownListener()
        self.delete_manager = DeleteManager(self.tree_model, self.st_parser)

    # --- Методы для работы с данными ---
    def add_file(self, file_path: str) -> bool:
        """
        Добавляет файл в модель. Автоматически определяет тип (.st или .md).
        Возвращает True при успехе.
        """
        try:
            if file_path.endswith('.st'):
                result = self.st_parser.parse_st_file(file_path)
                self.tree_model.add_file(file_path)
            elif file_path.endswith('.md'):
                result = self.md_parser.parse_markdown_file(file_path)
                self.tree_model.add_markdown_file(file_path)
            return True
        except Exception as e:
            print(f"Ошибка добавления файла {file_path}: {str(e)}")
            return False

    def remove_item(self, index: QModelIndex, delete_from_disk: bool = False) -> tuple[bool, str]:
        """
        Удаляет элемент через DeleteManager.
        Возвращает (success, message).
        """
        return self.delete_manager.execute_removal(index, delete_from_disk)

    # --- Методы для доступа к данным ---
    def get_item_type(self, index: QModelIndex) -> str:
        """Возвращает тип элемента ('file', 'folder', 'markdown', etc.)."""
        if not index.isValid():
            return ""
        return self.tree_model.get_item_type(index)

    def get_item_path(self, index: QModelIndex) -> str | None:
        """Возвращает путь к файлу (для 'file' и 'markdown'), иначе None."""
        if self.get_item_type(index) not in ('file', 'markdown'):
            return None
        return self.tree_model.get_item_path(index)

    def get_item_level(self, index: QModelIndex) -> int:
        """Возвращает уровень вложенности элемента (0 для корня)."""
        return self.tree_model.get_item_level(index)


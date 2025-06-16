# file_operations.py
from preparation.editor2.managers.file_manager import FileManager
from preparation.editor2.managers.tree_model_manager import TreeModelManager
class FileOperations:
    def __init__(self, file_manager: FileManager, tree_model_manager: TreeModelManager):
        self.file_manager = file_manager
        self.tree_manager = tree_model_manager

    def add_file_to_tree(self, file_path: str) -> bool:
        """Полный процесс добавления файла"""
        try:
            item_type, parsed_data = self.file_manager.parse_and_get_type(file_path) #TODO ?
            return self.tree_manager.add_item(item_type, file_path)
        except Exception as e:
            print(f"Ошибка добавления файла: {str(e)}")
            return False
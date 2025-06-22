# file_operations.py
import os
from preparation.editor2.managers.file_manager import FileManager
from preparation.editor2.managers.tree_model_manager import TreeModelManager
from preparation.editor2.managers.state_manager import FileStateManager

class FileOperations:
    def __init__(self, file_manager = None, tree_model_manager=None, state_manager = None):
        self.file_manager = file_manager #TODO - FileManager Будет обьявлен сдесь
        self.tree_manager = tree_model_manager
        self.state_manager = state_manager  #TODO - Будет заменен на наблюдателя

    def add_file_to_tree(self, file_path: str) -> bool:
        """Полный процесс добавления файла"""
        try:
            item_type, parsed_data = self.file_manager.parse_and_get_type(file_path) #TODO ?
            return self.tree_manager.add_item(item_type, file_path)
        except Exception as e:
            print(f"Ошибка добавления файла: {str(e)}")
            return False

    def create_and_add_st_file(self) -> tuple[bool, str]:
        """Полный цикл создания ST-файла"""
        path = self.file_manager.get_save_path("Создать ST файл", "ST Files (*.st)")
        if not path:
            return False, "Отменено пользователем"

        try:
            if self.file_manager.create_st_file(path):
                #TODO - tree_manager.add_item("file", path) какой тп элемента создает, нужно передать
                self.tree_manager.add_item("file", path)
                # Обновление состояния
                self.state_manager.set_current_file(path)  #TODO - Будет заменен на наблюдателя
                return True, f"Файл {os.path.basename(path)} создан"
        except Exception as e:
            return False, str(e)

    def create_and_add_md_file(self) -> tuple[bool, str]:
        """Полный цикл создания MD-файлов"""
        #TODO 🚧 В разработке: 19.06.2025 (нужно описать метод)
        path = self.file_manager.get_save_path("Создать MD файл", "Markdown Files (*.md)")
        if not path:
            return False, "Отменено пользователем"
        try:
            if self.file_manager.create_md_file(path):
                return True, f"Файл {os.path.basename(path)} создан"
        except Exception as e:
            return False, str(e)
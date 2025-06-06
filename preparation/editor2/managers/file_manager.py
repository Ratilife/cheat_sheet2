import json
import os
class FileManager:

    def __init__(self):
        self.tree_model = None
    def save_files_to_json(self):
        """Сохраняет список загруженных файлов в JSON"""
        save_path = self._get_save_path()
        files = []

        # Собираем пути всех загруженных файлов (как st, так и md)
        for i in range(len(self.tree_model.root_item.child_items)):
            item = self.tree_model.root_item.child_items[i]
            if item.item_data[1] in ["file", "markdown"]:  # Изменено условие
                files.append({
                    "path": item.item_data[2],
                    "type": item.item_data[1]  # Сохраняем тип файла
                })

        # Сохраняем в JSON
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(files, f, ensure_ascii=False, indent=4)

    def load_saved_files(self):
        """Загружает сохраненные файлы из JSON"""
        save_path = self._get_save_path()
        if not os.path.exists(save_path):
            return

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                files = json.load(f)
                for file_info in files:
                    file_path = file_info["path"]
                    file_type = file_info.get("type", "file")

                    if os.path.exists(file_path):
                        if file_type == "file":
                            self.tree_model.add_file(file_path)
                        elif file_type == "markdown":
                            self.tree_model.add_markdown_file(file_path)  # Используем новый метод

            self.tree_view.expandAll()
        except Exception as e:
            print(f"Ошибка при загрузке сохраненных файлов: {e}")

    def remove_file_from_json(self, file_path):
        """Удаляет файл из сохраненного списка"""
        save_path = self._get_save_path()
        if not os.path.exists(save_path):
            return

        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                files = json.load(f)

            # Удаляем файл из списка (теперь ищем по path в словаре)
            files = [f for f in files if f["path"] != file_path]

            # Сохраняем обновленный список
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(files, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при удалении файла из сохраненных: {e}")


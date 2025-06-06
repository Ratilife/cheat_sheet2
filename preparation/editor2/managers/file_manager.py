import json
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


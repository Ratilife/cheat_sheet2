class DeleteManager:
    def __init__(self, tree_model, parser):
        """Инициализация менеджера удаления.

        Args:
            tree_model (STFileTreeModel): Модель дерева для операций удаления
            parser (STFileParserWrapper): Парсер для работы с ST-файлами
        """
        self.tree_model = tree_model    # Сохраняем модель дерева для доступа к данным
        self.parser = parser            # Сохраняем парсер для работы с содержимым ST-файлов
        self.current_item = None  # Будет хранить текущий обрабатываемый элемент

    def prepare_removal(self, index):
        """Подготовка элемента к удалению: анализ и сохранение данных.
        
        Args:
            index (QModelIndex): Индекс элемента в модели дерева
            
        Returns:
            list: Данные элемента в формате [name, type, path, ...]
        """
        item = index.internalPointer()  # Получаем объект элемента по индексу
        self.current_item = item        # Сохраняем для возможного последующего использования
        return item.item_data           # Возвращаем основные данные элемента

    def execute_removal(self, index, delete_from_disk=False):
        """Основной метод выполнения удаления.

        Args:
            index (QModelIndex): Индекс удаляемого элемента
            delete_from_disk (bool): Флаг удаления файла с диска (для элементов типа file/markdown)

        Returns:
            bool: Результат операции (True - успешно, False - ошибка)
        """
        item_data = self.prepare_removal(index)     # Получаем данные элемента

        # Выбираем стратегию удаления в зависимости от типа элемента
        if item_data[1] in ['template', 'folder']:
            # Для шаблонов и папок используем специальную логику ST-файлов
            return self._remove_st_item(item_data)
        else:
            # Для файлов и markdown используем метод модели дерева
            return self.tree_model.remove_item(index, delete_from_disk)

    def _remove_st_item(self, item_data):
        """Приватный метод для удаления элементов ST-файлов.

        Args:
            item_data (list): Данные элемента в формате [name, type, path, ...]

        Returns:
            bool: Всегда возвращает True (требуется доработка для обработки ошибок)
        """
        if item_data[1] == 'template':
            # Удаление шаблона: передаем путь к файлу и имя шаблона
            self.parser.remove_template(
                item_data[2],  # file_path - путь к ST-файлу
                item_data[0]  # template_name - имя шаблона
            )
        elif item_data[1] == 'folder':
            # Удаление папки: передаем путь к файлу и имя папки
            self.parser.remove_folder(
                item_data[2], # file_path - путь к ST-файлу
                item_data[0]  # folder_path - имя/путь папки
            )
        return True
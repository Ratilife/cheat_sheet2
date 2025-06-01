class STFileTreeItem:
    def __init__(self, data, parent=None):
        self.item_data = data  # [Имя, Тип, Контент]
        self.parent_item = parent  # Родительская ветка
        self.child_items = []  # Дочерние элементы
        # Cвойство для доступа к типу
        self.type = data[1] if len(data) > 1 else ""
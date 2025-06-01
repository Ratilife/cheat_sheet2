# tree_manager.py
class TreeManager:
    def __init__(self, tree_view):
        self.tree_view = tree_view

    def expand_all(self):
        self.tree_view.expandAll()

    def collapse_all(self):
        self.tree_view.collapseAll()

    def expand_recursive(self, index):
        if not index.isValid():
            return
        self.tree_view.expand(index)
        model = index.model()
        for i in range(model.rowCount(index)):
            child_index = model.index(i, 0, index)
            if model.is_folder(child_index):
                self.expand_recursive(child_index)

    def collapse_recursive(self, index):
        self.tree_view.collapse(index)
        model = index.model()
        for i in range(model.rowCount(index)):
            child_index = model.index(i, 0, index)
            if model.is_folder(child_index):
                self.collapse_recursive(child_index)
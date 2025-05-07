from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget


class TreeExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Пример дерева (PySide6)")

        # Создаём QTreeWidget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Структура")

        # Добавляем корневой элемент (тип file)
        file_item = QTreeWidgetItem(["[file] Новый1"])
        self.tree.addTopLevelItem(file_item)

        # Добавляем папку (тип folder)
        folder1 = QTreeWidgetItem(["[folder] Папка"])
        file_item.addChild(folder1)

        # Добавляем вложенные шаблоны (тип template)
        template1 = QTreeWidgetItem(["[template] Текст1"])
        template2 = QTreeWidgetItem(["[template] Текст2"])
        folder1.addChildren([template1, template2])

        # Вложенная папка
        sub_folder = QTreeWidgetItem(["[folder] Вложенная папка"])
        folder1.addChild(sub_folder)

        # Шаблоны во вложенной папке
        template3 = QTreeWidgetItem(["[template] Вложенный шаблон"])
        sub_folder.addChild(template3)

        # Отображаем
        layout = QVBoxLayout()
        layout.addWidget(self.tree)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = TreeExample()
    window.resize(400, 300)
    window.show()
    sys.exit(app.exec())

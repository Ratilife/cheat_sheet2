from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QRadioButton


class RemovalDialog(QDialog):
    """Диалоговое окно подтверждения удаления с выбором вариантов удаления.

    Позволяет пользователю выбрать:
    - Для файлов: удаление только из дерева или полностью с диска
    - Для других элементов: простое подтверждение удаления
    """

    def __init__(self, parent, index):
        """Инициализация диалога.

        Args:
            parent: Родительское окно
            index: QModelIndex элемента, который нужно удалить
        """
        super().__init__(parent)                         # Инициализация базового класса QDialog
        self.setWindowTitle("Подтверждение удаления")    # Заголовок окна

        # Получаем данные элемента
        item = index.internalPointer()
        self.item_type = item.item_data[1]               # Тип элемента (file, markdown, folder и т.д.)

        # Основной layout диалога
        layout = QVBoxLayout(self)
        # Добавляем вопрос с именем элемента
        layout.addWidget(QLabel(f"Удалить {item.item_data[0]}?"))

        # Для файлов и markdown добавляем варианты удаления
        if self.item_type in ['file', 'markdown']:
            # Вариант 1: Удалить только из дерева
            self.radio_tree = QRadioButton("Удалить только из дерева")
            # Вариант 2: Удалить полностью (с диска)
            self.radio_disk = QRadioButton("Удалить полностью (с диска)")
            # Устанавливаем первый вариант по умолчанию
            self.radio_disk.setChecked(True)

            # Добавляем радиокнопки в layout
            layout.addWidget(self.radio_tree)
            layout.addWidget(self.radio_disk)

        # Кнопки OK/Cancel
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)  # Добавляем обе кнопки
        buttons.accepted.connect(self.accept)                                      # OK - принимаем диалог
        buttons.rejected.connect(self.reject)                                      # Cancel - отвергаем

        # Добавляем кнопки в layout
        layout.addWidget(buttons)

    def delete_from_disk(self):
        """Определяет, нужно ли удалять файл с диска.

        Returns:
            bool: True - удалить с диска, False - только из дерева
        """
        return (self.item_type in ['file', 'markdown'] and      # Проверяем тип элемента
                hasattr(self, 'radio_disk') and                 # Проверяем наличие радиокнопки
                self.radio_disk.isChecked())                    # Проверяем выбор пользователя



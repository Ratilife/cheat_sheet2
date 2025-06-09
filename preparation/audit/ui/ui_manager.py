import sys
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLineEdit,
    QFileDialog,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox
)
from PySide6.QtCore import QCoreApplication

class FileAnalysisApp(QWidget):
    """
    Главный класс приложения, который создает и настраивает виджеты окна.
    """
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Инициализация пользовательского интерфейса.
        """
        # Устанавливаем заголовок окна
        self.setWindowTitle("Анализ файла")
        self.setFixedSize(400, 150) # Устанавливаем фиксированный размер окна

        # --- Создание виджетов ---

        # Строка для отображения пути к файлу.
        # Устанавливаем его только для чтения, так как путь выбирается через диалог.
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        self.path_edit.setPlaceholderText("Путь к файлу...")

        # Кнопка для вызова диалога выбора файла
        self.browse_button = QPushButton("...")
        self.browse_button.setFixedWidth(40) # Фиксированная ширина для кнопки "..."

        # Кнопка "OK"
        self.ok_button = QPushButton("ОК")

        # Кнопка "Отмена"
        self.cancel_button = QPushButton("Отмена")

        # --- Создание компоновок (Layouts) ---

        # Горизонтальная компоновка для строки пути и кнопки "..."
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.path_edit)
        top_layout.addWidget(self.browse_button)

        # Горизонтальная компоновка для кнопок "ОК" и "Отмена"
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1) # Добавляем растягивающееся пространство слева
        bottom_layout.addWidget(self.ok_button)
        bottom_layout.addWidget(self.cancel_button)

        # Главная вертикальная компоновка
        main_layout = QVBoxLayout(self)
        main_layout.addLayout(top_layout)
        main_layout.addStretch(1) # Добавляем растягивающееся пространство между элементами
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

        # --- Привязка сигналов к слотам (обработчики событий) ---
        self.browse_button.clicked.connect(self.open_file_dialog)
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button.clicked.connect(QCoreApplication.instance().quit)


    def open_file_dialog(self):
        """
        Открывает диалоговое окно для выбора файла и устанавливает
        выбранный путь в виджет QLineEdit.
        """
        # Открываем диалог. Первый аргумент - родитель, второй - заголовок.
        # Возвращает кортеж (путь_к_файлу, фильтр)
        file_name, _ = QFileDialog.getOpenFileName(self, "Выбрать файл")
        if file_name:
            self.path_edit.setText(file_name)

    def on_ok_clicked(self):
        """
        Обработчик нажатия на кнопку "ОК".
        Проверяет, был ли выбран файл, и выводит сообщение.
        """
        file_path = self.path_edit.text()
        if file_path:
            # Здесь  добавить логику для анализа файла
            QMessageBox.information(self, "Успешно", f"Выбран файл для анализа:\n{file_path}")
            print(f"Файл для анализа: {file_path}")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите файл перед тем, как нажать ОК.")


def main():
    """
    Главная функция для запуска приложения.
    """
    app = QApplication(sys.argv)
    window = FileAnalysisApp()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

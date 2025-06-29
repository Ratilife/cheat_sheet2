import json
import os
from PySide6.QtWidgets import (QFileDialog, QMessageBox)
from preparation.editor2.parsers.st_file_parser import STFileParserWrapper
from preparation.editor2.parsers.md_file_parser import MarkdownListener
class FileManager:

    def __init__(self):
        self.tree_model = None
        self.st_parser = STFileParserWrapper()
        self.md_parser = MarkdownListener()



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
                            self.tree_model.add_st_file(file_path)
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

    def _get_save_path(self):
        """Возвращает путь к файлу сохранения"""
        return os.path.join(os.path.dirname(__file__), "saved_files.json")

    def load_st_md_files(self):
        """Загрузка ST-файлов, MD-файлов через диалог"""
        files, _ = QFileDialog.getOpenFileNames(None,
              "Открыть файлы", "", "ST Files (*.st);;Markdown Files (*.md)"
        )
        return files

    def _save_file_as(self):
        """Сохранение файла под новым именем"""
        if not self.current_file_path:
            default_path = ""
            default_ext = "st"
        else:
            default_path = self.current_file_path
            default_ext = "md" if self.current_file_path.endswith('.md') else "st"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл как",
            default_path,
            f"{default_ext.upper()} Files (*.{default_ext})"
        )

        if file_path:
            # Добавляем расширение, если его нет
            if not file_path.endswith(f'.{default_ext}'):
                file_path += f'.{default_ext}'

            self.current_file_path = file_path
            self._save_file()  # Сохраняем файл

    def open_file(self):
        """Открытие существующего файла через диалог"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть файл",
            "",
            "ST Files (*.st);;Markdown Files (*.md)"
        )

        if file_path:
            self._load_file_content(file_path)

    def _load_file_content(self, file_path):
        """Загрузка содержимого файла в соответствующий редактор"""
        try:
            # Сначала сбрасываем состояние редакторов
            self._reset_editors()
            # Вызов метода _reset_editors() для очистки всех редакторов и приведения их в исходное состояние
            # Это гарантирует, что перед загрузкой нового файла не останется содержимого от предыдущего

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Открытие файла по переданному пути в режиме чтения с кодировкой UTF-8
            # Чтение всего содержимого файла в переменную content

            self.current_file_path = file_path
            # Сохранение пути к текущему файлу в атрибуте класса для последующего использования

            if file_path.endswith('.st'):
                # Проверка расширения файла - если это .st файл
                # ST файл - используем text_editor
                self.current_structure = self._parse_st_file(content)
                # Парсинг содержимого ST файла в структуру данных и сохранение в current_structure
                self.text_editor.setPlainText(content)
                # Установка содержимого файла в текстовый редактор (QTextEdit)
                #self._update_st_display() почему убрали?

                # Настройка интерфейса для ST файлов
                self.btn_new_folder.setEnabled(True)
                self.btn_new_template.setEnabled(True)
                # Активация кнопок для работы с папками и шаблонами (актуально только для ST файлов)
                self.text_mode_btn.setEnabled(True)
                self.markdown_mode_btn.setEnabled(True)
                # Активация переключателей режимов просмотра (текст/Markdown)

                # Показываем нужные редакторы
                self.text_editor.show()              # <-- Гарантированно показываем text_editor
                # Отображение текстового редактора
                self.md_viewer.hide()
                # Скрытие просмотрщика Markdown
                #self.text_mode_btn.setChecked(True)  #  сброс режима просмотра
            else:
                # Если файл не .st (предположительно .md)
                # MD файл - используем md_viewer
                self.md_viewer.set_content(content)
                # Установка содержимого файла в просмотрщик Markdown

                # Настройка интерфейса для MD файлов
                self.btn_new_folder.setEnabled(False)
                self.btn_new_template.setEnabled(False)
                # Деактивация кнопок для работы с папками и шаблонами (неактуально для MD файлов)
                self.text_mode_btn.setEnabled(False)
                self.markdown_mode_btn.setEnabled(False)
                # Деактивация переключателей режимов просмотра (для MD файлов всегда только один режим)
                #self.text_mode_btn.setChecked(True)  #  сброс режима просмотра

                self.text_editor.hide()  # Скрытие текстового редактора
                self.md_viewer.show()    # Отображение просмотрщика Markdown

        except Exception as e:
            # Обработка возможных исключений при работе с файлом
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")
            # Показ сообщения об ошибке с деталями исключения
            self._reset_editors()
            # Сброс редакторов в случае ошибки

    def _save_file(self):
        """Сохранение текущего файла."""
        if not self.current_file_path:
            self._save_file_as()
            return

        try:
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                if self.current_file_path.endswith('.md'):
                    f.write(self.md_viewer.get_content())  # Получаем содержимое из MD просмотрщика
                else:
                    f.write(self.text_editor.toPlainText())

            QMessageBox.information(self, "Сохранено", "Файл успешно сохранен")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")


    def _save_st_file(self):
        """
        Специальное сохранение для ST файлов.
        Генерирует содержимое из текущей структуры и сохраняет в файл.
        """
        # Основное назначение:
        # 1. Преобразование внутренней структуры данных в валидный ST-формат
        # 2. Сохранение сгенерированного содержимого в файл
        # 3. Обработка возможных ошибок ввода-вывода

        # Проверка предварительных условий
        if not self.current_file_path or not self.current_structure:
            return
            # Выход если:
            # - не указан путь к текущему файлу (current_file_path is None)
            # - отсутствует текущая структура данных (current_structure is None)

        try:
            # Генерация содержимого файла из структуры данных
            content = self._generate_st_content(self.current_structure)
            # Вызов вспомогательного метода для преобразования:
            # current_structure (dict) → валидный ST-формат (str)

            # Запись сгенерированного содержимого в файл
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                # Открытие файла в режиме перезаписи ('w') с кодировкой UTF-8
                # Контекстный менеджер гарантирует корректное закрытие файла
                f.write(content)
                # Запись сгенерированного содержимого

        except Exception as e:
            raise Exception(f"Ошибка сохранения ST файла: {str(e)}")
        # Преобразование исходного исключения с добавлением контекста
        # Позволяет точнее идентифицировать источник ошибки

    def parse_and_get_type(self, file_path: str) -> tuple[str, dict]:
        """Определяет тип файла и парсит его содержимое"""
        if file_path.endswith('.st'):
            return "file", self.st_parser.parse_st_file(file_path)
        elif file_path.endswith('.md'):
            return "markdown", self.md_parser.parse_markdown_file(file_path)
        raise ValueError("Unsupported file type")

    # ---- Методы соответствуют функционалу модуля------
    @staticmethod
    def get_save_path(title: str, filter: str) -> str | None:
        """Открывает диалог сохранения файла"""
        # ✅ Реализовано: 19.06.2025
        # filter = "Создать ST файл", "", "ST Files (*.st)"
        path, _ = QFileDialog.getSaveFileName(None, title, "", filter)
        return path

    @staticmethod
    def create_st_file(path: str) -> bool:
        """Создает новый ST-файл с базовой структурой"""
        # ✅ Реализовано: 19.06.2025
        try:
            with open(path, 'w', encoding='utf-8') as f:
                name = os.path.basename(path).replace('.st', '')
                f.write(f"""{{1, {{"{name}", 1, 0, "", ""}}, []}}""")
            return True
        except Exception as e:
            raise Exception(f"Ошибка создания ST-файла: {str(e)}")

    @staticmethod
    def create_md_file(path: str) -> bool:
        """Создает новый MD-файл с базовым заголовком"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(f"# {os.path.basename(path).replace('.md', '')}\n\n")
            return True
        except Exception as e:
            raise Exception(f"Ошибка создания MD-файла: {str(e)}")

    def save_files_to_json(self):
        """Сохраняет список загруженных файлов в JSON"""
        # ✅ Реализовано: 29.06.2025
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
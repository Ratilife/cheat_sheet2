# file_editor.py
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QTextEdit, QTreeView, QFileDialog,
                               QMessageBox, QSplitter, QStyle, QInputDialog, QApplication, QButtonGroup, QRadioButton)
from PySide6.QtCore import Qt, QModelIndex, Signal
from PySide6.QtGui import QAction, QIcon
from delegates import TreeItemDelegate


class MarkdownEditor(QWidget):
    """Класс для редактирования MD файлов с поддержкой Markdown"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._init_ui()

    def _init_ui(self):
        """Инициализация интерфейса редактора MD"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Кнопки форматирования
        self.format_panel = QWidget()
        format_layout = QHBoxLayout(self.format_panel)
        format_layout.setSpacing(3)

        # Кнопки форматирования Markdown
        self.btn_bold = QPushButton("B")
        self.btn_bold.setToolTip("Жирный текст")
        self.btn_bold.clicked.connect(lambda: self._wrap_selection("**"))

        self.btn_italic = QPushButton("I")
        self.btn_italic.setToolTip("Курсив")
        self.btn_italic.clicked.connect(lambda: self._wrap_selection("*"))

        self.btn_header = QPushButton("H")
        self.btn_header.setToolTip("Заголовок")
        self.btn_header.clicked.connect(lambda: self._add_header())

        format_layout.addWidget(self.btn_bold)
        format_layout.addWidget(self.btn_italic)
        format_layout.addWidget(self.btn_header)
        format_layout.addStretch()

        # Текстовый редактор
        self.text_editor = QTextEdit()
        self.text_editor.setAcceptRichText(False)

        self.layout.addWidget(self.format_panel)
        self.layout.addWidget(self.text_editor)

    def _wrap_selection(self, wrapper):
        """Обернуть выделенный текст в указанные символы"""
        cursor = self.text_editor.textCursor()
        selected = cursor.selectedText()
        cursor.insertText(f"{wrapper}{selected}{wrapper}")

    def _add_header(self):
        """Добавить заголовок Markdown"""
        cursor = self.text_editor.textCursor()
        cursor.insertText("## ")

    def set_content(self, text):
        """Установить содержимое редактора"""
        self.text_editor.setPlainText(text)

    def get_content(self):
        """Получить содержимое редактора"""
        return self.text_editor.toPlainText()

class FileEditorWindow(QMainWindow):
    """
        Главное окно редактора файлов с поддержкой форматов .st и .md.
        Обеспечивает создание, редактирование и сохранение файлов.
    """
    # Сигналы для обновления дерева файлов в родительском окне
    file_created = Signal(str)  # Путь к созданному файлу
    file_saved = Signal(str)    # Путь к сохраненному файлу
    file_deleted = Signal(str)  # Путь к удаленному файлу
    def __init__(self, parent=None):
        """
        Инициализация окна редактора файлов
        
        Args:
            parent: Родительское окно (необязательно)
        """
        super().__init__(parent)
        self.parent_panel = parent  # Ссылка на родительскую панель
        self.setWindowTitle("Редактор файлов")
        self.setMinimumSize(600, 500)  # Минимальные размеры окна
        self.current_file_path = None  # Путь к текущему открытому файлу

        self._init_ui()  # Инициализация интерфейса
        self.current_structure = None  # Для хранения структуры ST файла
        self.center_window()  # Добавляем центрирование после инициализации UI

    def center_window(self):
        """Центрирует окно на экране"""
        frame_geometry = self.frameGeometry()  # Получаем геометрию окна с учетом рамок
        screen_center = QApplication.primaryScreen().availableGeometry().center()  # Центр экрана
        frame_geometry.moveCenter(screen_center)  # Совмещаем центры
        self.move(frame_geometry.topLeft())  # Перемещаем окно

    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основной виджет и layout
        main_widget = QWidget()                     # Создаем центральный виджет окна
        self.setCentralWidget(main_widget)          # Устанавливаем его как центральный виджет окна
        main_layout = QVBoxLayout(main_widget)      # Создаем вертикальный layout для основного виджета
        main_layout.setContentsMargins(5, 5, 5, 5)  # Устанавливаем минимальные отступы layout

        # Панель кнопок с иконками
        #self.btn_panel = QWidget()                  # Виджет для панели кнопок
        #btn_layout = QHBoxLayout(self.btn_panel)    # Горизонтальный layout для кнопок
        #btn_layout.setSpacing(5)                    # Устанавливаем расстояние между кнопками

        # Создаем панель инструментов (кнопки будут над деревом)
        tool_panel = QWidget()
        tool_layout = QHBoxLayout(tool_panel)
        tool_layout.setSpacing(5)

        # Кнопка создания ST файла
        self.btn_new_st = QPushButton()                                             # Кнопка для создания ST файла
        self.btn_new_st.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))      # Иконка файла
        self.btn_new_st.setToolTip("Создать ST файл")                               # Подсказка при наведении
        self.btn_new_st.clicked.connect(self._new_st_file)                          # Подключение обработчика

        # Кнопка создания MD файла
        self.btn_new_md = QPushButton()                                                     # Кнопка для создания MD файла
        self.btn_new_md.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))   # Иконка папки
        self.btn_new_md.setToolTip("Создать MD файл")                                       # Подсказка при наведении
        self.btn_new_md.clicked.connect(self._new_md_file)                                  # Подключение обработчика

        # Кнопка создания папки (активна только для .st файлов)
        self.btn_new_folder = QPushButton()         # Кнопка создания папки
        self.btn_new_folder.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))   # Иконка директории
        self.btn_new_folder.setToolTip("Создать папку")   # Подсказка при наведении
        self.btn_new_folder.clicked.connect(self._create_folder)    # Подключение обработчика
        self.btn_new_folder.setEnabled(False)       # По умолчанию отключена

        # Кнопка создания шаблона (активна только для .st файлов)
        self.btn_new_template = QPushButton()                           # Кнопка создания шаблона
        self.btn_new_template.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))  # Иконка шаблона
        self.btn_new_template.setToolTip("Создать шаблон")              # Подсказка при наведении
        self.btn_new_template.clicked.connect(self._create_template)    # Подключение обработчика
        self.btn_new_template.setEnabled(False)                         # По умолчанию отключена

        # Кнопка сохранения
        self.btn_save = QPushButton()                                   # Кнопка сохранения
        self.btn_save.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))    # Иконка сохранения
        self.btn_save.setToolTip("Сохранить")                           # Подсказка при наведении
        self.btn_save.clicked.connect(self._save_file)                  # Подключение обработчика

        # Кнопка открытия
        self.btn_open = QPushButton()                                   # Кнопка открытия файла
        self.btn_open.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))    # Иконка открытия
        self.btn_open.setToolTip("Открыть")                             # Подсказка при наведении
        self.btn_open.clicked.connect(self._open_file)                  # Подключение обработчика

        # Переключатель режимов для ST файлов
        self.view_mode_group = QButtonGroup(self)
        self.text_mode_btn = QRadioButton("Текст")
        self.markdown_mode_btn = QRadioButton("Markdown")
        self.text_mode_btn.setChecked(True)
        self.view_mode_group.addButton(self.text_mode_btn)
        self.view_mode_group.addButton(self.markdown_mode_btn)
        self.view_mode_group.buttonClicked.connect(self._change_view_mode)

        # Добавляем кнопки
        # Добавляем кнопки на панель инструментов
        tool_layout.addWidget(self.btn_new_st)
        tool_layout.addWidget(self.btn_new_md)
        tool_layout.addWidget(self.btn_new_folder)
        tool_layout.addWidget(self.btn_new_template)
        tool_layout.addWidget(self.btn_open)
        tool_layout.addWidget(self.btn_save)
        tool_layout.addStretch()         # Добавляем растягивающееся пространство

        # Разделитель для дерева и редактора
        self.splitter = QSplitter(Qt.Vertical)                          # Вертикальный разделитель


        # Верхняя часть - дерево
        self.tree_view = QTreeView()                                    # Виджет для отображения дерева файлов
        if self.parent_panel:
            self.tree_model = self.parent_panel.tree_model              # Используем модель из родительского окна
        else:
            self.tree_model = None                                      # Если нет родителя - модель не задана
        self.tree_view.setModel(self.tree_model)                        # Устанавливаем модель для дерева

        # Средняя часть - кнопки
        button_panel = QWidget()                                        # Виджет для панели кнопок
        button_layout = QHBoxLayout(button_panel)                       # Горизонтальный layout
        button_layout.setContentsMargins(0, 0, 0, 0)                    # Без отступов
        button_layout.setSpacing(1)  # Уменьшаем расстояние между кнопками


        # Кнопки с иконками вместо текста
        self.save_btn = QPushButton()                            # Кнопка сохранения (дублирует основную)
        self.save_btn.setIcon(QIcon.fromTheme("document-save"))  # Иконка сохранения
        self.save_btn.setFixedSize(30, 30)                       # Квадратные кнопки  Фиксированный размер
        self.save_btn.setToolTip("Сохранить")                    # Подсказка при наведении
        self.save_btn.clicked.connect(self._save_file)           # Обработчик

        self.delete_btn = QPushButton()                           # Кнопка удаления
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))   # Иконка удаления
        self.delete_btn.setFixedSize(30, 30)                      # Фиксированный размер
        self.delete_btn.setToolTip("Удалить")                     # Подсказка при наведении
        self.delete_btn.clicked.connect(self._delete_file)        # Обработчик

        # Аналогично для остальных кнопок (cut, copy, paste)
        self.cut_btn = QPushButton() # Вырезать
        self.cut_btn.setIcon(QIcon.fromTheme("edit-cut"))
        self.cut_btn.setFixedSize(30, 30)
        self.cut_btn.setToolTip("Вырезать")
        self.cut_btn.clicked.connect(self._cut_text)

        self.copy_btn = QPushButton()  # Копировать
        self.copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_btn.setFixedSize(30, 30)
        self.copy_btn.setToolTip("Копировать")
        self.copy_btn.clicked.connect(self._copy_text)

        self.paste_btn = QPushButton()  # Вставить
        self.paste_btn.setIcon(QIcon.fromTheme("edit-paste"))
        self.paste_btn.setFixedSize(30, 30)
        self.paste_btn.setToolTip("Вставить")
        self.paste_btn.clicked.connect(self._paste_text)

        # Добавляем кнопки в layout
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.cut_btn)
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.paste_btn)

        # Текстовый редактор
        self.text_editor = QTextEdit()             # Основной текстовый редактор
        self.text_editor.setAcceptRichText(False)  # Режим plain text  Отключаем форматированный текст

        # Контейнер для редактора и кнопок
        editor_container = QWidget()                     # Контейнерный виджет
        editor_layout = QVBoxLayout(editor_container)    # Вертикальный layout
        editor_layout.setContentsMargins(0, 0, 0, 0)     # Без отступов
        editor_layout.setSpacing(0)                      # Без промежутков

        # Добавляем кнопки над редактором
        editor_layout.addWidget(button_panel)
        editor_layout.addWidget(self.text_editor)

        # Добавляем виджеты в разделитель
        self.splitter.addWidget(self.tree_view)          # Дерево файлов сверху
        self.splitter.addWidget(editor_container)        # Редактор снизу
        self.splitter.setSizes([300, 200])               # Начальные размеры областей

        main_layout.addWidget(tool_panel)  # Основная панель кнопок снизу
        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)

        
        # Подключаем сигналы дерева файлов
        self.tree_view.doubleClicked.connect(self._on_tree_item_double_clicked)
        
        # Создаем меню
        #self._create_menu_bar() # Это ненадо

        # Добавьте в метод _init_ui класса FileEditorWindow после создания tree_view:
        self.tree_view.setHeaderHidden(False)           # Показываем заголовки
        self.tree_view.setIndentation(10)               # Отступ для вложенных элементов
        self.tree_view.setAnimated(True)                # Анимация раскрытия
        self.tree_view.setUniformRowHeights(True)       # Одинаковая высота строк
        self.tree_view.setRootIsDecorated(True)         # Показываем корневой элемент
        self.tree_view.setExpandsOnDoubleClick(True)    # Раскрытие двойным кликом
        self.tree_view.setSortingEnabled(False)         # Сортировка отключена

        # Установите делегат (если он используется)
        if hasattr(self.parent_panel, 'delegate'):
            # Создаем новый делегат на основе родительского, но для текущего tree_view
            self.delegate = TreeItemDelegate(self.tree_view)
            self.tree_view.setItemDelegate(self.delegate)

        # Настройте стиль (можно скопировать из панели)
        self.tree_view.setStyleSheet("""
            QTreeView {
                background-color: white;
                border: 1px solid #ddd;
            }
            QTreeView::item {
                padding: 2px;
                margin: 0px;
                height: 20px;
            }
            /* Убираем стандартные треугольники */
            QTreeView::branch {
                background: transparent;
                border: 0px;
            }
            QTreeView::branch:has-siblings:!adjoins-item {
                border-image: none;
                image: none;
            }
            QTreeView::branch:has-siblings:adjoins-item {
                border-image: none;
                image: none;
            }
            QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                border-image: none;
                image: none;
            }
            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: none;
            }
            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings {
                border-image: none;
                image: none;
            }
        """)

        
    def _create_menu_bar(self):
        """Создание меню приложения"""
        menu_bar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menu_bar.addMenu("Файл")
        
        # Действия меню
        new_st_action = QAction("Новый ST файл", self)
        new_st_action.triggered.connect(lambda: self._new_file('st'))
        file_menu.addAction(new_st_action)
        
        new_md_action = QAction("Новый MD файл", self)
        new_md_action.triggered.connect(lambda: self._new_file('md'))
        file_menu.addAction(new_md_action)
        
        open_action = QAction("Открыть...", self)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Сохранить как...", self)
        save_as_action.triggered.connect(self._save_file_as)
        file_menu.addAction(save_as_action)
        
    def _new_file(self, extension):
        """
        Создание нового файла
        
        Args:
            extension: Расширение файла ('st' или 'md')
        """
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Создать новый {extension.upper()} файл",
            "",
            f"{extension.upper()} Files (*.{extension})"
        )
        
        if file_path:
            # Добавляем расширение, если его нет
            if not file_path.endswith(f'.{extension}'):
                file_path += f'.{extension}'
                
            try:
                # Создаем пустой файл
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
                    
                # Добавляем в модель дерева
                if extension == 'st':
                    self.tree_model.add_file(file_path)
                else:
                    self.tree_model.add_markdown_file(file_path)
                    
                self.current_file_path = file_path
                self.text_editor.clear()  # Очищаем редактор
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать файл: {str(e)}")
    
    def _open_file(self):
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
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.current_file_path = file_path

            if file_path.endswith('.st'):
                # ST файл - используем text_editor
                self.current_structure = self._parse_st_file(content)
                self.text_editor.setPlainText(content)
                self._update_st_display()

                # Настройка интерфейса для ST файлов
                self.btn_new_folder.setEnabled(True)
                self.btn_new_template.setEnabled(True)
                self.text_mode_btn.setEnabled(True)
                self.markdown_mode_btn.setEnabled(True)

            else:
                # MD файл - используем md_editor
                self.md_editor.set_content(content)
                self.text_editor.hide()
                self.md_editor.show()

                # Настройка интерфейса для MD файлов
                self.btn_new_folder.setEnabled(False)
                self.btn_new_template.setEnabled(False)
                self.text_mode_btn.setEnabled(False)
                self.markdown_mode_btn.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    #TODO пересматреть формироване метода _save_file
    def _save_file(self):
        """Сохранение текущего файла"""
        if not self.current_file_path:
            self._save_file_as()  # Если файл новый - вызываем "Сохранить как"
            return
            
        try:
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                if self.current_file_path.endswith('.md'):
                    f.write(self.text_editor.toMarkdown())  # Сохраняем Markdown
                else:
                    f.write(self.text_editor.toPlainText())  # Сохраняем обычный текст
                    
            QMessageBox.information(self, "Сохранено", "Файл успешно сохранен")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def _save_file_Варант_для_выбора(self):
        """Сохранение текущего файла."""
        if not self.current_file_path:
            self._save_file_as()
            return

        try:
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                if self.current_file_path.endswith('.md'):
                    f.write(self.md_editor.get_content())
                else:
                    f.write(self.text_editor.toPlainText())

            QMessageBox.information(self, "Сохранено", "Файл успешно сохранен")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    # TODO пересматреть формироване метода _save_file_as
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

    def _save_st_file(self):
        """
        Специальное сохранение для ST файлов.
        Генерирует содержимое из текущей структуры и сохраняет в файл.
        """
        if not self.current_file_path or not self.current_structure:
            return

        try:
            content = self._generate_st_content(self.current_structure)
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            raise Exception(f"Ошибка сохранения ST файла: {str(e)}")

    #TODO разобраться с работой этого метода где применяется и зачем, нужно его переписывать _parse_st_file
    def _parse_st_file(self, content):
        """
        Упрощенный парсинг ST файла (для демонстрации).
        В реальной реализации следует использовать ANTLR парсер.

        Args:
            content: Содержимое ST файла

        Returns:
            dict: Словарь с распарсенной структурой файла
        """
        try:
            # Ищем имя корневой папки
            start = content.find('{"') + 2
            end = content.find('"', start)
            root_name = content[start:end]

            # Создаем базовую структуру
            structure = {
                'type': 'file',
                'name': os.path.basename(self.current_file_path).replace('.st', ''),
                'content': {
                    'type': 'folder',
                    'name': root_name,
                    'children': []
                }
            }

            # Упрощенный поиск шаблонов в файле
            templates = content.split('{0, {')
            for template in templates[1:]:
                parts = template.split('"')
                if len(parts) >= 6:
                    name = parts[1]
                    template_content = parts[5]
                    structure['content']['children'].append({
                        'type': 'template',
                        'name': name,
                        'content': template_content
                    })

            return structure

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка парсинга ST файла: {str(e)}")
            return None
    def _delete_file(self):
        """Удаление текущего файла"""
        if not self.current_file_path:
            QMessageBox.warning(self, "Ошибка", "Нет открытого файла для удаления")
            return
            
        # Запрос подтверждения
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить файл {os.path.basename(self.current_file_path)}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(self.current_file_path)  # Удаляем файл
                
                # Удаляем из модели дерева
                if self.parent_panel:
                    self.parent_panel.remove_file(self.current_file_path)
                    
                self.current_file_path = None
                self.text_editor.clear()  # Очищаем редактор
                
                QMessageBox.information(self, "Удалено", "Файл успешно удален")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить файл: {str(e)}")
    
    def _on_tree_item_double_clicked(self, index):
        """
        Обработка двойного клика по элементу дерева
        
        Args:
            index: Индекс элемента в дереве
        """
        if not index.isValid():
            return
            
        item = index.internalPointer()
        if not item:
            return
            
        # Загружаем содержимое файла или шаблона
        if item.item_data[1] in ['file', 'markdown']:
            file_path = item.item_data[2]
            self._load_file_content(file_path)
        elif item.item_data[1] == 'template':
            self.current_file_path = None
            self.text_editor.setPlainText(item.item_data[2])
    
    def _cut_text(self):
        """Вырезание выделенного текста"""
        self.text_editor.cut()
    
    def _copy_text(self):
        """Копирование выделенного текста"""
        self.text_editor.copy()
    
    def _paste_text(self):
        """Вставка текста из буфера обмена"""
        self.text_editor.paste()

    def expand_all(self):
        """Развернуть все узлы в дереве редактора"""
        self.tree_view.expandAll()

    def collapse_all(self):
        """Свернуть все узлы в дереве редактора"""
        self.tree_view.collapseAll()

    def _new_st_file(self):
        """
        Создание нового ST файла.
        Открывает диалог сохранения файла и инициализирует базовую структуру.
        """
        path, _ = QFileDialog.getSaveFileName(
            self, "Создать ST файл", "", "ST Files (*.st)")

        if path:
            # Добавляем расширение, если его нет
            if not path.endswith('.st'):
                path += '.st'

            # Базовая структура нового ST файла
            default_structure = {
                'type': 'file',
                'name': os.path.basename(path).replace('.st', ''),
                'content': {
                    'type': 'folder',
                    'name': os.path.basename(path).replace('.st', ''),
                    'children': []
                }
            }

            try:
                # Создаем файл и записываем начальную структуру
                with open(path, 'w', encoding='utf-8') as f:
                    content = self._generate_st_content(default_structure)
                    f.write(content)

                # Обновляем текущий файл и структуру
                self.current_file_path = path
                self.current_structure = default_structure
                self._update_tree_view()
                self.file_created.emit(path)  # Отправляем сигнал о создании файла

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать файл: {str(e)}")

    def _new_md_file(self):
        """
        Создание нового MD файла.
        Открывает диалог сохранения файла и инициализирует базовую структуру.
        """
        path, _ = QFileDialog.getSaveFileName(
            self, "Создать MD файл", "", "Markdown Files (*.md)")

        if path:
            # Добавляем расширение, если его нет
            if not path.endswith('.md'):
                path += '.md'

            try:
                # Создаем файл с заголовком, соответствующим имени файла
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(f"# {os.path.basename(path).replace('.md', '')}\n\n")

                # Обновляем текущий файл и загружаем его содержимое
                self.current_file_path = path
                self._load_file_content(path)
                self.file_created.emit(path)  # Отправляем сигнал о создании файла

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать файл: {str(e)}")

    def _create_folder(self):
        """
        Создание новой папки в текущем ST файле.
        Запрашивает имя папки через диалоговое окно.
        """
        if not self.current_file_path or not self.current_file_path.endswith('.st'):
            return

        # Запрашиваем имя папки у пользователя
        name, ok = QInputDialog.getText(
            self, "Создать папку", "Введите имя папки:")

        if ok and name:
            # Создаем структуру новой папки
            new_folder = {
                'type': 'folder',
                'name': name,
                'children': []
            }

            # Добавляем папку в корень (можно доработать для вложенных папок)
            self.current_structure['content']['children'].append(new_folder)
            self._save_st_file()  # Сохраняем изменения
            self._update_tree_view()  # Обновляем отображение дерева

    def _create_template(self):
        """
        Создание нового шаблона в текущем ST файле.
        Запрашивает имя шаблона, использует текущий текст из редактора как содержимое.
        """
        if not self.current_file_path or not self.current_file_path.endswith('.st'):
            return

        # Запрашиваем имя шаблона у пользователя
        name, ok = QInputDialog.getText(
            self, "Создать шаблон", "Введите имя шаблона:")

        if ok and name:
            # Создаем структуру нового шаблона
            new_template = {
                'type': 'template',
                'name': name,
                'content': self.text_editor.toPlainText()  # Текст из редактора
            }

            # Добавляем шаблон в корень (можно доработать для вложенных папок)
            self.current_structure['content']['children'].append(new_template)
            self._save_st_file()  # Сохраняем изменения
            self._update_tree_view()  # Обновляем отображение дерева

    def _open_file(self):
        """Открытие существующего файла через диалоговое окно."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "",
            "ST Files (*.st);;Markdown Files (*.md)")

        if path:
            self._load_file_content(path)  # Загружаем содержимое файла

    '''def _load_file_content(self, path):
        """
        Загрузка содержимого файла в редактор.

        Args:
            path: Путь к открываемому файлу
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.current_file_path = path

            if path.endswith('.st'):
                # Парсим ST файл (упрощенная версия)
                self.current_structure = self._parse_st_file(content)
                self._update_tree_view()
                # Активируем кнопки для работы с ST файлом
                self.btn_new_folder.setEnabled(True)
                self.btn_new_template.setEnabled(True)
            else:
                # Загружаем Markdown файл
                self.text_editor.setPlainText(content)
                # Деактивируем кнопки, не относящиеся к MD файлам
                self.btn_new_folder.setEnabled(False)
                self.btn_new_template.setEnabled(False)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")
    '''
    def _update_tree_view(self):
        """
        Обновление отображения дерева файлов.
        В текущей реализации не завершено - нужно подключить модель дерева.
        """
        if not self.current_structure:
            return

        # TODO: Реализовать через QStandardItemModel
        pass

    def _on_item_double_clicked(self, index):
        """
        Обработчик двойного клика по элементу дерева.
        Должен загружать содержимое элемента в текстовый редактор.

        Args:
            index: Индекс элемента в дереве
        """
        # TODO: Реализовать загрузку содержимого
        pass

    # TODO: разобраться с этим методом нужен ли он _generate_st_content
    def _generate_st_content(self, structure):
        """
        Генерация содержимого ST файла согласно грамматике STFile.g4.

        Args:
            structure: Словарь с описанием структуры файла

        Returns:
            str: Строка с содержимым файла в правильном формате
        """

        def build_folder(folder):
            """Рекурсивное построение структуры папок."""
            children = []
            for child in folder.get('children', []):
                if child['type'] == 'folder':
                    # Формируем структуру для вложенной папки
                    children.append(
                        f"{{1, {{\"{child['name']}\", 1, 0, \"\", \"\"}}, [\n"
                        f"{build_folder(child)}\n"
                        "]}}"
                    )
                elif child['type'] == 'template':
                    # Формируем структуру для шаблона
                    children.append(
                        f"{{0, {{\"{child['name']}\", 0, 1, \"\", \"{child['content']}\"}}}}"
                    )

            return ",\n".join(children)

        # Формируем корневую папку
        root_folder = structure['content']
        return (
            f"{{1, {{\"{root_folder['name']}\", 1, 0, \"\", \"\"}}, [\n"
            f"{build_folder(root_folder)}\n"
            "]}}"
        )

    def _change_view_mode(self):
        """Переключение между режимами просмотра ST файла"""
        if not self.current_file_path or not self.current_file_path.endswith('.st'):
            return

        if self.markdown_mode_btn.isChecked():
            # Переключаемся в режим Markdown
            md_content = self._convert_st_to_markdown(self.text_editor.toPlainText())
            self.md_editor.set_content(md_content)
            self.text_editor.hide()
            self.md_editor.show()
        else:
            # Возвращаемся к обычному тексту
            self.md_editor.hide()
            self.text_editor.show()
# file_editor.py
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QTextEdit, QTreeView, QFileDialog,
                              QMessageBox, QSplitter)
from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QAction, QIcon
from delegates import TreeItemDelegate


class FileEditorWindow(QMainWindow):
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
        
    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Основной виджет и layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(1, 1, 1, 1)  # Отступы
        
        # Разделитель для дерева и редактора
        self.splitter = QSplitter(Qt.Vertical)

        # Верхняя часть - дерево
        self.tree_view = QTreeView()
        if self.parent_panel:
            self.tree_model = self.parent_panel.tree_model
        else:
            self.tree_model = None
        self.tree_view.setModel(self.tree_model)

        # Средняя часть - кнопки
        button_panel = QWidget()
        button_layout = QHBoxLayout(button_panel)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(2)  # Уменьшаем расстояние между кнопками


        # Кнопки с иконками вместо текста
        self.save_btn = QPushButton()
        self.save_btn.setIcon(QIcon.fromTheme("document-save"))  # Иконка сохранения
        self.save_btn.setFixedSize(30, 30)  # Квадратные кнопки
        self.save_btn.setToolTip("Сохранить")  # Подсказка при наведении
        self.save_btn.clicked.connect(self._save_file)

        self.delete_btn = QPushButton()
        self.delete_btn.setIcon(QIcon.fromTheme("edit-delete"))
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setToolTip("Удалить")
        self.delete_btn.clicked.connect(self._delete_file)

        self.cut_btn = QPushButton()
        self.cut_btn.setIcon(QIcon.fromTheme("edit-cut"))
        self.cut_btn.setFixedSize(30, 30)
        self.cut_btn.setToolTip("Вырезать")
        self.cut_btn.clicked.connect(self._cut_text)

        self.copy_btn = QPushButton()
        self.copy_btn.setIcon(QIcon.fromTheme("edit-copy"))
        self.copy_btn.setFixedSize(30, 30)
        self.copy_btn.setToolTip("Копировать")
        self.copy_btn.clicked.connect(self._copy_text)

        self.paste_btn = QPushButton()
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
        self.text_editor = QTextEdit()
        self.text_editor.setAcceptRichText(False)  # Режим plain text

        # Контейнер для редактора и кнопок
        editor_container = QWidget()
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        # Добавляем кнопки над редактором
        editor_layout.addWidget(button_panel)
        editor_layout.addWidget(self.text_editor)

        # Добавляем виджеты в разделитель
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(editor_container)
        self.splitter.setSizes([300, 200])  # Начальные размеры областей

        # Добавляем разделитель в основной layout
        main_layout.addWidget(self.splitter)
        
        # Подключаем сигналы дерева файлов
        self.tree_view.doubleClicked.connect(self._on_tree_item_double_clicked)
        
        # Создаем меню
        self._create_menu_bar()

        # Добавьте в метод _init_ui класса FileEditorWindow после создания tree_view:
        self.tree_view.setHeaderHidden(False)
        self.tree_view.setIndentation(10)
        self.tree_view.setAnimated(True)
        self.tree_view.setUniformRowHeights(True)
        self.tree_view.setRootIsDecorated(True)
        self.tree_view.setExpandsOnDoubleClick(True)
        self.tree_view.setSortingEnabled(False)

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
        """
        Загрузка содержимого файла в редактор
        
        Args:
            file_path: Путь к файлу для загрузки
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            self.current_file_path = file_path
            if file_path.endswith('.md'):
                self.text_editor.setMarkdown(content)  # Markdown-форматирование
            else:
                self.text_editor.setPlainText(content)  # Обычный текст
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
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
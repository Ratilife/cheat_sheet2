# file_editor.py
import os
import json
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QTextEdit, QTreeView, QFileDialog,
                              QMessageBox, QSplitter, QInputDialog)
from PySide6.QtCore import Qt, QModelIndex, Signal
from PySide6.QtGui import QAction, QIcon

class FileEditorWindow(QMainWindow):
    # Сигналы для обновления дерева
    file_created = Signal(str)  # Путь к файлу
    file_saved = Signal(str)
    file_deleted = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_panel = parent
        self.setWindowTitle("Редактор файлов")
        self.setMinimumSize(800, 600)
        self.current_file_path = None
        self.current_structure = None  # Для хранения структуры ST файла
        self._init_ui()

    def _init_ui(self):
        # Основной layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Кнопки создания элементов
        self.btn_panel = QWidget()
        btn_layout = QHBoxLayout(self.btn_panel)
        
        self.btn_new_st = QPushButton("Создать ST файл")
        self.btn_new_st.clicked.connect(self._new_st_file)
        
        self.btn_new_md = QPushButton("Создать MD файл")
        self.btn_new_md.clicked.connect(self._new_md_file)
        
        self.btn_new_folder = QPushButton("Создать папку")
        self.btn_new_folder.clicked.connect(self._create_folder)
        self.btn_new_folder.setEnabled(False)
        
        self.btn_new_template = QPushButton("Создать шаблон")
        self.btn_new_template.clicked.connect(self._create_template)
        self.btn_new_template.setEnabled(False)

        btn_layout.addWidget(self.btn_new_st)
        btn_layout.addWidget(self.btn_new_md)
        btn_layout.addWidget(self.btn_new_folder)
        btn_layout.addWidget(self.btn_new_template)

        # Дерево и редактор
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Дерево файлов
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.doubleClicked.connect(self._on_item_double_clicked)
        
        # Текстовый редактор
        self.text_editor = QTextEdit()
        self.text_editor.setAcceptRichText(False)
        
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.text_editor)
        self.splitter.setSizes([300, 500])

        main_layout.addWidget(self.btn_panel)
        main_layout.addWidget(self.splitter)

        # Меню
        self._create_menu()

    def _create_menu(self):
        menu_bar = self.menuBar()
        
        # Меню Файл
        file_menu = menu_bar.addMenu("Файл")
        
        new_st_action = QAction("Новый ST файл", self)
        new_st_action.triggered.connect(self._new_st_file)
        file_menu.addAction(new_st_action)
        
        new_md_action = QAction("Новый MD файл", self)
        new_md_action.triggered.connect(self._new_md_file)
        file_menu.addAction(new_md_action)
        
        open_action = QAction("Открыть...", self)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("Сохранить", self)
        save_action.triggered.connect(self._save_file)
        file_menu.addAction(save_action)

    def _new_st_file(self):
        """Создание нового ST файла"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Создать ST файл", "", "ST Files (*.st)")
        
        if path:
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
                with open(path, 'w', encoding='utf-8') as f:
                    # Формируем содержимое согласно STFile.g4
                    content = self._generate_st_content(default_structure)
                    f.write(content)
                
                self.current_file_path = path
                self.current_structure = default_structure
                self._update_tree_view()
                self.file_created.emit(path)
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать файл: {str(e)}")

    def _generate_st_content(self, structure):
        """Генерация содержимого ST файла согласно грамматике"""
        def build_folder(folder):
            children = []
            for child in folder.get('children', []):
                if child['type'] == 'folder':
                    children.append(
                        f"{{1, {{\"{child['name']}\", 1, 0, \"\", \"\"}}, [\n"
                        f"{build_folder(child)}\n"
                        "]}}"
                    )
                elif child['type'] == 'template':
                    children.append(
                        f"{{0, {{\"{child['name']}\", 0, 1, \"\", \"{child['content']}\"}}}}"
                    )
            
            return ",\n".join(children)
        
        root_folder = structure['content']
        return (
            f"{{1, {{\"{root_folder['name']}\", 1, 0, \"\", \"\"}}, [\n"
            f"{build_folder(root_folder)}\n"
            "]}}"
        )

    def _new_md_file(self):
        """Создание нового MD файла"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Создать MD файл", "", "Markdown Files (*.md)")
        
        if path:
            if not path.endswith('.md'):
                path += '.md'
            
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(f"# {os.path.basename(path).replace('.md', '')}\n\n")
                
                self.current_file_path = path
                self._load_file_content(path)
                self.file_created.emit(path)
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать файл: {str(e)}")

    def _create_folder(self):
        """Создание новой папки в ST файле"""
        if not self.current_file_path or not self.current_file_path.endswith('.st'):
            return
            
        name, ok = QInputDialog.getText(
            self, "Создать папку", "Введите имя папки:")
        
        if ok and name:
            new_folder = {
                'type': 'folder',
                'name': name,
                'children': []
            }
            
            # Здесь нужно определить, куда добавлять папку (в корень или выбранную папку)
            # Для простоты добавляем в корень
            self.current_structure['content']['children'].append(new_folder)
            self._save_st_file()
            self._update_tree_view()

    def _create_template(self):
        """Создание нового шаблона в ST файле"""
        if not self.current_file_path or not self.current_file_path.endswith('.st'):
            return
            
        name, ok = QInputDialog.getText(
            self, "Создать шаблон", "Введите имя шаблона:")
        
        if ok and name:
            new_template = {
                'type': 'template',
                'name': name,
                'content': self.text_editor.toPlainText()
            }
            
            # Добавляем в корень (можно доработать для вложенных папок)
            self.current_structure['content']['children'].append(new_template)
            self._save_st_file()
            self._update_tree_view()

    def _open_file(self):
        """Открытие файла"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "", 
            "ST Files (*.st);;Markdown Files (*.md)")
        
        if path:
            self._load_file_content(path)

    def _load_file_content(self, path):
        """Загрузка содержимого файла"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.current_file_path = path
            
            if path.endswith('.st'):
                # Парсим ST файл (упрощенная версия)
                self.current_structure = self._parse_st_file(content)
                self._update_tree_view()
                self.btn_new_folder.setEnabled(True)
                self.btn_new_template.setEnabled(True)
            else:
                self.text_editor.setPlainText(content)
                self.btn_new_folder.setEnabled(False)
                self.btn_new_template.setEnabled(False)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")

    def _parse_st_file(self, content):
        """Упрощенный парсинг ST файла (для демонстрации)"""
        # В реальной реализации нужно использовать ANTLR парсер
        try:
            # Ищем имя корневой папки
            start = content.find('{"') + 2
            end = content.find('"', start)
            root_name = content[start:end]
            
            structure = {
                'type': 'file',
                'name': os.path.basename(self.current_file_path).replace('.st', ''),
                'content': {
                    'type': 'folder',
                    'name': root_name,
                    'children': []
                }
            }
            
            # Упрощенный поиск шаблонов
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

    def _save_file(self):
        """Сохранение текущего файла"""
        if not self.current_file_path:
            return
            
        try:
            if self.current_file_path.endswith('.st'):
                self._save_st_file()
            else:
                with open(self.current_file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_editor.toPlainText())
                
            self.file_saved.emit(self.current_file_path)
            QMessageBox.information(self, "Сохранено", "Файл успешно сохранен")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def _save_st_file(self):
        """Специальное сохранение для ST файлов"""
        if not self.current_file_path or not self.current_structure:
            return
            
        try:
            content = self._generate_st_content(self.current_structure)
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            raise Exception(f"Ошибка сохранения ST файла: {str(e)}")

    def _update_tree_view(self):
        """Обновление отображения дерева"""
        # В реальной реализации нужно использовать модель дерева
        # Здесь упрощенная версия для демонстрации
        if not self.current_structure:
            return
            
        # Можно реализовать через QStandardItemModel
        pass

    def _on_item_double_clicked(self, index):
        """Обработка двойного клика по элементу дерева"""
        # Загрузка содержимого элемента в редактор
        pass

    # Дополнительные методы (удаление, копирование и т.д.) можно добавить по аналогии
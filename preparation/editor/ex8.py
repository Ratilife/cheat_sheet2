# settings_window.py
import os
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QFileDialog)
from PySide6.QtCore import QStandardPaths

class SettingsWindow(QWidget):
    def __init__(self, parent=None):
        """
        Окно настроек программы
        
        Args:
            parent: Родительское окно (необязательно)
        """
        super().__init__(parent)
        self.settings_file = "settings.json"  # Файл для хранения настроек
        self.root_path = ""  # Текущий путь корневой папки
        self._init_ui()  # Инициализация интерфейса
        self._load_settings()  # Загрузка сохраненных настроек

    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("Настройка")
        self.setMinimumSize(400, 200)
        
        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        
        # Секция пути корневой папки
        path_layout = QVBoxLayout()
        
        # Метка и поле для пути
        path_label = QLabel("Путь к корневой папке:")
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Выберите папку для хранения данных программы")
        
        # Кнопка выбора папки
        browse_btn = QPushButton("Выбрать папку")
        browse_btn.clicked.connect(self._select_root_folder)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_btn)
        
        # Секция закладок
        bookmark_layout = QVBoxLayout()
        
        # Метка и поле для закладки
        bookmark_label = QLabel("Создать закладку:")
        self.bookmark_edit = QLineEdit()
        self.bookmark_edit.setPlaceholderText("Введите название закладки")
        
        # Кнопка создания закладки
        bookmark_btn = QPushButton("Создать закладку")
        bookmark_btn.clicked.connect(self._create_bookmark)
        
        bookmark_layout.addWidget(bookmark_label)
        bookmark_layout.addWidget(self.bookmark_edit)
        bookmark_layout.addWidget(bookmark_btn)
        
        # Кнопка закрытия
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(self.close)
        
        # Добавляем все секции в основной layout
        main_layout.addLayout(path_layout)
        main_layout.addLayout(bookmark_layout)
        main_layout.addStretch()
        main_layout.addWidget(close_btn)
        
        self.setLayout(main_layout)

    def _select_root_folder(self):
        """
        Выбор корневой папки через диалоговое окно
        """
        # Получаем предложенный путь (либо текущий, либо домашнюю директорию)
        initial_path = self.root_path or QStandardPaths.writableLocation(QStandardPaths.HomeLocation)
        
        # Открываем диалог выбора папки
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Выберите корневую папку",
            initial_path,
            QFileDialog.ShowDirsOnly
        )
        
        if folder_path:
            # Если уже был установлен путь - запрашиваем подтверждение
            if self.root_path and self.root_path != folder_path:
                reply = QMessageBox.question(
                    self,
                    "Подтверждение",
                    "Вы уверены, что хотите изменить путь корневой папки?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.No:
                    return
            
            self.root_path = folder_path
            self.path_edit.setText(folder_path)
            self._save_settings()

    def _create_bookmark(self):
        """
        Создание закладки (заглушка)
        """
        bookmark_name = self.bookmark_edit.text().strip()
        if bookmark_name:
            # Здесь будет функционал создания закладки
            pass

    def _load_settings(self):
        """
        Загрузка настроек из JSON файла
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.root_path = settings.get('root_path', '')
                    self.path_edit.setText(self.root_path)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")

    def _save_settings(self):
        """
        Сохранение настроек в JSON файл
        """
        try:
            settings = {
                'root_path': self.root_path
            }
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    def closeEvent(self, event):
        """
        Обработчик закрытия окна
        """
        self._save_settings()
        event.accept()
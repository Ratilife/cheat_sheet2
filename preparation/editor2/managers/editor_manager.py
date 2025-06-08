class EditorManager:

    def _clear_viewer(self):
        """Очищает все просмотрщики содержимого"""
        if hasattr(self, 'markdown_viewer'):
            self.markdown_viewer.set_content("")

        if hasattr(self, 'st_content_viewer'):  # Если у вас есть отдельный виджет для ST
            self.st_content_viewer.clear()

        # Или если используется единый виджет:
        if hasattr(self, 'content_view'):
            self.content_view.clear()

    def _change_view_mode(self):
        """Переключение между режимами просмотра ST файла"""
        if not self.current_file_path or not self.current_file_path.endswith('.st'):
            return

        if self.markdown_mode_btn.isChecked():
            # Переключаемся в режим Markdown
            md_content = self._convert_st_to_markdown(self.text_editor.toPlainText())
            self.md_viewer.set_content(md_content)
            self.text_editor.hide()
            self.md_viewer.show()
        else:
            # Возвращаемся к обычному тексту
            self.text_editor.show()  # <-- Гарантированно показываем text_editor
            self.md_viewer.hide()

    def _reset_editors(self):
        """Сбрасывает состояние всех редакторов
         Основное назначение метода - приведение всех редакторов в исходное состояние
         Используется при:
         1. Инициализации окна
         2. Очистке перед загрузкой нового файла
         3. Обработке ошибок
         4. Удалении файла
        """
        self.text_editor.clear()
        # Очистка содержимого основного текстового редактора (QTextEdit)
        # Удаляет весь текст и сбрасывает состояние редактора
        self.md_viewer.set_content("")
        # Очистка просмотрщика Markdown
        # Передает пустую строку в метод set_content() просмотрщика
        self.text_editor.show()
        # Гарантированное отображение основного текстового редактора
        # Делает виджет видимым (если был скрыт)
        self.md_viewer.hide()
        # Гарантированное скрытие просмотрщика Markdown
        # Делает виджет невидимым (если был показан)
        self.text_mode_btn.setChecked(True)
        # Установка переключателя режима просмотра в положение "Текст"
        # Активирует радио-кнопку текстового режима (если доступна)
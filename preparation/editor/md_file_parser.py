import os
import re
from PySide6.QtCore import QRegularExpression
from PySide6.QtWidgets import  QWidget,QVBoxLayout,QHBoxLayout, QButtonGroup, QRadioButton , QTextEdit
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

# Добавляем новые импорты
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
import re
class MarkdownListener:
    def __init__(self):
        self.structure = []

    def get_structure(self):
        return self.structure

    def parse_markdown_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_name = os.path.splitext(os.path.basename(file_path))[0]

            self.structure = [{
                'name': file_name,
                'type': 'markdown',
                'content': content
            }]

            return {
                'structure': self.structure,
                'root_name': file_name
            }
        except Exception as e:
            print(f"Error parsing markdown file: {str(e)}")
            return {
                'structure': [],
                'root_name': "Error"
            }


class MarkdownViewer(QWidget):
    """Класс для отображения MD файлов в двух режимах: текст и markdown"""

    def __init__(self, parent=None):
        # Инициализация базового класса QWidget
        super().__init__(parent)
        self.parent = parent            # Сохранение ссылки на родительский виджет
        self._init_ui()                  # Инициализация интерфейса
        self._current_mode = 'markdown'  # Текущий режим ('text' или 'markdown')
        self.highlighter = None      # Ссылка на экземпляр подсветки синтаксиса

    def _init_ui(self):
        """Инициализация интерфейса просмотрщика MD"""
        self.layout = QVBoxLayout(self)                 # Основной вертикальный layout
        self.layout.setContentsMargins(0, 0, 0, 0)      # Убираем отступы по краям

        # Панель переключения режимов
        self.mode_panel = QWidget()
        mode_layout = QHBoxLayout(self.mode_panel)
        mode_layout.setSpacing(5)                       # Расстояние между элементами

        # Группа для переключателей (радио-кнопок)
        self.mode_group = QButtonGroup(self)

        # Кнопка для текстового режима
        self.text_mode_btn = QRadioButton("Текст")

        # Кнопка для markdown режима
        self.markdown_mode_btn = QRadioButton("Markdown")
        self.markdown_mode_btn.setChecked(True)  # По умолчанию выбран текстовый режим

        # Добавление кнопок в группу
        self.mode_group.addButton(self.text_mode_btn)
        self.mode_group.addButton(self.markdown_mode_btn)
        # Подключение сигнала изменения выбранной кнопки
        self.mode_group.buttonClicked.connect(self._change_mode)

        # Добавление кнопок на панель
        mode_layout.addWidget(self.text_mode_btn)
        mode_layout.addWidget(self.markdown_mode_btn)
        # Добавление растягивающегося пространства
        mode_layout.addStretch()

        # Текстовый редактор для редактирования Markdown
        self.text_editor = QTextEdit()
        self.text_editor.setAcceptRichText(False)                            # Только plain text
        # Инициализация подсветки синтаксиса для текстового редактора
        self.highlighter = MarkdownHighlighter(self.text_editor.document())

        # Редактор для просмотра HTML (рендер Markdown)
        self.markdown_editor = QTextEdit()
        self.markdown_editor.setReadOnly(True)                              # Только для чтения
        self.markdown_editor.setVisible(True)                               # по умолчанию видим
        self.text_editor.setVisible(False)                                  # По умолчанию скрыт

        # Добавление виджетов на основной layout
        self.layout.addWidget(self.mode_panel)
        self.layout.addWidget(self.text_editor)
        self.layout.addWidget(self.markdown_editor)

    def _change_mode(self):
        """Переключение между режимами просмотра"""
        if self.text_mode_btn.isChecked():
            # Активация текстового режима
            self._current_mode = 'text'
            self.markdown_editor.setVisible(False)
            self.text_editor.setVisible(True)
        else:
            # Активация markdown режима
            self._current_mode = 'markdown'
            # Конвертируем текст в HTML для отображения markdown
            html = self._convert_md_to_html(self.text_editor.toPlainText())
            self.markdown_editor.setHtml(html)
            self.text_editor.setVisible(False)
            self.markdown_editor.setVisible(True)

    def _convert_md_to_html(self, md_text):
        """Конвертирует Markdown в HTML с подсветкой синтаксиса через Pygments"""

        def highlight_code(match):
            language = match.group(1) or 'text'
            code = match.group(2)
            try:
                lexer = get_lexer_by_name(language, stripall=True)
            except ClassNotFound:
                lexer = guess_lexer(code)
            formatter = HtmlFormatter(style='default', noclasses=True)
            return highlight(code, lexer, formatter)

        # Обработка блоков кода ```lang ... ```
        html = re.sub(
            r'```(\w+)?\n(.*?)\n```',
            highlight_code,
            md_text,
            flags=re.DOTALL
        )

        # Обработка остального Markdown (как у вас было)
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        # ... остальные замены ...

        return f'<div class="markdown-content">{html}</div>'

    def set_content(self, text):
        """Установка содержимого редактора"""
        self.text_editor.setPlainText(text)
        if self._current_mode == 'markdown':
            # Если в режиме markdown, сразу конвертируем в HTML
            html = self._convert_md_to_html(text)
            self.markdown_editor.setHtml(html)

    def get_content(self):
        """Получение содержимого редактора"""
        return self.text_editor.toPlainText()

    def set_view_mode(self, mode):
        """Устанавливает режим отображения: 'text' или 'markdown'"""
        if mode not in ['text', 'markdown']:
            return

        self._current_mode = mode

        # Обновляем состояние кнопок
        if mode == 'text':
            self.text_mode_btn.setChecked(True)
        else:
            self.markdown_mode_btn.setChecked(True)

        # Вызываем _change_mode для обновления отображения
        self._change_mode()

class MarkdownHighlighter(QSyntaxHighlighter):  # <-- Новый класс для подсветки синтаксиса
    """Класс для подсветки синтаксиса Markdown в QTextDocument"""

    def __init__(self, parent=None):
        super().__init__(parent)        # Инициализация базового класса QSyntaxHighlighter
        self._init_rules()              # Вызов метода для установки правил подсветки

        # Добавляем формат для блоков кода
        self.code_block_format = QTextCharFormat()
        self.code_block_format.setFontFamily("Courier New")
        self.code_block_format.setBackground(QColor("#f5f5f5"))

    def _init_rules(self):
        """Инициализация правил подсветки синтаксиса Markdown"""
        self.rules = []                                         # Список кортежей (регулярное выражение, формат)

        # # Формат для заголовков (#, ## и т.д.)
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#0066cc"))          # Синий цвет
        header_format.setFontWeight(QFont.Bold)                 # Жирный шрифт
        self.rules.append((r'^#{1,6}\s.*$', header_format))     # Регулярное выражение для заголовков (1-6 # в начале строки)

        # Формат для жирного текста (**текст** или __текст__)
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)                   # **текст**
        self.rules.append((r'\*\*(.*?)\*\*', bold_format))      # __текст__
        self.rules.append((r'__(.*?)__', bold_format))

        # Формат для курсивного текста (*текст* или _текст_)
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.rules.append((r'\*(.*?)\*', italic_format))        # *текст*
        self.rules.append((r'_(.*?)_', italic_format))          # _текст_

        # Формат для встроенного кода (`код`)
        code_format = QTextCharFormat()
        code_format.setFontFamily("Courier")                    # Моноширинный шрифт
        code_format.setBackground(QColor("#f0f0f0"))            # Светло-серый фон
        self.rules.append((r'`(.*?)`', code_format))

        # Формат для маркированных и нумерованных списков
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#993399"))            # Фиолетовый цвет
        self.rules.append((r'^[\*\-\+] .*$', list_format))      # *, -, +
        self.rules.append((r'^\d+\. .*$', list_format))         # 1., 2. и т.д.

        # Формат для ссылок ([текст](url))
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#009900"))            # Зеленый цвет
        link_format.setFontUnderline(True)                       # Подчеркивание
        self.rules.append((r'\[.*?\]\(.*?\)', link_format))

        # Формат для горизонтальных линий (---, ***, ___)
        line_format = QTextCharFormat()
        line_format.setForeground(QColor("#666666"))            # Серый цвет
        self.rules.append((r'^[-*_]{3,}$', line_format))

        '''# Добавляем правило для блоков кода с языком ```language
        self.code_block_format = QTextCharFormat()
        self.code_block_format.setFontFamily("Courier New")
        self.code_block_format.setBackground(QColor("#f5f5f5"))
        self.rules.append((r'^```(\w+)?$', self.code_block_format)) '''
    def highlightBlock(self, text):
        """Переопределенный метод для подсветки текста.
        Вызывается для каждого блока текста в документе."""
        for pattern, fmt in self.rules:
            expression = QRegularExpression(pattern)            # Создание регулярного выражения
            match_iterator = expression.globalMatch(text)       # Поиск всех совпадений в тексте
            # Применение формата к каждому совпадению
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # Новый код: подсветка блоков кода ```
        if '```' in text:
            self.setFormat(0, len(text), self.code_block_format)

        '''# Дополнительно: подсветка всего блока кода (если он открыт)
        if self.previousBlockState() == 1:  # 1 = внутри блока кода
            self.setFormat(0, len(text), self.code_block_format)
            self.setCurrentBlockState(1)  # Продолжаем блок кода
            if text.strip() == '```':  # Конец блока кода
                self.setCurrentBlockState(0)
        elif text.strip().startswith('```') and len(text.strip()) > 3:
            self.setCurrentBlockState(1)  # Начало блока кода'''


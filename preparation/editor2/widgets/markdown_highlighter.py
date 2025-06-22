from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter
from preparation.editor2.widgets.markdown_styles import MarkdownStyles


class MarkdownHighlighter(QSyntaxHighlighter):
    """Класс для подсветки синтаксиса Markdown в QTextDocument"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.styles = MarkdownStyles()  # Инициализация стилей

    def highlightBlock(self, text):
        """Переопределенный метод для подсветки текста"""
        # Применение регулярных выражений
        for pattern, fmt in self.styles.rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), fmt)

        # Подсветка блоков кода ```
        if '```' in text:
            self.setFormat(0, len(text), self.styles.code_block_format)
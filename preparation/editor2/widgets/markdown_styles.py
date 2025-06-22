from PySide6.QtGui import QTextCharFormat, QColor, QFont

class MarkdownStyles:
    """Класс для хранения стилей и правил подсветки Markdown"""

    def __init__(self):
        self.rules = []
        self._init_rules()
        self._init_code_block_format()

    def _init_rules(self):
        """Инициализация правил подсветки синтаксиса Markdown"""
        # Формат для заголовков (#, ## и т.д.)
        header_format = QTextCharFormat()
        header_format.setForeground(QColor("#0066cc"))
        header_format.setFontWeight(QFont.Bold)
        self.rules.append((r'^#{1,6}\s.*$', header_format))

        # Формат для жирного текста
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        self.rules.append((r'\*\*(.*?)\*\*', bold_format))
        self.rules.append((r'__(.*?)__', bold_format))

        # Формат для курсивного текста
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        self.rules.append((r'\*(.*?)\*', italic_format))
        self.rules.append((r'_(.*?)_', italic_format))

        # Формат для встроенного кода
        code_format = QTextCharFormat()
        code_format.setFontFamily("Courier")
        code_format.setBackground(QColor("#f0f0f0"))
        self.rules.append((r'`(.*?)`', code_format))

        # Формат для списков
        list_format = QTextCharFormat()
        list_format.setForeground(QColor("#993399"))
        self.rules.append((r'^[\*\-\+] .*$', list_format))
        self.rules.append((r'^\d+\. .*$', list_format))

        # Формат для ссылок
        link_format = QTextCharFormat()
        link_format.setForeground(QColor("#009900"))
        link_format.setFontUnderline(True)
        self.rules.append((r'\[.*?\]\(.*?\)', link_format))

        # Формат для горизонтальных линий
        line_format = QTextCharFormat()
        line_format.setForeground(QColor("#666666"))
        self.rules.append((r'^[-*_]{3,}$', line_format))

    def _init_code_block_format(self):
        """Инициализация формата для блоков кода"""
        self.code_block_format = QTextCharFormat()
        self.code_block_format.setFontFamily("Courier New")
        self.code_block_format.setBackground(QColor("#f5f5f5"))
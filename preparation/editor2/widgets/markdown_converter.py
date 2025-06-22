import re
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound


class MarkdownConverter:
    """Класс для конвертации Markdown в HTML с подсветкой синтаксиса"""

    @staticmethod
    def highlight_code(match):
        """Подсветка блоков кода с использованием Pygments"""
        language = match.group(1) or 'text'
        code = match.group(2)
        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except ClassNotFound:
            lexer = guess_lexer(code)
        formatter = HtmlFormatter(style='default', noclasses=True)
        return highlight(code, lexer, formatter)

    @classmethod
    def convert_md_to_html(cls, md_text):
        """Конвертирует Markdown в HTML с подсветкой синтаксиса"""
        # Обработка блоков кода ```lang ... ```
        html = re.sub(
            r'```(\w+)?\n(.*?)\n```',
            cls.highlight_code,
            md_text,
            flags=re.DOTALL
        )

        # Обработка остального Markdown
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        # ... остальные замены ...

        return f'<div class="markdown-content">{html}</div>'
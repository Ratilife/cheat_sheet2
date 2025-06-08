from PySide6.QtWidgets import QTextEdit, QApplication

class ClipboardManager:
    """
    Менеджер для работы с буфером обмена. Инкапсулирует операции:
    - Вырезание/копирование/вставка текста
    - Работает с любым QTextEdit или его наследниками
    """

    def __init__(self, text_editor: QTextEdit):
        """
        :param text_editor: Ссылка на текстовый редактор (QTextEdit/MarkdownViewer)
        """
        self.text_editor = text_editor

    def cut_text(self) -> None:
        """Вырезает выделенный текст в буфер обмена."""
        if self.text_editor:
            self.text_editor.cut()

    def copy_text(self) -> None:
        """Копирует выделенный текст в буфер обмена."""
        if self.text_editor:
            self.text_editor.copy()

    def paste_text(self) -> None:
        """Вставляет текст из буфера обмена."""
        if self.text_editor:
            self.text_editor.paste()

    @staticmethod
    def get_clipboard_text() -> str:
        """Возвращает текст из системного буфера обмена (статический метод)."""
        clipboard = QApplication.clipboard()
        return clipboard.text() if clipboard else ""

    @staticmethod
    def set_clipboard_text(text: str) -> None:
        """Устанавливает текст в системный буфер обмена (статический метод)."""
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)
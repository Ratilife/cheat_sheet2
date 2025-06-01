import os
# Импорт компонентов ANTLR
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
from antlr4.error.ErrorListener import ErrorListener
from preparation.editor.ANTLR4.st_Files.STFileLexer import STFileLexer
from preparation.editor.ANTLR4.st_Files.STFileParser import STFileParser
from preparation.editor.ANTLR4.st_Files.STFileListener import STFileListener
# ===================================================================
# КЛАССЫ ДЛЯ ПАРСИНГА ST-ФАЙЛОВ
# ===================================================================

class STFileParserWrapper:
    def parse_st_file(self, file_path):
        try:
            input_stream = FileStream(file_path, encoding="utf-8")
            lexer = STFileLexer(input_stream)
            tokens = CommonTokenStream(lexer)
            parser = STFileParser(tokens)

            # Устанавливаем обработчик ошибок
            parser.removeErrorListeners()
            parser.addErrorListener(ExceptionErrorListener())

            tree = parser.fileStructure()
            listener = StructureListener()
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            listener.root_name = file_name  # ИЗМЕНЕНИЕ: Имя файла в listener
            ParseTreeWalker().walk(listener, tree)

            return {
                'structure': listener.get_structure(),
                'root_name': listener.root_name
            }
        except Exception as e:
            # Возвращаем базовую структуру при ошибке парсинга
            return {
                'structure': [],
                'root_name': os.path.splitext(os.path.basename(file_path))[0]
            }

    # Добавляем методы в STFileParserWrapper:
    def remove_template(self, file_path, template_name):
        """Удаляет шаблон из ST файла."""
        structure = self.parse_st_file(file_path)
        if not structure:
            raise ValueError(f"Не удалось прочитать файл {file_path}")

        new_structure = self._remove_from_structure(
            structure,
            lambda x: not (x['type'] == 'template' and x['name'] == template_name)
        )
        self._save_structure(file_path, new_structure)

    def remove_folder(self, file_path, folder_name):
        """Удаляет папку из ST файла."""
        structure = self.parse_st_file(file_path)
        if not structure:
            raise ValueError(f"Не удалось прочитать файл {file_path}")

        new_structure = self._remove_from_structure(
            structure,
            lambda x: not (x['type'] == 'folder' and x['name'] == folder_name)
        )
        self._save_structure(file_path, new_structure)

    def _remove_from_structure(self, structure, filter_fn):
        """Рекурсивно фильтрует структуру."""
        structure['structure'] = [
            item for item in structure['structure']
            if filter_fn(item)
        ]
        for item in structure['structure']:
            if item['type'] == 'folder':
                item['children'] = self._remove_from_structure(item, filter_fn)
        return structure

    def _save_structure(self, file_path, structure):
        """Сохраняет измененную структуру."""
        content = self._generate_st_content(structure)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise IOError(f"Ошибка сохранения файла: {str(e)}")
class ExceptionErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Exception(f"Ошибка парсинга в строке {line}:{column} - {msg}")

class StructureListener(STFileListener):
    def __init__(self):
        self.stack = [{'children': []}]
        self.current_parent = self.stack[0]
        self.root_name = "Unnamed"
        self.found_root = False


    def get_structure(self):
        return self.stack[0]['children']


    def enterEntry(self, ctx):
        if ctx.folderHeader():
            # Обработка папки
            header = ctx.folderHeader()
            name = header.STRING(0).getText()[1:-1]

            new_item = {
                'name': name,
                'type': 'folder',
                'children': []
            }
            self.current_parent['children'].append(new_item)
            self.stack.append(new_item)
            self.current_parent = new_item



        elif ctx.templateHeader():
            # Обработка шаблона
            header = ctx.templateHeader()
            name = header.STRING(0).getText()[1:-1]
            content = header.STRING(2).getText()[1:-1] if len(header.STRING()) > 1 else ""
            self.current_parent['children'].append({
                'name': name,
                'type': 'template',
                'content': content
            })

    def exitEntry(self, ctx):
        if ctx.folderHeader() and len(self.stack) > 1:
            self.stack.pop()
            self.current_parent = self.stack[-1]


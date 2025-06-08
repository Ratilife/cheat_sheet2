import os

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


from antlr4 import Parser
from .CSharpParser import CSharpParser  # Импортируем CSharpParser для доступа к типам контекста

class CSharpParserBase(Parser):
    def __init__(self, input_stream, output=None, error_output=None):
        super().__init__(input_stream, output, error_output)

    def IsLocalVariableDeclaration(self):
        local_var_decl = self.getContext()
        if not isinstance(local_var_decl, CSharpParser.Local_variable_declarationContext):
            return True

        local_variable_type = local_var_decl.local_variable_type()
        if local_variable_type is None:
            return True

        return local_variable_type.getText() != "var"
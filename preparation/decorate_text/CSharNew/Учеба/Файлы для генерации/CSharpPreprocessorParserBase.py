from antlr4 import Parser

class CSharpPreprocessorParserBase(Parser):
    def __init__(self, input_stream, output=None, error_output=None):
        super().__init__(input_stream, output, error_output)
        self.conditions = [True]
        self.ConditionalSymbols = {"DEBUG"}

    def AllConditions(self):
        return all(self.conditions)

    def OnPreprocessorDirectiveDefine(self):
        d = self._ctx
        self.ConditionalSymbols.add(d.CONDITIONAL_SYMBOL().getText())
        d.value = self.AllConditions()

    def OnPreprocessorDirectiveUndef(self):
        d = self._ctx
        self.ConditionalSymbols.discard(d.CONDITIONAL_SYMBOL().getText())
        d.value = self.AllConditions()

    def OnPreprocessorDirectiveIf(self):
        d = self._ctx
        d.value = d.expr.value == "true" and self.AllConditions()
        self.conditions.append(d.expr.value == "true")

    def OnPreprocessorDirectiveElif(self):
        d = self._ctx
        if not self.conditions[-1]:
            self.conditions.pop()
            d.value = d.expr.value == "true" and self.AllConditions()
            self.conditions.append(d.expr.value == "true")
        else:
            d.value = False

    def OnPreprocessorDirectiveElse(self):
        d = self._ctx
        if not self.conditions[-1]:
            self.conditions.pop()
            d.value = True and self.AllConditions()
            self.conditions.append(True)
        else:
            d.value = False

    def OnPreprocessorDirectiveEndif(self):
        d = self._ctx
        self.conditions.pop()
        d.value = self.conditions[-1]

    def OnPreprocessorDirectiveLine(self):
        d = self._ctx
        d.value = self.AllConditions()

    def OnPreprocessorDirectiveError(self):
        d = self._ctx
        d.value = self.AllConditions()

    def OnPreprocessorDirectiveWarning(self):
        d = self._ctx
        d.value = self.AllConditions()

    def OnPreprocessorDirectiveRegion(self):
        d = self._ctx
        d.value = self.AllConditions()

    def OnPreprocessorDirectiveEndregion(self):
        d = self._ctx
        d.value = self.AllConditions()

    def OnPreprocessorDirectivePragma(self):
        d = self._ctx
        d.value = self.AllConditions()

    def OnPreprocessorDirectiveNullable(self):
        d = self._ctx
        d.value = self.AllConditions()

    def OnPreprocessorExpressionTrue(self):
        d = self._ctx
        d.value = "true"

    def OnPreprocessorExpressionFalse(self):
        d = self._ctx
        d.value = "false"

    def OnPreprocessorExpressionConditionalSymbol(self):
        d = self._ctx
        d.value = "true" if d.CONDITIONAL_SYMBOL().getText() in self.ConditionalSymbols else "false"

    def OnPreprocessorExpressionConditionalOpenParens(self):
        d = self._ctx
        d.value = d.expr.value

    def OnPreprocessorExpressionConditionalBang(self):
        d = self._ctx
        d.value = "false" if d.expr.value == "true" else "true"

    def OnPreprocessorExpressionConditionalEq(self):
        d = self._ctx
        d.value = "true" if d.expr1.value == d.expr2.value else "false"

    def OnPreprocessorExpressionConditionalNe(self):
        d = self._ctx
        d.value = "true" if d.expr1.value != d.expr2.value else "false"

    def OnPreprocessorExpressionConditionalAnd(self):
        d = self._ctx
        d.value = "true" if d.expr1.value == "true" and d.expr2.value == "true" else "false"

    def OnPreprocessorExpressionConditionalOr(self):
        d = self._ctx
        d.value = "true" if d.expr1.value == "true" or d.expr2.value == "true" else "false"

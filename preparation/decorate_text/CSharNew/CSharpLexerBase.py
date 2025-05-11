from antlr4 import Lexer
from collections import deque

class CSharpLexerBase(Lexer):
    def __init__(self, input_stream, output=None, error_output=None):
        #super().__init__(input_stream, output, error_output)
        super().__init__(input_stream, output,)
        self._input = input_stream
        self.interpolatedStringLevel = 0
        self.interpolatedVerbatiums = deque()
        self.curlyLevels = deque()
        self.verbatium = False

    def OnInterpolatedRegularStringStart(self):
        self.interpolatedStringLevel += 1
        self.interpolatedVerbatiums.append(False)
        self.verbatium = False

    def OnInterpolatedVerbatiumStringStart(self):
        self.interpolatedStringLevel += 1
        self.interpolatedVerbatiums.append(True)
        self.verbatium = True

    def OnOpenBrace(self):
        if self.interpolatedStringLevel > 0 and self.curlyLevels:
            self.curlyLevels.append(self.curlyLevels.pop() + 1)

    def OnCloseBrace(self):
        if self.interpolatedStringLevel > 0 and self.curlyLevels:
            self.curlyLevels.append(self.curlyLevels.pop() - 1)
            if self.curlyLevels[-1] == 0:
                self.curlyLevels.pop()
                self.skip()
                self.popMode()

    def OnColon(self):
        if self.interpolatedStringLevel > 0:
            ind = 1
            switchToFormatString = True
            while chr(self._input.LA(ind)) != '}':
                if self._input.LA(ind) in (ord(':'), ord(')')):
                    switchToFormatString = False
                    break
                ind += 1
            if switchToFormatString:
                self.mode(CSharpLexer.INTERPOLATION_FORMAT)

    def OpenBraceInside(self):
        self.curlyLevels.append(1)

    def OnDoubleQuoteInside(self):
        self.interpolatedStringLevel -= 1
        if self.interpolatedVerbatiums:
            self.interpolatedVerbatiums.pop()
        self.verbatium = self.interpolatedVerbatiums[-1] if self.interpolatedVerbatiums else False

    def OnCloseBraceInside(self):
        if self.curlyLevels:
            self.curlyLevels.pop()

    def IsRegularCharInside(self):
        return not self.verbatium

    def IsVerbatiumDoubleQuoteInside(self):
        return self.verbatium

# Generated from STFile.g4 by ANTLR 4.13.1
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,0,9,56,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,
        6,7,6,2,7,7,7,2,8,7,8,1,0,1,0,1,1,1,1,1,2,1,2,1,3,1,3,1,3,1,3,1,
        4,4,4,31,8,4,11,4,12,4,32,1,5,1,5,1,5,1,5,5,5,39,8,5,10,5,12,5,42,
        9,5,1,5,1,5,1,6,1,6,1,7,1,7,1,8,4,8,51,8,8,11,8,12,8,52,1,8,1,8,
        0,0,9,1,1,3,2,5,3,7,4,9,5,11,6,13,7,15,8,17,9,1,0,3,2,0,48,57,65296,
        65305,1,0,34,34,3,0,9,10,13,13,32,32,59,0,1,1,0,0,0,0,3,1,0,0,0,
        0,5,1,0,0,0,0,7,1,0,0,0,0,9,1,0,0,0,0,11,1,0,0,0,0,13,1,0,0,0,0,
        15,1,0,0,0,0,17,1,0,0,0,1,19,1,0,0,0,3,21,1,0,0,0,5,23,1,0,0,0,7,
        25,1,0,0,0,9,30,1,0,0,0,11,34,1,0,0,0,13,45,1,0,0,0,15,47,1,0,0,
        0,17,50,1,0,0,0,19,20,5,44,0,0,20,2,1,0,0,0,21,22,5,48,0,0,22,4,
        1,0,0,0,23,24,5,49,0,0,24,6,1,0,0,0,25,26,5,65279,0,0,26,27,1,0,
        0,0,27,28,6,3,0,0,28,8,1,0,0,0,29,31,7,0,0,0,30,29,1,0,0,0,31,32,
        1,0,0,0,32,30,1,0,0,0,32,33,1,0,0,0,33,10,1,0,0,0,34,40,5,34,0,0,
        35,36,5,34,0,0,36,39,5,34,0,0,37,39,8,1,0,0,38,35,1,0,0,0,38,37,
        1,0,0,0,39,42,1,0,0,0,40,38,1,0,0,0,40,41,1,0,0,0,41,43,1,0,0,0,
        42,40,1,0,0,0,43,44,5,34,0,0,44,12,1,0,0,0,45,46,5,123,0,0,46,14,
        1,0,0,0,47,48,5,125,0,0,48,16,1,0,0,0,49,51,7,2,0,0,50,49,1,0,0,
        0,51,52,1,0,0,0,52,50,1,0,0,0,52,53,1,0,0,0,53,54,1,0,0,0,54,55,
        6,8,0,0,55,18,1,0,0,0,5,0,32,38,40,52,1,6,0,0
    ]

class STFileLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    BOM = 4
    INT = 5
    STRING = 6
    LBRACE = 7
    RBRACE = 8
    WS = 9

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "','", "'0'", "'1'", "'\\uFEFF'", "'{'", "'}'" ]

    symbolicNames = [ "<INVALID>",
            "BOM", "INT", "STRING", "LBRACE", "RBRACE", "WS" ]

    ruleNames = [ "T__0", "T__1", "T__2", "BOM", "INT", "STRING", "LBRACE", 
                  "RBRACE", "WS" ]

    grammarFileName = "STFile.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None



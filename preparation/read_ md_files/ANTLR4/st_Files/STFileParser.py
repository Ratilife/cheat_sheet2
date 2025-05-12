# Generated from STFile.g4 by ANTLR 4.13.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,9,95,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,6,
        2,7,7,7,1,0,1,0,1,0,1,0,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,
        1,2,5,2,32,8,2,10,2,12,2,35,9,2,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,
        1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,1,3,3,3,57,8,3,1,4,1,
        4,1,4,5,4,62,8,4,10,4,12,4,65,9,4,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,
        5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,
        6,1,7,1,7,3,7,93,8,7,1,7,0,0,8,0,2,4,6,8,10,12,14,0,1,1,0,2,3,91,
        0,16,1,0,0,0,2,22,1,0,0,0,4,28,1,0,0,0,6,56,1,0,0,0,8,58,1,0,0,0,
        10,66,1,0,0,0,12,78,1,0,0,0,14,92,1,0,0,0,16,17,5,7,0,0,17,18,3,
        14,7,0,18,19,5,1,0,0,19,20,3,2,1,0,20,21,5,8,0,0,21,1,1,0,0,0,22,
        23,5,7,0,0,23,24,3,14,7,0,24,25,5,1,0,0,25,26,3,4,2,0,26,27,5,8,
        0,0,27,3,1,0,0,0,28,33,3,10,5,0,29,30,5,1,0,0,30,32,3,6,3,0,31,29,
        1,0,0,0,32,35,1,0,0,0,33,31,1,0,0,0,33,34,1,0,0,0,34,5,1,0,0,0,35,
        33,1,0,0,0,36,37,5,7,0,0,37,38,3,14,7,0,38,39,5,1,0,0,39,40,3,10,
        5,0,40,41,5,1,0,0,41,42,3,8,4,0,42,43,5,8,0,0,43,57,1,0,0,0,44,45,
        5,7,0,0,45,46,3,14,7,0,46,47,5,1,0,0,47,48,3,10,5,0,48,49,5,8,0,
        0,49,57,1,0,0,0,50,51,5,7,0,0,51,52,5,2,0,0,52,53,5,1,0,0,53,54,
        3,12,6,0,54,55,5,8,0,0,55,57,1,0,0,0,56,36,1,0,0,0,56,44,1,0,0,0,
        56,50,1,0,0,0,57,7,1,0,0,0,58,63,3,6,3,0,59,60,5,1,0,0,60,62,3,6,
        3,0,61,59,1,0,0,0,62,65,1,0,0,0,63,61,1,0,0,0,63,64,1,0,0,0,64,9,
        1,0,0,0,65,63,1,0,0,0,66,67,5,7,0,0,67,68,5,6,0,0,68,69,5,1,0,0,
        69,70,5,3,0,0,70,71,5,1,0,0,71,72,7,0,0,0,72,73,5,1,0,0,73,74,5,
        6,0,0,74,75,5,1,0,0,75,76,5,6,0,0,76,77,5,8,0,0,77,11,1,0,0,0,78,
        79,5,7,0,0,79,80,5,6,0,0,80,81,5,1,0,0,81,82,5,2,0,0,82,83,5,1,0,
        0,83,84,7,0,0,0,84,85,5,1,0,0,85,86,5,6,0,0,86,87,5,1,0,0,87,88,
        5,6,0,0,88,89,5,8,0,0,89,13,1,0,0,0,90,93,5,5,0,0,91,93,7,0,0,0,
        92,90,1,0,0,0,92,91,1,0,0,0,93,15,1,0,0,0,4,33,56,63,92
    ]

class STFileParser ( Parser ):

    grammarFileName = "STFile.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "','", "'0'", "'1'", "'\\uFEFF'", "<INVALID>", 
                     "<INVALID>", "'{'", "'}'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "BOM", "INT", "STRING", "LBRACE", "RBRACE", "WS" ]

    RULE_fileStructure = 0
    RULE_rootContent = 1
    RULE_folderContent = 2
    RULE_entry = 3
    RULE_entryList = 4
    RULE_folderHeader = 5
    RULE_templateHeader = 6
    RULE_int_value = 7

    ruleNames =  [ "fileStructure", "rootContent", "folderContent", "entry", 
                   "entryList", "folderHeader", "templateHeader", "int_value" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    BOM=4
    INT=5
    STRING=6
    LBRACE=7
    RBRACE=8
    WS=9

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class FileStructureContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(STFileParser.LBRACE, 0)

        def int_value(self):
            return self.getTypedRuleContext(STFileParser.Int_valueContext,0)


        def rootContent(self):
            return self.getTypedRuleContext(STFileParser.RootContentContext,0)


        def RBRACE(self):
            return self.getToken(STFileParser.RBRACE, 0)

        def getRuleIndex(self):
            return STFileParser.RULE_fileStructure

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFileStructure" ):
                listener.enterFileStructure(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFileStructure" ):
                listener.exitFileStructure(self)




    def fileStructure(self):

        localctx = STFileParser.FileStructureContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_fileStructure)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self.match(STFileParser.LBRACE)
            self.state = 17
            self.int_value()
            self.state = 18
            self.match(STFileParser.T__0)
            self.state = 19
            self.rootContent()
            self.state = 20
            self.match(STFileParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RootContentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(STFileParser.LBRACE, 0)

        def int_value(self):
            return self.getTypedRuleContext(STFileParser.Int_valueContext,0)


        def folderContent(self):
            return self.getTypedRuleContext(STFileParser.FolderContentContext,0)


        def RBRACE(self):
            return self.getToken(STFileParser.RBRACE, 0)

        def getRuleIndex(self):
            return STFileParser.RULE_rootContent

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRootContent" ):
                listener.enterRootContent(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRootContent" ):
                listener.exitRootContent(self)




    def rootContent(self):

        localctx = STFileParser.RootContentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_rootContent)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 22
            self.match(STFileParser.LBRACE)
            self.state = 23
            self.int_value()
            self.state = 24
            self.match(STFileParser.T__0)
            self.state = 25
            self.folderContent()
            self.state = 26
            self.match(STFileParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FolderContentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def folderHeader(self):
            return self.getTypedRuleContext(STFileParser.FolderHeaderContext,0)


        def entry(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(STFileParser.EntryContext)
            else:
                return self.getTypedRuleContext(STFileParser.EntryContext,i)


        def getRuleIndex(self):
            return STFileParser.RULE_folderContent

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFolderContent" ):
                listener.enterFolderContent(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFolderContent" ):
                listener.exitFolderContent(self)




    def folderContent(self):

        localctx = STFileParser.FolderContentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_folderContent)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            self.folderHeader()
            self.state = 33
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 29
                self.match(STFileParser.T__0)
                self.state = 30
                self.entry()
                self.state = 35
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EntryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(STFileParser.LBRACE, 0)

        def int_value(self):
            return self.getTypedRuleContext(STFileParser.Int_valueContext,0)


        def folderHeader(self):
            return self.getTypedRuleContext(STFileParser.FolderHeaderContext,0)


        def entryList(self):
            return self.getTypedRuleContext(STFileParser.EntryListContext,0)


        def RBRACE(self):
            return self.getToken(STFileParser.RBRACE, 0)

        def templateHeader(self):
            return self.getTypedRuleContext(STFileParser.TemplateHeaderContext,0)


        def getRuleIndex(self):
            return STFileParser.RULE_entry

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEntry" ):
                listener.enterEntry(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEntry" ):
                listener.exitEntry(self)




    def entry(self):

        localctx = STFileParser.EntryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_entry)
        try:
            self.state = 56
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 36
                self.match(STFileParser.LBRACE)
                self.state = 37
                self.int_value()
                self.state = 38
                self.match(STFileParser.T__0)
                self.state = 39
                self.folderHeader()
                self.state = 40
                self.match(STFileParser.T__0)
                self.state = 41
                self.entryList()
                self.state = 42
                self.match(STFileParser.RBRACE)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 44
                self.match(STFileParser.LBRACE)
                self.state = 45
                self.int_value()
                self.state = 46
                self.match(STFileParser.T__0)
                self.state = 47
                self.folderHeader()
                self.state = 48
                self.match(STFileParser.RBRACE)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 50
                self.match(STFileParser.LBRACE)
                self.state = 51
                self.match(STFileParser.T__1)
                self.state = 52
                self.match(STFileParser.T__0)
                self.state = 53
                self.templateHeader()
                self.state = 54
                self.match(STFileParser.RBRACE)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EntryListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def entry(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(STFileParser.EntryContext)
            else:
                return self.getTypedRuleContext(STFileParser.EntryContext,i)


        def getRuleIndex(self):
            return STFileParser.RULE_entryList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEntryList" ):
                listener.enterEntryList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEntryList" ):
                listener.exitEntryList(self)




    def entryList(self):

        localctx = STFileParser.EntryListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_entryList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 58
            self.entry()
            self.state = 63
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 59
                self.match(STFileParser.T__0)
                self.state = 60
                self.entry()
                self.state = 65
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FolderHeaderContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(STFileParser.LBRACE, 0)

        def STRING(self, i:int=None):
            if i is None:
                return self.getTokens(STFileParser.STRING)
            else:
                return self.getToken(STFileParser.STRING, i)

        def RBRACE(self):
            return self.getToken(STFileParser.RBRACE, 0)

        def getRuleIndex(self):
            return STFileParser.RULE_folderHeader

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFolderHeader" ):
                listener.enterFolderHeader(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFolderHeader" ):
                listener.exitFolderHeader(self)




    def folderHeader(self):

        localctx = STFileParser.FolderHeaderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_folderHeader)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.match(STFileParser.LBRACE)
            self.state = 67
            self.match(STFileParser.STRING)
            self.state = 68
            self.match(STFileParser.T__0)
            self.state = 69
            self.match(STFileParser.T__2)
            self.state = 70
            self.match(STFileParser.T__0)
            self.state = 71
            _la = self._input.LA(1)
            if not(_la==2 or _la==3):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 72
            self.match(STFileParser.T__0)
            self.state = 73
            self.match(STFileParser.STRING)
            self.state = 74
            self.match(STFileParser.T__0)
            self.state = 75
            self.match(STFileParser.STRING)
            self.state = 76
            self.match(STFileParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TemplateHeaderContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(STFileParser.LBRACE, 0)

        def STRING(self, i:int=None):
            if i is None:
                return self.getTokens(STFileParser.STRING)
            else:
                return self.getToken(STFileParser.STRING, i)

        def RBRACE(self):
            return self.getToken(STFileParser.RBRACE, 0)

        def getRuleIndex(self):
            return STFileParser.RULE_templateHeader

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTemplateHeader" ):
                listener.enterTemplateHeader(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTemplateHeader" ):
                listener.exitTemplateHeader(self)




    def templateHeader(self):

        localctx = STFileParser.TemplateHeaderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_templateHeader)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.match(STFileParser.LBRACE)
            self.state = 79
            self.match(STFileParser.STRING)
            self.state = 80
            self.match(STFileParser.T__0)
            self.state = 81
            self.match(STFileParser.T__1)
            self.state = 82
            self.match(STFileParser.T__0)
            self.state = 83
            _la = self._input.LA(1)
            if not(_la==2 or _la==3):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 84
            self.match(STFileParser.T__0)
            self.state = 85
            self.match(STFileParser.STRING)
            self.state = 86
            self.match(STFileParser.T__0)
            self.state = 87
            self.match(STFileParser.STRING)
            self.state = 88
            self.match(STFileParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Int_valueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(STFileParser.INT, 0)

        def getRuleIndex(self):
            return STFileParser.RULE_int_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInt_value" ):
                listener.enterInt_value(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInt_value" ):
                listener.exitInt_value(self)




    def int_value(self):

        localctx = STFileParser.Int_valueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_int_value)
        self._la = 0 # Token type
        try:
            self.state = 92
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [5]:
                self.enterOuterAlt(localctx, 1)
                self.state = 90
                self.match(STFileParser.INT)
                pass
            elif token in [2, 3]:
                self.enterOuterAlt(localctx, 2)
                self.state = 91
                _la = self._input.LA(1)
                if not(_la==2 or _la==3):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx






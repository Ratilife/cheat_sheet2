grammar STFile;

BOM: '\uFEFF' -> skip;

fileStructure: LBRACE int_value ',' rootContent RBRACE;

rootContent: LBRACE int_value ',' folderContent RBRACE;

folderContent: entry (',' entry)*;

entry:
    LBRACE int_value ',' folderHeader (',' entryList)? RBRACE
    |
    LBRACE '0' ',' templateHeader RBRACE
;

entryList: entry (',' entry)*;

folderHeader:
    LBRACE
    STRING ',' 
    INT ','      // type (1 для папки)
    INT ','      // flags (0 или 1)
    STRING ','   // описание
    STRING       // комментарий
    RBRACE
;

templateHeader:
    LBRACE
    STRING ','   // имя шаблона
    '0' ','      // type (0 для шаблона)
    INT ','      // flags (0 или 1)
    STRING ','   // тип шаблона
    STRING       // содержимое
    RBRACE
;

int_value: INT | ('0' | '1');
INT: [0-9\uFF10-\uFF19]+;
STRING: '"' ('""' | ~["])* '"';
LBRACE: '{';
RBRACE: '}';
WS: [ \t\r\n]+ -> skip;
grammar STFile;

BOM: '\uFEFF' -> skip;

fileStructure: LBRACE int_value ',' rootContent RBRACE;

rootContent: LBRACE int_value ',' folderContent RBRACE;


//folderContent: 
//    folderHeader ',' entriesBlock 
//    | folderHeader (',' entry)* 
//;

//entriesBlock: LBRACE (entry (',' entry)*)? RBRACE;
folderContent: folderHeader (',' entry)*;

entry:
// Папка: {count, header, вложенные_элементы}
                // что бы незабыть LBRACE int_value ',' folderHeader ','(entriesBlock |entry (','  entry)*) RBRACE
LBRACE int_value ',' folderHeader ',' entryList RBRACE
|
// Пустая папка
LBRACE int_value ',' folderHeader RBRACE
|
// Шаблон: {0, header}
LBRACE '0' ',' templateHeader RBRACE
;

entryList: entry (',' entry)*;

folderHeader:
    LBRACE
    STRING ',' 
    '1' ','    // type (строго 1)
    ('0' | '1')  ','    // flags (0 или 1)
    STRING ',' 
    STRING
    RBRACE
;

templateHeader:
    LBRACE
    STRING ',' 
    '0' ','     // type (строго 0)
    ('0' | '1') ',' // flags (0 или 1)
    STRING ',' 
    STRING
    RBRACE
;
int_value: INT | ('0' | '1');  // Разрешаем как INT, так и явное '1'
INT: [0-9\uFF10-\uFF19]+;   
STRING: '"' ('""' | ~["])* '"';
LBRACE: '{';
RBRACE: '}';
WS: [ \t\r\n]+ -> skip;
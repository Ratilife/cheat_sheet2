lexer grammar CSharpPreprocessorLexer;

// Определение токенов
WS      : [ \t\r\n]+ -> skip; // Пропускаем пробелы
NEWLINE : [\r\n]+;

# Директивы препроцессора
# Пример: #define, #undef, #if, #else, #elif, #endif
DEFINE  : '#' 'define' ;
UNDEF   : '#' 'undef' ;
IF      : '#' 'if' ;
ELSE    : '#' 'else' ;
ELIF    : '#' 'elif' ;
ENDIF   : '#' 'endif' ;

// Определите другие токены по мере необходимости
ID      : [a-zA-Z_][a-zA-Z0-9_]*; // Идентификаторы
STRING  : '"' ( ~["\\] | '\\' . )* '"'; // Строки

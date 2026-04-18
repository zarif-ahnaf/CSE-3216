%{
#include "parser.tab.h"
%}

%%

[0-9]+      { yylval = atoi(yytext); return NUMBER; }
"+"         { return PLUS; }
"-"         { return MINUS; }
"*"         { return TIMES; }
"/"         { return DIVIDE; }
[ \t]       { /* ignore whitespace */ }
\n          { return NEWLINE; }
.           { printf("Unknown character: %s\n", yytext); }

%%

int yywrap() { return 1; }
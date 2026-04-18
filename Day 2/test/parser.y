%{
#include <stdio.h>
#include <stdlib.h>

void yyerror(const char *s);
int yylex();
%}

%token NUMBER PLUS MINUS TIMES DIVIDE NEWLINE

%%

calculation:
    | calculation line
    ;

line:
    NEWLINE
    | expression NEWLINE { printf("Result: %d\n", $1); }
    ;

expression:
    NUMBER                  { $$ = $1; }
    | expression PLUS expression    { $$ = $1 + $3; }
    | expression MINUS expression   { $$ = $1 - $3; }
    | expression TIMES expression   { $$ = $1 * $3; }
    | expression DIVIDE expression  { 
        if ($3 == 0) yyerror("Division by zero");
        else $$ = $1 / $3; 
    }
    ;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Error: %s\n", s);
}

int main() {
    return yyparse();
}
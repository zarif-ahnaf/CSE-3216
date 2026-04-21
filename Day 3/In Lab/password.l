%{
#include <stdio.h>
#include <string.h>
#include <locale.h>

int has_upper = 0;
int has_lower = 0;
int has_digit = 0;
int has_special = 0;
int length = 0;

void check_password();
%}

%%

[A-Z]        { has_upper = 1; length++; }
[a-z]        { has_lower = 1; length++; }
[0-9]        { has_digit = 1; length++; }
[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]  { has_special = 1; length++; }

\n           { check_password(); }

.            { length++; }

%%

void check_password() {
    printf("\n--- Password Analysis ---\n");

    if (has_upper) printf("Has Uppercase\n");
    else printf("Missing Uppercase\n");

    if (has_lower) printf("Has Lowercase\n");
    else printf("Missing Lowercase\n");

    if (has_digit) printf("Has Digit\n");
    else printf("Missing Digit\n");

    if (has_special) printf("Has Special Character\n");
    else printf("Missing Special Character\n");

    printf("Length: %d\n", length);

    if (has_upper && has_lower && has_digit && has_special && length >= 8)
        printf("Strong Password\n");
    else
        printf("Weak Password\n");

    // reset for next input
    has_upper = has_lower = has_digit = has_special = length = 0;
}

int main() {
    setlocale(LC_ALL, "");
    printf("Enter password:\n");
    yylex();
    return 0;
}
int yywrap() {
    return 1;
}
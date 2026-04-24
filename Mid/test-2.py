def cyk(grammar, start, s):
    n = len(s)
    table = [[set() for _ in range(n + 1)] for _ in range(n)]

    for i in range(n):
        for A, productions in grammar.items():
            for p in productions:
                if p == s[i]:
                    table[i][1].add(A)
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            for k in range(1, length):
                left = table[i][k]
                right = table[i + k][length - k]
                for A, productions in grammar.items():
                    for p in productions:
                        if len(p) == 2:
                            B, C = p
                            if B in left and C in right:
                                table[i][length].add(A)

    return start in table[0][n]


grammar = {
    "S": ["AB"],
    "A": ["a"],
    "B": ["b"],
}

print(cyk(grammar, "S", "ab"))  # True
print(cyk(grammar, "S", "aa"))  # False

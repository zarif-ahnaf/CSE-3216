from collections import defaultdict


def to_cnf(grammar):
    cnf = defaultdict(set)
    term_map = {}
    counter = 0

    # 1. Identify Nullable Symbols (symbols that can derive ϵ)
    nullable = set()
    if any("ϵ" in prods for prods in grammar.values()):
        # Simple check for direct epsilon
        for nt, prods in grammar.items():
            if "ϵ" in prods:
                nullable.add(nt)

    def get_term(t):
        nonlocal counter
        if t not in term_map:
            var = f"T{counter}"
            counter += 1
            term_map[t] = var
            cnf[var].add(t)
        return term_map[t]

    # 2. Process rules and handle the "Nullable" expansion
    for A, prods in grammar.items():
        for p in prods:
            if p == "ϵ":
                continue

            # Create variations for nullable symbols (e.g., (S) becomes (S) AND ())
            variations = [p]
            if any(char in nullable for char in p):
                for char in p:
                    if char in nullable:
                        # This is a simple version: replace nullable char with empty
                        variations.append(p.replace(char, ""))

            for var_p in set(variations):
                if not var_p:
                    continue

                # Convert string to list of symbols (mix of terminals and non-terminals)
                symbols = []
                for ch in var_p:
                    if not ch.isupper():  # Terminal
                        symbols.append(get_term(ch))
                    else:
                        symbols.append(ch)

                # 3. Binary Split logic (Breaking down A -> B C D into A -> B X, X -> C D)
                if len(symbols) == 1:
                    cnf[A].add(symbols[0])
                else:
                    curr = A
                    while len(symbols) > 2:
                        new_var = f"X{counter}"
                        counter += 1
                        cnf[curr].add((symbols[0], new_var))
                        curr = new_var
                        symbols.pop(0)
                    cnf[curr].add(tuple(symbols))

    return dict(cnf), "ϵ" in grammar.get("S", [])


def cyk(grammar, start, s, has_epsilon=False):
    n = len(s)
    if n == 0:
        return has_epsilon

    # table[length][start_pos]
    table = [[set() for _ in range(n)] for _ in range(n + 1)]

    for i in range(n):
        for A, prods in grammar.items():
            if s[i] in prods:
                table[1][i].add(A)

    # Standard CYK DP
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            for k in range(1, length):
                for A, prods in grammar.items():
                    for p in prods:
                        if isinstance(p, tuple):
                            B, C = p
                            if B in table[k][i] and C in table[length - k][i + k]:
                                table[length][i].add(A)

    return start in table[n][0]


# --- Test ---
grammar = {
    "E": ["E+T", "T"],
    "T": ["T*F", "F"],
    "F": ["(E)", "id"],
}
cnf_grammar, has_epsilon = to_cnf(grammar)

print(f"Result for '()(())': {cyk(cnf_grammar, 'E', 'id+id*id', has_epsilon)}")

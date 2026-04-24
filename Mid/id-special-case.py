from collections import defaultdict


def to_cnf(grammar):
    cnf = defaultdict(set)
    term_map = {}
    counter = 0

    # 1. Identify Nullable Symbols (for epsilon expansion)
    nullable = set()
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

    for A, prods in grammar.items():
        for p in prods:
            if p == "ϵ":
                continue

            # Handle Nullable expansion (e.g., S -> (S) also adds S -> ())
            variations = [p]
            for nt in nullable:
                if nt in p:
                    # Very basic expansion: replace first occurrence
                    variations.append(p.replace(nt, ""))

            for var_p in set(variations):
                if not var_p:
                    continue

                # Tokenize: Split multi-char terminals or use specific identifiers
                # For this logic, we assume non-terminals are SINGLE uppercase letters
                symbols = []
                i = 0
                while i < len(var_p):
                    if var_p[i].isupper():
                        symbols.append(var_p[i])
                        i += 1
                    elif var_p[i : i + 2] == "id":  # Handle 'id' as a special token
                        symbols.append(get_term("id"))
                        i += 2
                    else:
                        symbols.append(get_term(var_p[i]))
                        i += 1

                # 3. Binary Split Logic
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


def cyk(grammar, start, input_str, has_epsilon=False):
    # Tokenizer for the input string
    tokens = []
    i = 0
    while i < len(input_str):
        if input_str[i : i + 2] == "id":
            tokens.append("id")
            i += 2
        else:
            tokens.append(input_str[i])
            i += 1

    n = len(tokens)
    if n == 0:
        return has_epsilon

    table = [[set() for _ in range(n)] for _ in range(n + 1)]

    # BASE CASE: Fill Length 1 & Resolve Unit Productions (A -> B)
    for i in range(n):
        # 1. Direct Terminal Match
        for A, prods in grammar.items():
            if tokens[i] in prods:
                table[1][i].add(A)

        # 2. Unit Production Pull-up (Crucial for E -> T -> F -> id)
        added = True
        while added:
            added = False
            for A, prods in grammar.items():
                for p in prods:
                    if isinstance(p, str) and p in table[1][i] and A not in table[1][i]:
                        table[1][i].add(A)
                        added = True

    # DP: Fill Length 2 to N
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


# --- Execution ---
arithmetic_grammar = {
    "E": ["E+T", "T"],
    "T": ["T*F", "F"],
    "F": ["(E)", "id"],
}

# 1. Convert to CNF
cnf_grammar, has_eps = to_cnf(arithmetic_grammar)

# 2. Test Cases
print(f"id+id*id: {cyk(cnf_grammar, 'E', 'id+id*id', has_eps)}")  # True
print(f"(id+id)*id: {cyk(cnf_grammar, 'E', '(id+id)*id', has_eps)}")  # True
print(f"id+: {cyk(cnf_grammar, 'E', 'id+', has_eps)}")  # False

# 3. Test original balanced grammar
balanced_grammar = {"S": ["(S)", "ϵ", "SS"]}
cnf_bal, has_eps_bal = to_cnf(balanced_grammar)
print(f"()(()): {cyk(cnf_bal, 'S', '()(())', has_eps_bal)}")  # True

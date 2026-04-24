from collections import defaultdict


def to_cnf(grammar):
    """
    Simplifies a grammar into CNF.
    Note: This is a simplified version focusing on terminal mapping and binary splitting.
    """
    cnf = defaultdict(set)
    term_map = {}
    counter = 0

    # 1. Handle Terminals: Replace terminals in complex rules with new non-terminals
    temp_grammar = defaultdict(set)
    non_terminals = set(grammar.keys())

    def get_term_var(t):
        nonlocal counter
        if t not in term_map:
            var = f"T_{t.strip('()')}_{counter}"  # Unique name
            counter += 1
            term_map[t] = var
            cnf[var].add(t)
        return term_map[t]

    for A, prods in grammar.items():
        for p in prods:
            tokens = p.split()
            if len(tokens) == 1 and tokens[0] not in non_terminals:
                temp_grammar[A].add(tokens[0])  # Pure terminal rule
            else:
                new_prod = []
                for tok in tokens:
                    if tok not in non_terminals:
                        new_prod.append(get_term_var(tok))
                    else:
                        new_prod.append(tok)
                temp_grammar[A].add(tuple(new_prod))

    # 2. Binary Splitting: Break rules with > 2 non-terminals
    final_grammar = defaultdict(set)
    for A, prods in temp_grammar.items():
        for p in prods:
            if isinstance(p, str):
                final_grammar[A].add(p)
                continue

            symbols = list(p)
            curr_A = A
            while len(symbols) > 2:
                new_var = f"X{counter}"
                counter += 1
                first = symbols.pop(0)
                final_grammar[curr_A].add((first, new_var))
                curr_A = new_var

            if len(symbols) == 2:
                final_grammar[curr_A].add(tuple(symbols))
            else:
                final_grammar[curr_A].add(symbols[0])

    # Add the terminal mappings created in step 1
    for var, t_set in cnf.items():
        final_grammar[var].update(t_set)

    return dict(final_grammar)


def remove_unit_productions(grammar):
    """Eliminates rules of type A -> B"""
    new_grammar = defaultdict(set)
    non_terminals = set(grammar.keys())

    def get_all_derivations(A, visited):
        derivs = set()
        if A not in grammar:
            return derivs
        for p in grammar[A]:
            if isinstance(p, str) and p in non_terminals:
                if p not in visited:
                    visited.add(p)
                    derivs.update(get_all_derivations(p, visited))
            else:
                derivs.add(p)
        return derivs

    for A in grammar:
        new_grammar[A] = get_all_derivations(A, {A})
    return dict(new_grammar)


def cyk(grammar, start, s):
    tokens = s.split()
    n = len(tokens)
    if n == 0:
        return False  # Simplified epsilon check

    # Table[length][start_pos]
    table = [[set() for _ in range(n)] for _ in range(n)]

    # Base case: length 1
    for i, word in enumerate(tokens):
        for A, prods in grammar.items():
            if word in prods:
                table[0][i].add(A)

    # DP for lengths 2 to n
    for length in range(2, n + 1):
        for i in range(n - length + 1):  # Start position
            for k in range(1, length):  # Split point
                # Check A -> BC where B is in left part, C in right
                left_cell = table[k - 1][i]
                right_cell = table[length - k - 1][i + k]

                for A, prods in grammar.items():
                    for p in prods:
                        if isinstance(p, tuple) and len(p) == 2:
                            B, C = p
                            if B in left_cell and C in right_cell:
                                table[length - 1][i].add(A)

    return start in table[n - 1][0]


# --- Test Execution ---
arithmetic_grammar = {
    "E": ["E + T", "T"],
    "T": ["T * F", "F"],
    "F": ["( E )", "id"],
}

# Process Grammar
step1 = to_cnf(arithmetic_grammar)
cnf_grammar = remove_unit_productions(step1)

# Test Cases
print(f"id + id * id:    {cyk(cnf_grammar, 'E', 'id + id * id')}")  # True
print(f"( id + id ) * id: {cyk(cnf_grammar, 'E', '( id + id ) * id')}")  # True
print(f"id + :           {cyk(cnf_grammar, 'E', 'id +')}")  # False

# Edge Case 2 ( Azim's Fucked up Strings )
from collections import defaultdict
import itertools


def remove_epsilon(grammar):
    nullable = set()

    # 1. Direct nullable
    for A, prods in grammar.items():
        if "ε" in prods or "" in prods:
            nullable.add(A)

    # 2. Indirect nullable
    changed = True
    while changed:
        changed = False
        for A, prods in grammar.items():
            if A not in nullable:
                for p in prods:
                    tokens = p.split()
                    if tokens and all(t in nullable for t in tokens):
                        nullable.add(A)
                        changed = True

    # 3. Generate new productions
    new_grammar = defaultdict(set)

    for A, prods in grammar.items():
        for p in prods:
            tokens = p.split()

            if not tokens or tokens == ["ε"]:
                continue

            positions = [i for i, t in enumerate(tokens) if t in nullable]

            for r in range(len(positions) + 1):
                for combo in itertools.combinations(positions, r):
                    new_p = [t for i, t in enumerate(tokens) if i not in combo]
                    if new_p:
                        new_grammar[A].add(" ".join(new_p))

    return dict(new_grammar), nullable


def to_cnf_and_unit(grammar):
    cnf = defaultdict(set)
    term_map = {}
    counter = 0
    non_terminals = set(grammar.keys())

    # Step 1: Replace terminals in long productions
    temp_grammar = defaultdict(set)

    for A, prods in grammar.items():
        for p in prods:
            tokens = p.split()

            if len(tokens) == 1:
                temp_grammar[A].add(tokens[0])
            else:
                new_p = []
                for t in tokens:
                    if t not in non_terminals:
                        if t not in term_map:
                            var = f"T{counter}"
                            counter += 1
                            term_map[t] = var
                            cnf[var].add(t)
                        new_p.append(term_map[t])
                    else:
                        new_p.append(t)

                temp_grammar[A].add(tuple(new_p))

    # Step 2: Binary splitting
    split_grammar = defaultdict(set)

    for A, prods in temp_grammar.items():
        for p in prods:
            if isinstance(p, str):
                split_grammar[A].add(p)
            else:
                curr = list(p)
                lhs = A

                while len(curr) > 2:
                    new_var = f"X{counter}"
                    counter += 1
                    split_grammar[lhs].add((curr[0], new_var))
                    lhs = new_var
                    curr.pop(0)

                split_grammar[lhs].add(tuple(curr))

    # Add terminal mappings
    for k, v in cnf.items():
        split_grammar[k].update(v)

    # Step 3: Remove unit productions
    final_grammar = defaultdict(set)

    def get_derivs(A, visited):
        res = set()
        for p in split_grammar.get(A, []):
            if isinstance(p, str) and p in split_grammar:
                if p not in visited:
                    res.update(get_derivs(p, visited | {p}))
            else:
                res.add(p)
        return res

    for A in split_grammar:
        final_grammar[A] = get_derivs(A, {A})

    return dict(final_grammar)


def cyk(grammar, start, s, start_is_nullable):
    if s.strip() == "ε":
        s = ""

    tokens = list(s.replace(" ", ""))
    n = len(tokens)

    if n == 0:
        return start_is_nullable

    term_to_vars = defaultdict(set)
    for A, prods in grammar.items():
        for p in prods:
            if isinstance(p, str):
                term_to_vars[p].add(A)

    table = [[set() for _ in range(n)] for _ in range(n)]

    for i, word in enumerate(tokens):
        table[0][i] = set(term_to_vars[word])

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            for k in range(1, length):
                left = table[k - 1][i]
                right = table[length - k - 1][i + k]

                for A, prods in grammar.items():
                    for p in prods:
                        if isinstance(p, tuple) and p[0] in left and p[1] in right:
                            table[length - 1][i].add(A)

    return start in table[n - 1][0]


raw_grammar = {"S": ["( S )", "S S", "ε"]}

# Preprocess
no_eps, nullables = remove_epsilon(raw_grammar)
cnf_final = to_cnf_and_unit(no_eps)
start_nullable = "S" in nullables

# VALID tests for this grammar
tests = ["ε", "( )", "( ( ) )", "( ) ( )", "( ( ) ( ) )"]

for t in tests:
    res = cyk(cnf_final, "S", t, start_nullable)
    print(f"Input: '{t}' -> Valid: {res}")

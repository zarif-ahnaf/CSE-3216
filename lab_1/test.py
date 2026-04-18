import re


def parse_grammar(lines):
    grammar = {}
    for line in lines:
        if not line.strip():
            continue
        # Support both arrow types
        head, bodies = re.split(r"→|->", line)
        head = head.strip()

        # Split by |
        parts = [p.strip() for p in bodies.split("|")]
        productions = []

        for p in parts:
            # 1. If the production is EXACTLY epsilon, it becomes the empty string ""
            if p in ["ϵ", "ε", "eps", ""]:
                productions.append("")
            else:
                # 2. If epsilon is attached to other letters (like "ϵBb"),
                # we strip the ϵ out because empty string + text = text.
                cleaned = p.replace("ϵ", "").replace("ε", "")
                productions.append(cleaned)

        if head in grammar:
            grammar[head].extend(productions)
        else:
            grammar[head] = productions

    return grammar


def compute_sets(grammar):
    first = {nt: set() for nt in grammar}
    follow = {nt: set() for nt in grammar}
    non_terminals = list(grammar.keys())

    if not non_terminals:
        return {}, {}

    # Initialization: Start symbol gets $
    follow[non_terminals[0]].add("$")

    # --- Compute FIRST Sets ---
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                before_len = len(first[nt])
                if prod == "":  # Epsilon production
                    first[nt].add("")
                else:
                    for i, symbol in enumerate(prod):
                        if symbol not in grammar:  # Terminal
                            first[nt].add(symbol)
                            break
                        else:  # Non-Terminal
                            first[nt].update(first[symbol] - {""})
                            if "" not in first[symbol]:
                                break
                    else:
                        first[nt].add("")

                if len(first[nt]) > before_len:
                    changed = True

    # --- Compute FOLLOW Sets ---
    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for prod in productions:
                for i, symbol in enumerate(prod):
                    if symbol in grammar:  # Only compute follow for Non-Terminals
                        before_len = len(follow[symbol])

                        trailer = prod[i + 1 :]
                        if not trailer:
                            follow[symbol].update(follow[nt])
                        else:
                            first_of_trailer = set()
                            for next_sym in trailer:
                                if next_sym not in grammar:
                                    first_of_trailer.add(next_sym)
                                    break
                                first_of_trailer.update(first[next_sym] - {""})
                                if "" not in first[next_sym]:
                                    break
                            else:
                                first_of_trailer.add("")

                            follow[symbol].update(first_of_trailer - {""})
                            if "" in first_of_trailer:
                                follow[symbol].update(follow[nt])

                        if len(follow[symbol]) > before_len:
                            changed = True
    return first, follow


def main():
    print("Grammar Parser (First & Follow)")
    print("Example input format: S -> AB")
    print("Use 'eps' or 'ϵ' for epsilon. Press Ctrl+C to exit.\n")

    try:
        n = int(input("How many production lines? "))
        lines = []
        for i in range(n):
            lines.append(input(f"Line {i + 1}: "))

        grammar = parse_grammar(lines)
        f_sets, fol_sets = compute_sets(grammar)

        print(f"\n{'NT':<5} | {'First':<20} | {'Follow':<20}")
        print("-" * 50)
        for nt in grammar:
            # Replaces the internal "" back to ϵ for clean printing
            f_str = (
                "{"
                + ", ".join(sorted([x if x != "" else "ϵ" for x in f_sets[nt]]))
                + "}"
            )
            fol_str = "{" + ", ".join(sorted(list(fol_sets[nt]))) + "}"
            print(f"{nt:<5} | {f_str:<20} | {fol_str:<20}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

import re
from tabulate import tabulate


def parse_grammar(lines):
    grammar = {}
    productions_list = []
    rule_id = 1

    for line in lines:
        if not line.strip():
            continue
        # Support both arrow types
        try:
            head, bodies = re.split(r"→|->", line)
        except ValueError:
            continue

        head = head.strip()
        parts = [p.strip() for p in bodies.split("|")]

        if head not in grammar:
            grammar[head] = []

        for p in parts:
            # Normalize Epsilon
            if p in ["ϵ", "ε", "eps", ""]:
                symbols = ["ε"]
            else:
                # Remove ϵ if it is part of a string (e.g., ϵBb -> Bb)
                p_clean = p.replace("ϵ", "").replace("ε", "").replace("eps", "")
                symbols = list(p_clean) if p_clean else ["ε"]

            grammar[head].append(symbols)
            productions_list.append({"id": rule_id, "head": head, "rhs": symbols})
            rule_id += 1

    return grammar, productions_list


def compute_ll1_logic(grammar, prod_list):
    first = {nt: set() for nt in grammar}
    follow = {nt: set() for nt in grammar}
    nts = list(grammar.keys())
    follow[nts[0]].add("$")

    # --- Compute FIRST Sets ---
    changed = True
    while changed:
        changed = False
        for nt, prods in grammar.items():
            for rhs in prods:
                before = len(first[nt])
                if rhs == ["ε"]:
                    first[nt].add("ε")
                else:
                    for sym in rhs:
                        if sym not in grammar:  # Terminal
                            first[nt].add(sym)
                            break
                        else:  # Non-Terminal
                            first[nt].update(first[sym] - {"ε"})
                            if "ε" not in first[sym]:
                                break
                    else:
                        first[nt].add("ε")
                if len(first[nt]) > before:
                    changed = True

    # --- Compute FOLLOW Sets ---
    changed = True
    while changed:
        changed = False
        for nt, prods in grammar.items():
            for rhs in prods:
                for i, sym in enumerate(rhs):
                    if sym in grammar:
                        before = len(follow[sym])
                        trailer = rhs[i + 1 :]
                        if not trailer:
                            follow[sym].update(follow[nt])
                        else:
                            f_t = set()
                            for s in trailer:
                                if s not in grammar:
                                    f_t.add(s)
                                    break
                                f_t.update(first[s] - {"ε"})
                                if "ε" not in first[s]:
                                    break
                            else:
                                f_t.add("ε")

                            follow[sym].update(f_t - {"ε"})
                            if "ε" in f_t:
                                follow[sym].update(follow[nt])
                        if len(follow[sym]) > before:
                            changed = True

    # --- Build Table with Multiple Rule Support ---
    table = {}
    terminals = set()
    for p in prod_list:
        for s in p["rhs"]:
            if s not in grammar and s != "ε":
                terminals.add(s)
    terminals.add("$")

    for p in prod_list:
        head, rhs, rid = p["head"], p["rhs"], p["id"]
        lookaheads = set()

        # Determine Lookaheads for this specific production
        if rhs == ["ε"]:
            lookaheads = follow[head]
        else:
            for s in rhs:
                if s not in grammar:
                    lookaheads.add(s)
                    break
                lookaheads.update(first[s] - {"ε"})
                if "ε" not in first[s]:
                    break
            else:
                lookaheads.update(follow[head])

        if head not in table:
            table[head] = {}
        for la in lookaheads:
            if la not in table[head]:
                table[head][la] = []
            table[head][la].append(rid)

    return table, sorted(list(terminals)), first, follow


def run_parser():
    print("--- LL(1) Predictive Parser Generator ---")
    n = int(input("How many lines of grammar? "))
    user_lines = [input(f"Line {i + 1}: ") for i in range(n)]

    g_dict, p_list = parse_grammar(user_lines)
    start_symbol = list(g_dict.keys())[0]
    table, terminals, firsts, follows = compute_ll1_logic(g_dict, p_list)

    # Format table cells for display (e.g., [1, 3] -> "1, 3")
    display_rows = []
    for nt in g_dict:
        row = [nt]
        for t in terminals:
            cell_data = table.get(nt, {}).get(t, "-")
            if isinstance(cell_data, list):
                row.append(", ".join(map(str, cell_data)))
            else:
                row.append(cell_data)
        display_rows.append(row)

    print("\n[LL(1) Parsing Table]")
    print(tabulate(display_rows, headers=["NT"] + terminals, tablefmt="grid"))

    # Parsing Execution Logic
    test_str = input("\nEnter string to parse: ")
    tokens = list(test_str.replace(" ", "")) + ["$"]
    stack = ["$", start_symbol]
    idx = 0
    history = []
    p_map = {p["id"]: p["rhs"] for p in p_list}

    success = True
    while stack:
        top = stack[-1]
        curr = tokens[idx]
        step = [str(stack), "".join(tokens[idx:])]

        if top == curr:
            step.append(f"Match {top}")
            stack.pop()
            if top != "$":
                idx += 1
        elif top in table:
            rules = table[top].get(curr)
            if rules:
                # If multiple rules exist, pick the first one but note the conflict
                rid = rules[0]
                rhs = p_map[rid]
                action_text = f"Apply Rule {rid}"
                if len(rules) > 1:
                    action_text += f" (Conflict! used {rid})"
                step.append(action_text)
                stack.pop()
                if rhs != ["ε"]:
                    for s in reversed(rhs):
                        stack.append(s)
            else:
                step.append(f"ERROR: No entry for ({top}, {curr})")
                success = False
        else:
            step.append(f"ERROR: Unexpected {top}")
            success = False

        history.append(step)
        if not success or (top == "$" and curr == "$"):
            break

    print(f"\n[Trace for '{test_str}']")
    print(tabulate(history, headers=["Stack", "Input", "Action"], tablefmt="simple"))
    print("\nRESULT:", "Accepted" if success else "Rejected")


if __name__ == "__main__":
    run_parser()

import itertools

class Normalizer:
    def __init__(self, attributes, fds, multivalued_attributes=None, has_repeating_groups=False):
        self.attributes = set(attributes)
        self.fds = fds
        self.multivalued_attributes = multivalued_attributes or []
        self.has_repeating_groups = has_repeating_groups
        self.candidate_keys = []
        self.prime_attributes = set()
        self.find_candidate_keys()

    # ─── 1NF ───────────────────────────────────────────────────────────────────

    def check_1nf_violations(self):
        violations = []
        for attr in self.multivalued_attributes:
            violations.append({
                "type": "Multi-valued Attribute",
                "attribute": attr,
                "reason": f"'{attr}' can hold multiple values (e.g. a list), which violates atomicity."
            })
        if self.has_repeating_groups:
            violations.append({
                "type": "Repeating Group",
                "attribute": "—",
                "reason": "The schema contains repeating groups (e.g. numbered columns like Phone1, Phone2). Each fact should be stored in its own row."
            })
        return violations

    def get_1nf_steps(self):
        violations = self.check_1nf_violations()
        steps = []
        steps.append({
            "title": "Identify atomic requirement",
            "detail": (
                "First Normal Form (1NF) requires every attribute to hold a single, indivisible "
                "(atomic) value, and every row to be unique. There must be no repeating groups "
                "or multi-valued columns."
            )
        })
        if not violations:
            steps.append({
                "title": "Check: all attributes atomic?",
                "detail": (
                    f"All {len(self.attributes)} attribute(s) — {{{', '.join(sorted(self.attributes))}}} — "
                    "appear to store atomic values. No repeating groups were reported."
                )
            })
            steps.append({
                "title": "Result: already in 1NF",
                "detail": (
                    "The relation satisfies 1NF. We can proceed to check higher normal forms."
                )
            })
        else:
            for v in violations:
                if v["type"] == "Multi-valued Attribute":
                    steps.append({
                        "title": f"Violation: '{v['attribute']}' is multi-valued",
                        "detail": (
                            f"'{v['attribute']}' can contain multiple values in a single cell. "
                            "Fix: create a separate row for each value, moving '{v['attribute']}' "
                            "into a child relation keyed by the parent's primary key."
                        )
                    })
                else:
                    steps.append({
                        "title": "Violation: repeating groups detected",
                        "detail": (
                            "Repeating groups (e.g. Phone1, Phone2, Phone3) encode the same "
                            "fact multiple times as separate columns. Fix: replace them with a "
                            "single attribute in a new relation, with one row per value."
                        )
                    })
            steps.append({
                "title": "Result: 1NF violations found",
                "detail": (
                    "Resolve the violations above before proceeding. Once every attribute is "
                    "atomic and rows are unique, the relation is in 1NF."
                )
            })
        return steps

    def get_closure(self, attribute_set, fds=None):
        if fds is None:
            fds = self.fds
        closure = set(attribute_set)
        while True:
            new_elements = set()
            for lhs, rhs in fds:
                if lhs.issubset(closure):
                    new_elements.update(rhs)
            if new_elements.issubset(closure):
                break
            closure.update(new_elements)
        return closure

    def find_candidate_keys(self):
        if self.fds:
            rhs_all = set().union(*(rhs for lhs, rhs in self.fds))
        else:
            rhs_all = set()

        core = self.attributes - rhs_all
        others = self.attributes - core
        found_keys = []

        if self.get_closure(core) == self.attributes:
            minimal_found = False
            for size in range(1, len(core) + 1):
                for combo in itertools.combinations(core, size):
                    test_set = frozenset(combo)
                    if self.get_closure(test_set) == self.attributes:
                        if not any(k.issubset(test_set) for k in found_keys):
                            found_keys.append(test_set)
                            minimal_found = True
                if minimal_found:
                    break
            if not found_keys:
                found_keys.append(frozenset(core))
        else:
            for size in range(1, len(others) + 1):
                for combo in itertools.combinations(others, size):
                    test_set = frozenset(core | set(combo))
                    if self.get_closure(test_set) == self.attributes:
                        if not any(k.issubset(test_set) for k in found_keys):
                            found_keys.append(test_set)
                next_size_has_new = False
                if size < len(others):
                    for combo in itertools.combinations(others, size + 1):
                        test_set = frozenset(core | set(combo))
                        if not any(k.issubset(test_set) for k in found_keys):
                            next_size_has_new = True
                            break
                if not next_size_has_new:
                    break

        self.candidate_keys = [set(k) for k in found_keys]
        self.prime_attributes = set().union(*self.candidate_keys) if self.candidate_keys else set()
        return self.candidate_keys

    def is_superkey(self, attr_set):
        return any(attr_set.issuperset(k) for k in self.candidate_keys)

    def check_2nf_violations(self):
        violations = []
        seen = set()
        for lhs, rhs in self.fds:
            for key in self.candidate_keys:
                if lhs < set(key):
                    non_prime_rhs = rhs - self.prime_attributes
                    if non_prime_rhs:
                        fd_str = f"{sorted(list(lhs))} -> {sorted(list(non_prime_rhs))}"
                        if fd_str not in seen:
                            seen.add(fd_str)
                            violations.append({
                                "fd": fd_str,
                                "type": "Partial Dependency",
                                "reason": f"{sorted(list(lhs))} is a proper subset of candidate key {sorted(list(key))}",
                                "lhs": sorted(list(lhs)),
                                "rhs": sorted(list(non_prime_rhs))
                            })
        return violations

    def check_3nf_violations(self):
        violations = []
        seen = set()
        for lhs, rhs in self.fds:
            if not self.is_superkey(lhs):
                non_prime_rhs = rhs - self.prime_attributes
                if non_prime_rhs:
                    fd_str = f"{sorted(list(lhs))} -> {sorted(list(non_prime_rhs))}"
                    if fd_str not in seen:
                        seen.add(fd_str)
                        violations.append({
                            "fd": fd_str,
                            "type": "Transitive Dependency",
                            "reason": f"{sorted(list(lhs))} is not a superkey and determines non-prime attribute(s)",
                            "lhs": sorted(list(lhs)),
                            "rhs": sorted(list(non_prime_rhs))
                        })
        return violations

    def check_bcnf_violations(self):
        violations = []
        seen = set()
        for lhs, rhs in self.fds:
            actual_rhs = rhs - lhs
            if not self.is_superkey(lhs) and actual_rhs:
                fd_str = f"{sorted(list(lhs))} -> {sorted(list(actual_rhs))}"
                if fd_str not in seen:
                    seen.add(fd_str)
                    violations.append({
                        "fd": fd_str,
                        "type": "BCNF Violation",
                        "reason": f"{sorted(list(lhs))} is not a superkey",
                        "lhs": sorted(list(lhs)),
                        "rhs": sorted(list(actual_rhs))
                    })
        return violations

    # ─── Step-by-step narratives ────────────────────────────────────────────────

    def get_candidate_key_steps(self):
        steps = []
        if self.fds:
            rhs_all = set().union(*(rhs for _, rhs in self.fds))
        else:
            rhs_all = set()
        core = self.attributes - rhs_all
        steps.append({
            "title": "Identify core attributes",
            "detail": (
                f"Attributes that never appear on the RHS of any FD cannot be derived — "
                f"they must be in every candidate key. "
                f"Core attributes: {{{', '.join(sorted(core)) if core else 'empty set'}}}."
            )
        })
        closure_core = self.get_closure(core)
        steps.append({
            "title": "Compute closure of core",
            "detail": (
                f"Closure {{{', '.join(sorted(core))}}}+ = "
                f"{{{', '.join(sorted(closure_core))}}}. "
                + ("The core alone determines all attributes — it is a candidate key." if closure_core == self.attributes
                   else "The core alone does not determine all attributes; we must augment it with other attributes.")
            )
        })
        if self.candidate_keys:
            for i, ck in enumerate(self.candidate_keys):
                closure = self.get_closure(ck)
                steps.append({
                    "title": f"Candidate key K{i+1}: {{{', '.join(sorted(ck))}}}",
                    "detail": (
                        f"Closure {{{', '.join(sorted(ck))}}}+ = {{{', '.join(sorted(closure))}}}. "
                        f"This equals all attributes — it is a superkey. "
                        f"No proper subset also determines all attributes, so it is minimal (a candidate key)."
                    )
                })
        steps.append({
            "title": "Identify prime vs non-prime attributes",
            "detail": (
                f"Prime attributes (appear in at least one candidate key): "
                f"{{{', '.join(sorted(self.prime_attributes)) if self.prime_attributes else 'none'}}}. "
                f"Non-prime attributes: "
                f"{{{', '.join(sorted(self.attributes - self.prime_attributes)) if (self.attributes - self.prime_attributes) else 'none'}}}."
            )
        })
        return steps

    def get_2nf_steps(self):
        violations = self.check_2nf_violations()
        steps = []
        steps.append({
            "title": "2NF definition",
            "detail": (
                "A relation is in 2NF if it is in 1NF and every non-prime attribute is "
                "fully functionally dependent on every candidate key (no partial dependencies allowed)."
            )
        })
        steps.append({
            "title": "Check each FD for partial dependency",
            "detail": (
                f"For each FD, check: is the LHS a proper subset of some candidate key AND does the RHS contain a non-prime attribute? "
                f"Candidate keys: {[sorted(list(k)) for k in self.candidate_keys]}. "
                f"Non-prime attributes: {sorted(self.attributes - self.prime_attributes)}."
            )
        })
        if not violations:
            steps.append({
                "title": "Result: already in 2NF",
                "detail": "No partial dependencies found. The relation is already in 2NF — proceed to check 3NF."
            })
        else:
            for v in violations:
                steps.append({
                    "title": f"Partial dependency found: {v['fd']}",
                    "detail": (
                        f"{v['reason']}. "
                        f"Non-prime attribute(s) {v['rhs']} are determined by only part of a candidate key."
                    )
                })
            tables = self.decompose_to_2nf()
            steps.append({
                "title": "Decompose to remove partial dependencies",
                "detail": (
                    "For each partial dependency X -> Y (where X is a proper subset of a candidate key): "
                    "create a new relation with attributes X union Y, with X as the primary key. "
                    "Remove Y from the original relation."
                )
            })
            for t in tables:
                pk = t['primary_key']
                attrs = t['attributes']
                non_pk = [a for a in attrs if a not in pk]
                steps.append({
                    "title": f"Create {t['name']}({', '.join(attrs)})",
                    "detail": (
                        f"Primary key: {{{', '.join(pk)}}}. "
                        + (f"Attributes {non_pk} are fully determined by {{{', '.join(pk)}}}."
                           if non_pk else "This table captures the original candidate key.")
                    )
                })
        return steps

    def get_3nf_steps(self):
        violations = self.check_3nf_violations()
        steps = []
        steps.append({
            "title": "3NF definition",
            "detail": (
                "A relation is in 3NF if it is in 2NF and for every non-trivial FD X->Y, "
                "either X is a superkey OR every attribute in Y is a prime attribute. "
                "This eliminates transitive dependencies on non-prime attributes."
            )
        })
        steps.append({
            "title": "Check each FD for transitive dependency",
            "detail": (
                "For each FD where the LHS is NOT a superkey, check if the RHS contains any non-prime attribute. "
                f"Superkeys are all supersets of: {[sorted(list(k)) for k in self.candidate_keys]}."
            )
        })
        if not violations:
            steps.append({
                "title": "Result: already in 3NF",
                "detail": "No transitive dependencies found. The relation is already in 3NF — proceed to check BCNF."
            })
        else:
            for v in violations:
                steps.append({
                    "title": f"Transitive dependency found: {v['fd']}",
                    "detail": (
                        f"{v['reason']}. "
                        f"Non-prime attribute(s) {v['rhs']} are transitively determined through a non-superkey LHS."
                    )
                })
            steps.append({
                "title": "Compute minimal cover (canonical cover)",
                "detail": (
                    "Step 1: Split every FD so each RHS has exactly one attribute. "
                    "Step 2: Remove extraneous attributes from each LHS (try removing each attribute; if closure is unchanged, it is extraneous). "
                    "Step 3: Remove redundant FDs (if the RHS is derivable from remaining FDs without this one, drop it). "
                    "Step 4: Merge FDs with the same LHS."
                )
            })
            tables = self.decompose_to_3nf()
            steps.append({
                "title": "Create one relation per FD group in minimal cover",
                "detail": (
                    "For each FD X->Y in the minimal cover, create a relation with attributes X union Y, with X as primary key. "
                    "If no relation contains a candidate key, add one extra relation with just the candidate key attributes."
                )
            })
            for t in tables:
                pk = t['primary_key']
                attrs = t['attributes']
                non_pk = [a for a in attrs if a not in pk]
                steps.append({
                    "title": f"Create {t['name']}({', '.join(attrs)})",
                    "detail": (
                        f"Primary key: {{{', '.join(pk)}}}. "
                        + (f"Attributes {non_pk} are fully and non-transitively determined by {{{', '.join(pk)}}}."
                           if non_pk else "This relation preserves the candidate key.")
                    )
                })
        return steps

    def get_bcnf_steps(self):
        violations = self.check_bcnf_violations()
        steps = []
        steps.append({
            "title": "BCNF definition",
            "detail": (
                "A relation is in BCNF (Boyce-Codd Normal Form) if for every non-trivial FD X->Y, "
                "X is a superkey. BCNF is stricter than 3NF — it guarantees no redundancy from FDs, "
                "but lossless decomposition may not always preserve every FD."
            )
        })
        steps.append({
            "title": "Check every non-trivial FD: is LHS a superkey?",
            "detail": (
                "A non-trivial FD is one where the RHS is not a subset of the LHS. "
                "For each such FD, the LHS must determine all attributes. "
                f"Candidate keys: {[sorted(list(k)) for k in self.candidate_keys]}."
            )
        })
        if not violations:
            steps.append({
                "title": "Result: already in BCNF",
                "detail": "Every non-trivial FD has a superkey on its LHS. The relation is in BCNF."
            })
        else:
            for v in violations:
                steps.append({
                    "title": f"BCNF violation: {v['fd']}",
                    "detail": (
                        f"{v['reason']}. Because {v['lhs']} is not a superkey but functionally determines "
                        f"{v['rhs']}, this FD causes redundancy and must be eliminated by decomposition."
                    )
                })
            steps.append({
                "title": "Apply recursive lossless decomposition",
                "detail": (
                    "For the violating FD X->Y: compute closure(X). "
                    "Split into R1 = closure(X) and R2 = X union (all_attributes minus closure(X)). "
                    "R1 and R2 join losslessly on X (since X is a key in R1). "
                    "Repeat on each sub-relation until all satisfy BCNF."
                )
            })
            tables = self.decompose_to_bcnf()
            for t in tables:
                pk = t['primary_key']
                attrs = t['attributes']
                non_pk = [a for a in attrs if a not in pk]
                steps.append({
                    "title": f"Result {t['name']}({', '.join(attrs)})",
                    "detail": (
                        f"Primary key: {{{', '.join(pk)}}}. "
                        + (f"All FDs within this sub-relation have {{{', '.join(pk)}}} as superkey. "
                           f"Attributes {non_pk} are fully determined by the key."
                           if non_pk else "This sub-relation contains only key attributes.")
                    )
                })
        return steps

    def decompose_to_2nf(self):
        violations = self.check_2nf_violations()

        if not violations:
            return [{
                "name": "R1",
                "attributes": sorted(list(self.attributes)),
                "primary_key": sorted(list(self.candidate_keys[0])) if self.candidate_keys else []
            }]

        lhs_groups = {}
        for v in violations:
            lhs_frozen = frozenset(v["lhs"])
            if lhs_frozen not in lhs_groups:
                lhs_groups[lhs_frozen] = set(v["lhs"])
            lhs_groups[lhs_frozen].update(v["rhs"])

        moved_out = set()
        for lhs_frozen, attrs in lhs_groups.items():
            moved_out.update(attrs - lhs_frozen)

        tables = []
        for i, (lhs_frozen, attrs) in enumerate(lhs_groups.items()):
            tables.append({
                "name": f"R{i + 1}",
                "attributes": sorted(list(attrs)),
                "primary_key": sorted(list(lhs_frozen))
            })

        main_attrs = self.attributes - moved_out
        has_key = any(set(k).issubset(main_attrs) for k in self.candidate_keys)
        if not has_key and self.candidate_keys:
            main_attrs.update(self.candidate_keys[0])

        tables.append({
            "name": f"R{len(tables) + 1}",
            "attributes": sorted(list(main_attrs)),
            "primary_key": sorted(list(self.candidate_keys[0])) if self.candidate_keys else []
        })

        return tables

    def decompose_to_3nf(self):
        violations = self.check_3nf_violations()

        if not violations:
            return self.decompose_to_2nf()

        def get_minimal_cover(fds):
            split_fds = []
            for lhs, rhs in fds:
                for r in rhs:
                    split_fds.append((frozenset(lhs), frozenset([r])))

            minimized = []
            for lhs, rhs in split_fds:
                min_lhs = set(lhs)
                for attr in list(lhs):
                    reduced = min_lhs - {attr}
                    if not reduced:
                        continue
                    if self.get_closure(frozenset(reduced), split_fds) >= rhs:
                        min_lhs = reduced
                minimized.append((frozenset(min_lhs), rhs))

            final = []
            for i, (lhs, rhs) in enumerate(minimized):
                other_fds = [fd for j, fd in enumerate(minimized) if j != i]
                closure_without = self.get_closure(lhs, other_fds)
                if not rhs.issubset(closure_without):
                    final.append((lhs, rhs))

            merged = {}
            for lhs, rhs in final:
                if lhs not in merged:
                    merged[lhs] = set()
                merged[lhs].update(rhs)

            return [(lhs, frozenset(rhs)) for lhs, rhs in merged.items()]

        minimal_cover = get_minimal_cover(self.fds)

        tables = []
        for lhs, rhs in minimal_cover:
            table_attrs = set(lhs) | set(rhs)
            tables.append({
                "attrs": table_attrs,
                "primary_key": sorted(list(lhs))
            })

        has_candidate_key = any(
            any(set(ck).issubset(t["attrs"]) for ck in self.candidate_keys)
            for t in tables
        )
        if not has_candidate_key and self.candidate_keys:
            ck = self.candidate_keys[0]
            tables.append({
                "attrs": set(ck),
                "primary_key": sorted(list(ck))
            })

        non_redundant = []
        for i, t in enumerate(tables):
            is_redundant = any(
                t["attrs"].issubset(other["attrs"]) and i != j
                for j, other in enumerate(tables)
            )
            if not is_redundant:
                non_redundant.append(t)

        return [
            {
                "name": f"R{i + 1}",
                "attributes": sorted(list(t["attrs"])),
                "primary_key": t["primary_key"]
            }
            for i, t in enumerate(non_redundant)
        ]

    def decompose_to_bcnf(self):
        violations = self.check_bcnf_violations()

        if not violations:
            return self.decompose_to_3nf()

        def get_closure_local(attr_set, fds):
            closure = set(attr_set)
            changed = True
            while changed:
                changed = False
                for lhs, rhs in fds:
                    if lhs.issubset(closure) and not rhs.issubset(closure):
                        closure.update(rhs)
                        changed = True
            return closure

        def find_keys_local(attrs, fds):
            relevant_fds = []
            for lhs, rhs in fds:
                if lhs.issubset(attrs):
                    trimmed = rhs & attrs
                    if trimmed and trimmed != lhs:
                        relevant_fds.append((lhs, trimmed))
            if not relevant_fds:
                return [frozenset(attrs)]
            rhs_all = set().union(*(rhs for _, rhs in relevant_fds))
            core = attrs - rhs_all
            others = attrs - core
            found = []
            for size in range(len(others) + 1):
                for combo in itertools.combinations(others, size):
                    test = frozenset(core | set(combo))
                    if get_closure_local(test, relevant_fds) >= attrs:
                        if not any(k.issubset(test) for k in found):
                            found.append(test)
                if found:
                    break
            return found if found else [frozenset(attrs)]

        def pick_violation(attrs, relevant_fds):
            # Group all RHS by unique LHS first
            lhs_coverage = {}
            for lhs, rhs in relevant_fds:
                if lhs not in lhs_coverage:
                    lhs_coverage[lhs] = set()
                lhs_coverage[lhs].update(rhs)

            best_lhs = None
            best_closure_size = -1
            best_coverage_size = -1

            for lhs, combined_rhs in lhs_coverage.items():
                actual_rhs = combined_rhs - lhs
                if not actual_rhs:
                    continue
                local_closure = get_closure_local(lhs, relevant_fds)
                # Skip superkeys
                if local_closure >= attrs:
                    continue
                closure_size = len(local_closure)
                coverage_size = len(combined_rhs)
                # Pick by closure size, tiebreak by coverage size
                if (closure_size > best_closure_size or
                        (closure_size == best_closure_size and
                         coverage_size > best_coverage_size)):
                    best_closure_size = closure_size
                    best_coverage_size = coverage_size
                    best_lhs = lhs

            return best_lhs

        def decompose(attrs, fds):
            relevant_fds = []
            for lhs, rhs in fds:
                if lhs.issubset(attrs):
                    trimmed_rhs = rhs & attrs
                    if trimmed_rhs and trimmed_rhs != lhs:
                        relevant_fds.append((lhs, trimmed_rhs))

            viol_lhs = pick_violation(attrs, relevant_fds)

            if viol_lhs is None:
                keys = find_keys_local(attrs, relevant_fds)
                return [{
                    "attributes": sorted(list(attrs)),
                    "primary_key": sorted(list(keys[0])) if keys else sorted(list(attrs))
                }]

            closure_lhs = get_closure_local(viol_lhs, relevant_fds)
            r1 = frozenset(closure_lhs)
            r2 = frozenset(viol_lhs | (attrs - closure_lhs))

            if r1 == frozenset(attrs) or r2 == frozenset(attrs):
                keys = find_keys_local(attrs, relevant_fds)
                return [{
                    "attributes": sorted(list(attrs)),
                    "primary_key": sorted(list(keys[0])) if keys else sorted(list(attrs))
                }]

            return decompose(r1, fds) + decompose(r2, fds)

        raw_tables = decompose(self.attributes, self.fds)

        seen_attrs = []
        unique_tables = []
        for t in raw_tables:
            key = frozenset(t["attributes"])
            if key not in seen_attrs:
                seen_attrs.append(key)
                unique_tables.append(t)

        non_redundant = []
        for i, t in enumerate(unique_tables):
            is_redundant = any(
                frozenset(t["attributes"]).issubset(frozenset(other["attributes"])) and i != j
                for j, other in enumerate(unique_tables)
            )
            if not is_redundant:
                non_redundant.append(t)

        return [{"name": f"R{i + 1}", **t} for i, t in enumerate(non_redundant)]
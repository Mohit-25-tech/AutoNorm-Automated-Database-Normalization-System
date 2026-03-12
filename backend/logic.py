import itertools

class Normalizer:
    def __init__(self, attributes, fds):
        self.attributes = set(attributes)
        self.fds = fds
        self.candidate_keys = []
        self.prime_attributes = set()
        self.find_candidate_keys()

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
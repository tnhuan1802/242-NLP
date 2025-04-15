from pyvi import ViTokenizer
import re

class DependencyParser:
    def __init__(self):
        # City names for dependency parsing
        self.cities = ["Huế", "TP. Hồ Chí Minh", "Đà Nẵng", "Hà Nội", "Khánh Hòa", "Hải Phòng"]
        # City mapping
        self.city_mappings = {
            "Huế": "HUE",
            "Tp. Hồ Chí Minh": "HCMC",
            "Đà Nẵng": "ĐN",
            "Hà Nội": "HN",
            "Khánh Hòa": "KH",
            "Hải Phòng": "HP"
        }
        # Load stopwords from file
        self.stopwords = self.load_stopwords("input/vietnamese-stopwords.txt")
        # Golden-tree bank: Unified list of (head, dependent, label) relations
        self.golden_tree_bank = [
            # Query 1
            ("đến", "máy bay", "nsubj"),
            ("đến", "Máy bay", "nsubj"),
            ("root", "đến", "root"),
            ("đến", "thành phố", "to-loc"),
            ("thành phố", "Huế", "nmod"),
            ("máy bay", "nào", "which"),
            ("Máy bay", "nào", "which"),
            ("13:30HR", "lúc", "at"),
            ("đến", "13:30HR", "at-time"),
            ("đến", "?", "question"),
            # Query 2
            ("bay", "máy bay", "nsubj"),
            ("root", "bay", "root"),
            ("từ", "Đà Nẵng", "from-loc"),
            ("đến", "TP. Hồ Chí Minh", "to-loc"),
            ("1:00HR", "mất", "wh-time"),
            ("bay", "1:00HR", "at-time"),
            ("bay", "?", "question"),
            # Query 3
            ("hạ cánh", "máy bay", "nsubj"),
            ("root", "hạ cánh", "root"),
            ("Huế", "ở", "to-loc"),
            ("hạ cánh", "?", "question"),
            ("máy bay", "nào", "which"),
            ("máy bay", "mã hiệu", "nmod"),
            ("máy bay", "các", "det"),
            ("hạ cánh", "cho biết", "discourse"),
            ("cho biết", "Hãy", "aux"),
            # Query 4: Máy bay nào xuất phát từ Tp.Hồ Chí Minh, lúc mấy giờ ?
            ("xuất phát", "máy bay", "nsubj"),
            ("root", "xuất phát", "root"),
            ("TP. Hồ Chí Minh", "từ", "from-loc"),
            ("mấy giờ", "lúc", "at"),
            ("xuất phát", "mấy giờ", "at-time"),
            ("xuất phát", "?", "question"),
            ("máy bay", "nào", "which"),
            # Query 5: Máy bay nào bay từ TP.Hồ Chí Minh đến Hà Nội ?
            ("bay", "máy bay", "nsubj"),
            ("root", "bay", "root"),
            ("TP. Hồ Chí Minh", "từ", "from-loc"),
            ("Hà Nội", "đến", "to-loc"),
            ("bay", "?", "question"),
            ("máy bay", "nào", "which"),
        ]

    def load_stopwords(self, filepath):
        """Load stopwords from a file."""
        stopwords = set()
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip()
                    if word:
                        stopwords.add(word)
        except FileNotFoundError:
            print(f"Warning: Stopwords file {filepath} not found. Using empty stopwords list.")
        return stopwords

    def tokenize(self, sentence):
        """Tokenize using pyvi, convert underscores to spaces, merge city and time tokens."""
        sentence = re.sub(r'\bmấy\s+giờ\b', 'mấy_giờ', sentence)
        sentence = re.sub(r'TP\.\s*Hồ Chí Minh', 'TP. Hồ Chí Minh', sentence)
        sentence = re.sub(r'Tp\.\s*Hồ Chí Minh', 'TP. Hồ Chí Minh', sentence)
        sentence = re.sub(r'TP\.\s*HCMC', 'TP. Hồ Chí Minh', sentence)
        sentence = re.sub(r'Tp\.\s*HCMC', 'TP. Hồ Chí Minh', sentence)
        sentence = re.sub(r'(\d{1,2})\s*giờ', r'\1:00HR', sentence)
        sentence = re.sub(r'(\d{1,2})\s*:\s*(\d{2})\s*HR', r'\1:\2HR', sentence)
        sentence = re.sub(r'(\d{1,2})\s*:\s*(\d{2}HR)', r'\1:\2', sentence)
        tokens = ViTokenizer.tokenize(sentence).split()
        tokens = [t.replace("_", " ") for t in tokens]
        
        merged_tokens = []
        i = 0
        while i < len(tokens):
            if i + 1 < len(tokens) and tokens[i] == "TP." and tokens[i + 1] == "Hồ Chí Minh":
                merged_tokens.append("TP. Hồ Chí Minh")
                i += 2
            elif i + 3 < len(tokens) and tokens[i].isdigit() and tokens[i + 1] == ":" and tokens[i + 2].isdigit() and tokens[i + 3] == "HR":
                merged_tokens.append(f"{tokens[i]}:{tokens[i + 2]}HR")
                i += 4
            elif i + 2 < len(tokens) and tokens[i].isdigit() and tokens[i + 1] == ":" and re.match(r"\d{2}HR", tokens[i + 2]):
                merged_tokens.append(f"{tokens[i]}:{tokens[i + 2]}")
                i += 3
            elif re.match(r"\d{1,2}:\d{2}HR", tokens[i]):
                merged_tokens.append(tokens[i])
                i += 1
            else:
                merged_tokens.append(tokens[i])
                i += 1
        # Truncate stopwords
        return merged_tokens
        # return [token for token in merged_tokens if token.lower() not in self.stopwords] 

    def get_dependencies(self, sentence):
        """Arc-eager dependency parser using golden-tree bank."""
        tokens = self.tokenize(sentence)
        stack = ["root"]
        buffer = tokens[:]
        arcs = []
        
        # Track assigned dependencies
        assigned_deps = set()

        def can_reduce(stack, arcs):
            if len(stack) < 1:
                return False
            s_top = stack[-1]

            # Check if s_top has root as a dependent
            if f"root(root, {s_top})" in arcs:
                return False

            # Check if s_top has been assigned as a dependent
            assigned_as_dep = any(f"{l}({h}, {s_top})" in arc for arc in arcs for h, d, l in self.golden_tree_bank if f"{l}({h}, {d})" == arc)

            # Check if s_top has any dependents
            expected_deps = [f"{l}({h}, {d})" for h, d, l in self.golden_tree_bank if h == s_top]
            assigned = [f"{l}({h}, {d})" for h, d, l in self.golden_tree_bank if f"{l}({h}, {d})" in arcs]
            # Check if s_top is not a dependent in unassigned arcs
            pending_deps = [f"{l}({h}, {d})" for h, d, l in self.golden_tree_bank if d == s_top and f"{l}({h}, {d})" not in assigned_deps]
            # REDUCE if s_top has been assigned as a dependent and has no dependents,
            # or if it has assigned all its dependents and no pending dependencies
            return (assigned_as_dep and not expected_deps) or (len(expected_deps) == len(assigned) and not pending_deps) or (set(expected_deps) <= set(assigned))

        def find_action(stack, buffer):
            if len(stack) < 1:
                return None, None
            s_top = stack[-1].lower()
            b_front = buffer[0] if buffer else None
            
            # Evaluate all possible actions
            valid_actions = []
            
            
            # LEFT-ARC: Check if b_front -> s_top exists in tree bank
            if buffer and s_top != "root":
                for head, dep, label in self.golden_tree_bank:
                    dep_str = f"{label}({head}, {dep})"
                    if dep_str not in assigned_deps and head == b_front and dep == s_top:
                        valid_actions.append(("LEFT-ARC", (label, head, dep)))
            
            # RIGHT-ARC: Check if s_top -> b_front exists in tree bank
            if buffer:
                for head, dep, label in self.golden_tree_bank:
                    dep_str = f"{label}({head}, {dep})"
                    if dep_str not in assigned_deps and head == s_top and dep == b_front:
                        valid_actions.append(("RIGHT-ARC", (label, head, dep)))
            
            # REDUCE: Check if s_top can be reduced
            if can_reduce(stack, arcs):
                valid_actions.append(("REDUCE", None))
            
            # SHIFT: Possible if buffer is non-empty
            if buffer:
                valid_actions.append(("SHIFT", None))
            # Return first valid action (treats all equally)\
            return valid_actions[0] if valid_actions else (None, None)

        while buffer or len(stack) > 1:
            action, arc_info = find_action(stack, buffer)
            # print(f"Action: {action}, Stack: {stack}, Buffer: {buffer}, Arcs: {arcs}")
            if action == "SHIFT" and buffer:
                stack.append(buffer.pop(0))
            elif action == "LEFT-ARC" and stack and buffer:
                label, head, dep = arc_info
                arcs.append(f"{label}({head}, {dep})")
                assigned_deps.add(f"{label}({head}, {dep})")
                stack.pop(-1)  # Pop s_top
            elif action == "RIGHT-ARC" and stack and buffer:
                label, head, dep = arc_info
                arcs.append(f"{label}({head}, {dep})")
                assigned_deps.add(f"{label}({head}, {dep})")
                stack.append(buffer.pop(0))  # Shift b_front to stack
                if label in ["question", "punctuation"]:
                    break
            elif action == "REDUCE" and stack:
                stack.pop(-1)  # Reduce
            else:
                if stack and len(stack) > 1:
                    stack.pop(-1)  # Clear stack
                else:
                    break

            # Set root for verbs
            if stack and stack[-1] in ["đến", "bay", "xuất phát"] and "root(root, " not in "".join(arcs):
                arcs.append(f"root(root, {stack[-1]})")

        return arcs if arcs else []  # Always return a list
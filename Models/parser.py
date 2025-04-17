from underthesea import word_tokenize
import re

class DependencyParser:
    def __init__(self):
        # City names for dependency parsing
        self.cities = ["Huế", "Hồ Chí Minh", "Đà Nẵng", "Hà Nội", "Khánh Hòa", "Hải Phòng"]
        # City mapping
        self.city_mappings = {
            "Huế": "HUE",
            "Hồ Chí Minh": "HCMC",
            "Đà Nẵng": "ĐN",
            "Hà Nội": "HN",
            "Hà Nội": "HN",
            "Khánh Hòa": "KH",
            "Hải Phòng": "HP"
        }
        # Load stopwords from file
        self.stopwords = self.load_stopwords("input/vietnamese-stopwords.txt")
        # Golden-tree bank: Unified list of (head, dependent, label) relations
        self.golden_tree_bank = [
            # Query 1: Máy bay nào đến thành phố Huế lúc 13:30HR ?
            ("đến", "máy bay", "nsubj"),
            ("root", "đến", "root"),
            ("đến", "thành phố", "to-loc"),
            ("thành phố", "Huế", "nmod"),
            ("máy bay", "nào", "which"),
            ("13:30HR", "lúc", "at"),
            ("đến", "13:30HR", "at-time"),
            ("đến", "?", "question"),
            # Query 2: Máy bay nào bay từ Đà Nẵng đến TP. Hồ Chí Minh mất 1 giờ ?
            ("bay", "máy bay", "nsubj"),
            ("root", "bay", "root"),
            ("từ", "Đà Nẵng", "from-loc"),
            ("đến", "Hồ Chí Minh", "to-loc"),
            ("1:00HR", "mất", "wh-time"),
            ("bay", "1:00HR", "at-time"),
            ("bay", "?", "question"),
            # Query 3: Hãy cho biết mã hiệu các máy bay hạ cánh ở Huế ?
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
            ("Hồ Chí Minh", "từ", "from-loc"),
            ("mấy giờ", "lúc", "at"),
            ("xuất phát", "?", "question"),
            ("máy bay", "nào", "which"),
            # Query 5: Máy bay nào bay từ TP.Hồ Chí Minh đến Hà Nội ?
            ("bay", "máy bay", "nsubj"),
            ("root", "bay", "root"),
            ("Hồ Chí Minh", "từ", "from-loc"),
            ("Hà Nội", "đến", "to-loc"),
            ("bay", "?", "question"),
            ("máy bay", "nào", "which"),
            # Query 6: Máy bay VN4 có xuất phát từ Đà Nẵng không ?
            ("xuất phát", "máy bay", "nsubj"),
            ("root", "xuất phát", "root"),
            ("máy bay", "VN4", "nmod"),
            ("xuất phát", "có", "aux"),
            ("Đà Nẵng", "từ", "from-loc"),
            ("xuất phát", "?", "question"),
            ("xuất phát", "không", "discourse"),
            # Query 7: Thời gian máy bay VJ5 bay từ TP. Hà Nội đến Khánh Hòa mất mấy giờ ?
            ("thời gian", "máy bay", "nmod"),
            ("máy bay", "VJ5", "nmod"),
            ("từ", "Hà Nội", "from-loc"),
            ("đến", "Khánh Hòa", "to-loc"),
            ("root", "bay", "root"),
            ("mất", "mấy giờ", "at-time"),
            ("bay", "?", "question"),
            # Query 8: Có máy bay nào xuất phát từ Hải Phòng không ?
            ("xuất phát", "máy bay", "nsubj"),
            ("root", "xuất phát", "root"),
            ("máy bay", "nào", "which"),
            ("từ", "Hải Phòng", "from-loc"),
            ("xuất phát", "?", "question"),
            # Query 9: Máy bay của hãng hàng không VietJet Air bay đến những thành phố nào ?
            ("bay", "máy bay", "nsubj"),
            ("root", "bay", "root"),
            ("máy bay", "VietJet Air", "nmod"),
            ("bay", "thành phố", "to-loc"),
            ("thành phố", "nào", "which"),
            ("bay", "?", "question"),
            # Query 11: Máy bay VJ1 xuất phát từ HCMC 10:00HR phải không?
            ("xuất phát", "máy bay", "nsubj"),
            ("máy bay", "VJ1", "nmod"),
            ("từ", "HCMC", "from-loc"),
            ("xuất phát", "10:00HR", "at-time"),
            ("root", "xuất phát", "root"),
            ("xuất phát", "?", "question"),
            # Query 12: Máy bay nào bay từ TP. Hồ Chí Minh đến Đà Nẵng mất 1:00HR ?
            ("đến", "Đà Nẵng", "to-loc"),
            # Query 13: Máy bay nào của VNAirline nào bay từ TP.HCM ra Huế mất 1 giờ ?
            ("bay", "máy bay", "nsubj"),
            ("root", "bay", "root"),
            ("máy bay", "VNAirline", "nmod"),
            ("từ", "Hồ Chí Minh", "from-loc"),
            ("ra", "Huế", "to-loc"),
            ("1:00HR", "mất", "wh-time"),
            ("máy bay", "nào", "which"),
            ("bay", "?", "question"),
            # Query 14: Máy bay VJ5 có xuất phát từ Hà Nội không, lúc mấy giờ ?
            ("máy bay", "VJ5", "nmod"),
            ("từ", "Hà Nội", "from-loc"),
            # Query 16: Máy bay nào cất cánh từ TP. Hồ Chí Minh?
            ("cất cánh", "máy bay", "nsubj"),
            ("root", "cất cánh", "root"),
            ("cất cánh", "?", "question"),
            # Query 16: Có máy bay nào bay từ Đà Nẵng ra Khánh Hòa không, nếu có thì thời gian bay là bao lâu ?
            ("ra", "Khánh Hòa", "to-loc"),
            # Query 18: Máy bay VN2 có xuất phát từ Đà Nắng không, lúc mấy giờ ?
            ("máy bay", "VN2", "nmod"),
            ("từ", "Đà Nẵng", "from-loc"),
            # Query 19: Có mấy máy bay bay đến Hà Nội, kể tên máy bay !
            ("bay", "!", "punctuation"),

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
        """Tokenize using underthesea, merge city and time tokens."""
        # Preprocess to prevent VJ5 bay merging
        sentence = re.sub(r'\b(VJ5)\s+bay\b', r'\1* bay', sentence)
        sentence = re.sub(r'\bHCMC\b', r'Hồ Chí Minh', sentence)
        sentence = re.sub(r'\bTP.HCM\b', r'Hồ Chí Minh', sentence)
        sentence = re.sub(r'\b(Hải\sPhòng)\s+không\b', r'\1 * không', sentence)
        # Preprocess to merge 'hãng hàng không VietJet Air' into 'VietJet Air'
        sentence = re.sub(r'hãng\s+hàng\s+không\s+VietJet\s+Air', 'VietJet Air', sentence)
        sentence = re.sub(r'\bVNAirline bay\b', 'VNAirline *bay', sentence)
        # Preprocess specific patterns
        sentence = re.sub(r'\bmấy\s+giờ\b', 'mấy_giờ', sentence)
        sentence = re.sub(r'TP\.\s*Hồ Chí Minh', 'Hồ Chí Minh', sentence)
        sentence = re.sub(r'Tp\.\s*Hồ Chí Minh', 'Hồ Chí Minh', sentence)
        sentence = re.sub(r'TP\.\s*HCMC', 'Hồ Chí Minh', sentence)
        sentence = re.sub(r'Tp\.\s*HCMC', 'Hồ Chí Minh', sentence)
        sentence = re.sub(r'TP\.\s*Hà Nội', 'Hà Nội', sentence)
        sentence = re.sub(r'Tp\.\s*Hà Nội', 'Hà Nội', sentence)
        sentence = re.sub(r'(\d{1,2})\s*giờ', r'\1:00HR', sentence)
        sentence = re.sub(r'(\d{1,2})\s*:\s*(\d{2})\s*HR', r'\1:\2HR', sentence)
        sentence = re.sub(r'(\d{1,2})\s*:\s*(\d{2}HR)', r'\1:\2', sentence)
        # Use underthesea word_tokenize
        tokens = word_tokenize(sentence)
        tokens = [t.replace("_", " ") for t in tokens]
        unique_tokens = []
        [unique_tokens.append(x) for x in tokens if x not in unique_tokens]
        tokens = unique_tokens
        
        merged_tokens = []
        i = 0
        while i < len(tokens):
            if i + 3 < len(tokens) and tokens[i].isdigit() and tokens[i + 1] == ":" and tokens[i + 2].isdigit() and tokens[i + 3] == "HR":
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
        # return merged_tokens
        return [token for token in merged_tokens if token.lower() not in self.stopwords] 

    def get_dependencies(self, sentence):
        """Arc-eager dependency parser using golden-tree bank."""
        tokens = self.tokenize(sentence)
        stack = ["root"]
        buffer = tokens[:]
        arcs = []
        
        assigned_deps = set()

        def can_reduce(stack, arcs):
            if len(stack) < 1:
                return False
            s_top = stack[-1]
            if f"root(root, {s_top})" in arcs:
                return False
            assigned_as_dep = any(f"{l}({h}, {s_top})" in arc for arc in arcs for h, d, l in self.golden_tree_bank if f"{l}({h}, {d})" == arc)
            expected_deps = [f"{l}({h}, {d})" for h, d, l in self.golden_tree_bank if h == s_top]
            assigned = [f"{l}({h}, {d})" for h, d, l in self.golden_tree_bank if f"{l}({h}, {d})" in arcs]
            pending_deps = [f"{l}({h}, {d})" for h, d, l in self.golden_tree_bank if d == s_top and f"{l}({h}, {d})" not in assigned_deps]
            return (assigned_as_dep and not expected_deps) or (len(expected_deps) == len(assigned) and not pending_deps) or (set(expected_deps) <= set(assigned)) or (set(expected_deps) & set(assigned))

        def find_action(stack, buffer):
            if len(stack) < 1:
                return None, None
            s_top = stack[-1].lower()
            b_front = buffer[0] if buffer else None
            
            valid_actions = []
            if buffer:
                for head, dep, label in self.golden_tree_bank:
                    dep_str = f"{label}({head}, {dep})"
                    if dep_str not in assigned_deps and head == b_front and dep == s_top:
                        valid_actions.append(("LEFT-ARC", (label, head, dep)))
            if buffer:
                for head, dep, label in self.golden_tree_bank:
                    dep_str = f"{label}({head}, {dep})"
                    if dep_str not in assigned_deps and head == s_top and dep == b_front:
                        valid_actions.append(("RIGHT-ARC", (label, head, dep)))
            if can_reduce(stack, arcs):
                valid_actions.append(("REDUCE", None))
            if buffer:
                valid_actions.append(("SHIFT", None))
            return valid_actions[0] if valid_actions else (None, None)

        while buffer or len(stack) > 1:
            action, arc_info = find_action(stack, buffer)
            if action == "SHIFT" and buffer:
                stack.append(buffer.pop(0))
            elif action == "LEFT-ARC" and stack and buffer:
                label, head, dep = arc_info
                arcs.append(f"{label}({head}, {dep})")
                assigned_deps.add(f"{label}({head}, {dep})")
                stack.pop(-1)
            elif action == "RIGHT-ARC" and stack and buffer:
                label, head, dep = arc_info
                arcs.append(f"{label}({head}, {dep})")
                assigned_deps.add(f"{label}({head}, {dep})")
                stack.append(buffer.pop(0))
                if label in ["question", "punctuation"]:
                    break
            elif action == "REDUCE" and stack:
                stack.pop(-1)
            else:
                if stack and len(stack) > 1:
                    stack.pop(-1)
                else:
                    break

            if stack and stack[-1] in ["đến", "bay", "xuất phát", "hạ cánh", "mất"] and "root(root, " not in "".join(arcs):
                arcs.append(f"root(root, {stack[-1]})")

        return arcs if arcs else []
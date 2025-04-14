# Models/parser.py
from pyvi import ViTokenizer
import re

class DependencyParser:
    def __init__(self):
        # City names for dependency parsing
        self.cities = ["Huế", "TP. Hồ Chí Minh", "Đà Nẵng", "Hà Nội", "Khánh Hòa", "Hải Phòng"]

    def tokenize(self, sentence):
        """Tokenize using pyvi, convert underscores to spaces, merge city and time tokens."""
        # Preprocess to protect city names and time formats
        sentence = re.sub(r'TP\.\s*Hồ Chí Minh', 'TP. Hồ Chí Minh', sentence)
        sentence = re.sub(r'Tp\.\s*Hồ Chí Minh', 'TP. Hồ Chí Minh', sentence)
        sentence = re.sub(r'TP\.\s*HCM', 'TP. Hồ Chí Minh', sentence)
        sentence = re.sub(r'Tp\.\s*HCM', 'TP. Hồ Chí Minh', sentence)
        sentence = re.sub(r'(\d{1,2})\s*:\s*(\d{2})\s*HR', r'\1:\2HR', sentence)
        sentence = re.sub(r'(\d{1,2})\s*:\s*(\d{2}HR)', r'\1:\2', sentence)
        tokens = ViTokenizer.tokenize(sentence).split()
        tokens = [t.replace("_", " ") for t in tokens]
        
        # Merge split city and time tokens
        merged_tokens = []
        i = 0
        while i < len(tokens):
            # Merge TP. Hồ Chí Minh
            if i + 1 < len(tokens) and tokens[i] == "TP." and tokens[i + 1] == "Hồ Chí Minh":
                merged_tokens.append("TP. Hồ Chí Minh")
                i += 2
            # Merge time tokens (e.g., "1", ":", "00", "HR" -> "1:00HR")
            elif i + 3 < len(tokens) and tokens[i].isdigit() and tokens[i + 1] == ":" and tokens[i + 2].isdigit() and tokens[i + 3] == "HR":
                merged_tokens.append(f"{tokens[i]}:{tokens[i + 2]}HR")
                i += 4
            # Merge time tokens (e.g., "1", ":", "00HR" -> "1:00HR")
            elif i + 2 < len(tokens) and tokens[i].isdigit() and tokens[i + 1] == ":" and re.match(r"\d{2}HR", tokens[i + 2]):
                merged_tokens.append(f"{tokens[i]}:{tokens[i + 2]}")
                i += 3
            # Pass through correct time tokens
            elif re.match(r"\d{1,2}:\d{2}HR", tokens[i]):
                merged_tokens.append(tokens[i])
                i += 1
            else:
                merged_tokens.append(tokens[i])
                i += 1
        return merged_tokens

    def get_dependencies(self, sentence):
        """Custom rule-based dependency parser for Query 1."""
        tokens = self.tokenize(sentence)
        relations = []
        
        # Simulate stack-buffer parsing
        stack = ["root"]
        buffer = tokens[:]
        i = 0
        current_verb = None

        while buffer or len(stack) > 1:
            if not buffer and len(stack) > 1:
                stack.pop()
                continue

            current = buffer[0] if buffer else None
            if not current:
                break

            # Rules for Query 1
            if current == "nào" and stack[-1] == "Máy bay":
                relations.append(f"which(máy bay, nào)")
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "đến" and stack[-1] in ["Máy bay", "nào"]:
                relations.append(f"nsubj(đến, máy bay)")
                relations.append(f"root(root, đến)")
                stack.pop()
                stack.append(current)
                current_verb = current
                buffer.pop(0)
                i += 1
            elif current == "thành phố" and i + 1 < len(tokens) and tokens[i + 1] == "Huế" and stack[-1] == "đến":
                relations.append(f"to-loc(đến, thành phố)")
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "Huế" and stack[-1] == "thành phố":
                relations.append(f"(thành phố, Huế)")
                stack.pop()
                stack.append("thành phố Huế")
                buffer.pop(0)
                i += 1
            elif current == "lúc" and i + 1 < len(tokens) and re.match(r"\d{1,2}:\d{2}HR", tokens[i + 1]):
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif re.match(r"\d{1,2}:\d{2}HR", current) and stack[-1] == "lúc":
                relations.append(f"at({current}, lúc)")
                relations.append(f"at-time(đến, {current})")
                stack.pop()
                if current_verb:
                    stack.append(current_verb)
                buffer.pop(0)
                i += 1
            elif current == "?" and current_verb:
                relations.append(f"question(đến, ?)")
                stack.append(current)
                buffer.pop(0)
                i += 1
            else:
                stack.append(current)
                buffer.pop(0)
                i += 1

        return relations
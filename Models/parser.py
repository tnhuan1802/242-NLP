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
        """Custom rule-based dependency parser."""
        tokens = self.tokenize(sentence)
        relations = []
        
        # Simulate stack-buffer parsing
        stack = ["root"]
        buffer = tokens[:]
        i = 0
        current_verb = None  # Track the main verb (e.g., "bay")

        while buffer or len(stack) > 1:
            if not buffer and len(stack) > 1:
                stack.pop()  # Clean up stack
                continue

            current = buffer[0] if buffer else None
            if not current:
                break

            # Rules based on sentence structure
            if current == "nào" and stack[-1] == "Máy bay":
                relations.append(f"which(máy bay, nào)")
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "mã hiệu" and stack[-1] == "Máy bay" and "hạ cánh" in buffer:
                relations.append(f"which(máy bay, mã hiệu)")
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif re.match(r"VN\d+|VJ\d+", current) and stack[-1] == "Máy bay" and "xuất phát" in buffer:
                relations.append(f"nsubj(xuất phát, {current})")
                stack.pop()
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current in ["đến", "bay", "hạ cánh", "xuất phát"] and stack[-1] in ["Máy bay", "nào", "mã hiệu"] or (stack[-1] and re.match(r"VN\d+|VJ\d+", stack[-1])):
                verb = current
                subject = stack[-1]
                if subject == "nào" or subject == "mã hiệu":
                    subject = "máy bay"
                relations.append(f"nsubj({verb}, {subject})")
                while len(stack) > 1 and stack[-1] not in ["root"]:
                    stack.pop()
                stack.append(verb)
                current_verb = verb
                buffer.pop(0)
                i += 1
            elif current == "từ" and i + 1 < len(tokens) and (tokens[i + 1] in self.cities or tokens[i + 1] == "thành phố"):
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current in self.cities and stack[-1] == "từ":
                relations.append(f"from-loc({current}, từ)")
                stack.pop()
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current in ["đến", "ra", "ở"] and i + 1 < len(tokens) and (tokens[i + 1] in self.cities or tokens[i + 1] == "thành phố"):
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "thành phố" and i + 1 < len(tokens) and tokens[i + 1] in self.cities and stack[-1] in ["đến", "ra", "ở"]:
                buffer.pop(0)
                i += 1
                continue  # Skip "thành phố" and process the city name next
            elif current in self.cities and stack[-1] in ["đến", "ra", "ở"]:
                relations.append(f"to-loc({current}, {stack[-1]})")
                stack.pop()
                if current_verb and stack[-1] != current_verb:
                    stack.append(current_verb)  # Restore verb for later rules
                else:
                    stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "lúc" and i + 1 < len(tokens) and re.match(r"\d{1,2}:\d{2}HR", tokens[i + 1]):
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif re.match(r"\d{1,2}:\d{2}HR", current) and stack[-1] == "lúc":
                relations.append(f"at-time({current}, lúc)")
                stack.pop()
                if current_verb and stack[-1] != current_verb:
                    stack.append(current_verb)  # Restore verb
                else:
                    stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "mất" and i + 1 < len(tokens) and re.match(r"\d{1,2}:\d{2}HR", tokens[i + 1]):
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif re.match(r"\d{1,2}:\d{2}HR", current) and stack[-1] == "mất":
                relations.append(f"wh-time(thời gian, mất)")
                relations.append(f"at-time({current}, mất)")
                stack.pop()
                if current_verb and stack[-1] != current_verb:
                    stack.append(current_verb)  # Restore verb
                else:
                    stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "?" and current_verb:
                relations.append(f"question({current_verb}, ?)")
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "không" and current_verb:
                relations.append(f"question({current_verb}, không)")
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "thời gian" and "bao lâu" in buffer:
                stack.append(current)
                buffer.pop(0)
                i += 1
            elif current == "bao lâu":
                relations.append(f"wh-time(thời gian, bao lâu)")
                stack.append(current)
                buffer.pop(0)
                i += 1
            else:
                stack.append(current)
                buffer.pop(0)
                i += 1

        # Final check for root
        if current_verb in ["đến", "bay", "xuất phát", "hạ cánh"]:
            relations.append(f"root(root, {current_verb})")

        return relations
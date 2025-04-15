from Models.parser import DependencyParser
import re

class QueryProcessor:
    def __init__(self):
        self.parser = DependencyParser()

    def process(self, query):
        """Process query through all steps."""
        tokens = self.parser.tokenize(query)
        dependencies = self.parser.get_dependencies(query) or []  # Ensure non-None
        grammatical = self.dependencies_to_grammatical(dependencies, query)
        logical = self.grammatical_to_logical(grammatical)
        procedural = self.logical_to_procedural(logical, query)

        return {
            "tokens": tokens,
            "dependencies": dependencies,
            "grammatical": grammatical,
            "logical": logical,
            "procedural": procedural
        }

    def dependencies_to_grammatical(self, dependencies, query):
        """Convert dependencies to grammatical relations as a list."""
        grammatical = []
        city_unit = None
        for dep in dependencies or []:  # Handle empty or None dependencies
            if not isinstance(dep, str):  # Skip non-string entries
                continue
            if "which" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["WHICH", "m1", parts[0].upper()])
            elif "nsubj" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["PRED", "m1", parts[0].upper()])
                grammatical.append(["LSUBJ", "m1", parts[1].upper()])
            elif "to-loc" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[1] == "thành phố":
                    city_unit = "THÀNH PHỐ-HUẾ"
                elif parts[0] == "TP. Hồ Chí Minh":
                    grammatical.append(["TO-LOC", "m1", parts[0].upper()])
                else:
                    grammatical.append(["TO-LOC", "m1", parts[0].upper()])
                continue
            elif "nmod" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[0] == "thành phố" and parts[1] == "Huế":
                    if city_unit:
                        grammatical.append(["TO-LOC", "m1", city_unit])
                        city_unit = None
            elif "from-loc" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["FROM-LOC", "m1", parts[0].upper()])
            elif "at(" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["AT-TIME", "m1", parts[0].upper()])
            elif "at-time(" in dep:
                continue  # Handled by at()
            elif "wh-time" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[1] == "mất" or parts[1] == "bao lâu":
                    grammatical.append(["WH-TIME", "m1", parts[0].upper()])
        return grammatical

    def grammatical_to_logical(self, grammatical):
        """Convert grammatical relations to logical form as a list."""
        logical = []
        pred = None
        args = []
        for g in grammatical:
            if g[0] == "WHICH":
                logical.append("(m1 WHICH MÁY BAY)")
            elif g[0] == "PRED":
                pred = g[2]
            elif g[0] == "LSUBJ":
                args.append("[ MÁY BAY ]")
            elif g[0] == "TO-LOC":
                args.append(f"[TO-LOC {g[2]}]")
            elif g[0] == "FROM-LOC":
                args.append(f"[FROM-LOC {g[2]}]")
            elif g[0] == "AT-TIME":
                args.append(f"[AT-TIME {g[2]}]")
            elif g[0] == "WH-TIME":
                args.append(f"[RUN-TIME {g[2]}]")
        if pred:
            logical.append(f"(m1 PRED {pred} {' '.join(args)})")
        return logical

    def logical_to_procedural(self, logical, query):
        """Convert logical form to procedural form as a list."""
        if not logical:
            return ["Invalid query"]
        conditions = []
        var = "?m1"
        conditions.append(f"(MÁY_BAY {var})")
        for l in logical:
            if "RUN-TIME" in l:
                from_match = re.search(r"FROM-LOC ([^\]\[]+)]", l)
                to_match = re.search(r"TO-LOC ([^\]\[]+)]", l)
                time_match = re.search(r"RUN-TIME (\d{1,2}:\d{2}HR)", l)
                if from_match and to_match and time_match:
                    source = from_match.group(1).strip()
                    dest = to_match.group(1).strip()
                    time = time_match.group(1)
                    if source == "ĐÀ NẴNG":
                        source = "ĐN"
                    if source == "HẢI PHÒNG":
                        source = "HP"
                    if dest == "TP. HỒ CHÍ MINH":
                        dest = "HCMC"
                    elif dest == "THÀNH PHỐ-HUẾ":
                        dest = "HUE"
                    conditions.append(f"(RUN-TIME {var} {source} {dest} {time})")
            elif "AT-TIME" in l:
                city_match = re.search(r"TO-LOC ([^\]\[]+)]", l)
                time_match = re.search(r"AT-TIME (\d{1,2}:\d{2}HR)", l)
                if city_match and time_match:
                    city = city_match.group(1).strip()
                    if city == "THÀNH PHỐ-HUẾ":
                        city = "HUE"
                    elif city == "TP. HỒ CHÍ MINH":
                        city = "HCMC"
                    time = time_match.group(1)
                    conditions.append(f"(ATIME {var} {city} {time})")
        return ["PRINT-ALL", var] + conditions
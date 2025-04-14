# Models/processor.py
from Models.parser import DependencyParser
import re

class QueryProcessor:
    def __init__(self):
        self.parser = DependencyParser()

    def process(self, query):
        """Process query through all steps."""
        tokens = self.parser.tokenize(query)
        dependencies = self.parser.get_dependencies(query)
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
        for dep in dependencies:
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
                continue
            elif dep == "(thành phố, Huế)":
                if city_unit:
                    grammatical.append(["TO-LOC", "m1", city_unit])
                    city_unit = None
            elif "at(" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["AT-TIME", "m1", parts[0].upper()])
            elif "at-time(" in dep:
                continue  # Handled by at()
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
                args.append("[MÁY BAY]")
            elif g[0] == "TO-LOC":
                args.append(f"[TO-LOC {g[2]}]")
            elif g[0] == "AT-TIME":
                args.append(f"[AT-TIME {g[2]}]")
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
        # Parse logical form list
        for l in logical:
            if "AT-TIME" in l:
                city_match = re.search(r"TO-LOC ([^\]\[]+)]", l)
                time_match = re.search(r"AT-TIME (\d{1,2}:\d{2}HR)", l)
                if city_match and time_match:
                    city = city_match.group(1).strip()
                    if city == "THÀNH PHỐ-HUẾ":
                        city = "HUE"
                    time = time_match.group(1)
                    conditions.append(f"(ATIME {var} {city} {time})")
        return ["PRINT-ALL", var] + conditions
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
        """Convert dependencies to grammatical relations."""
        grammatical = []
        for dep in dependencies:
            if "which" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(f"(WHICH m1 {parts[0].upper()})")
            elif "nsubj" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                plane = parts[1].upper()
                grammatical.append(f"(m1 PRED {parts[0].upper()})")
                grammatical.append(f"(m1 LSUBJ {plane})")
            elif "to-loc" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                city = parts[0].upper()
                if city == "TP. HỒ CHÍ MINH": city = "HCMC"
                elif city == "ĐÀ NẴNG": city = "ĐN"
                elif city == "HÀ NỘI": city = "HN"
                elif city == "KHÁNH HÒA": city = "KH"
                elif city == "HẢI PHÒNG": city = "HP"
                elif city == "HUẾ": city = "HUE"
                grammatical.append(f"(m1 TO-LOC {city})")
            elif "from-loc" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                city = parts[0].upper()
                if city == "TP. HỒ CHÍ MINH": city = "HCMC"
                elif city == "ĐÀ NẴNG": city = "ĐN"
                elif city == "HÀ NỘI": city = "HN"
                elif city == "KHÁNH HÒA": city = "KH"
                elif city == "HẢI PHÒNG": city = "HP"
                elif city == "HUẾ": city = "HUE"
                grammatical.append(f"(m1 FROM-LOC {city})")
            elif "at-time" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(f"(m1 AT-TIME {parts[0].upper()})")
            elif "wh-time" in dep:
                grammatical.append("(m1 WH-TIME)")
        return grammatical

    def grammatical_to_logical(self, grammatical):
        """Convert grammatical relations to logical form."""
        logical = []
        pred = None
        args = []
        for g in grammatical:
            if "WHICH" in g:
                logical.append(g)
            elif "PRED" in g:
                pred = g.split()[2]
            elif "LSUBJ" in g:
                args.append(g.split()[2])
            elif "TO-LOC" in g:
                args.append(f"TO-LOC {g.split()[2]}")
            elif "FROM-LOC" in g:
                args.append(f"FROM-LOC {g.split()[2]}")
            elif "AT-TIME" in g:
                args.append(f"AT-TIME {g.split()[2]}")
            elif "WH-TIME" in g:
                args.append("RUN-TIME")
        if pred:
            logical.append(f"(m1 PRED {pred} [{' '.join(args)}])")
        return logical

    def logical_to_procedural(self, logical, query):
        """Convert logical form to procedural form."""
        if not logical:
            return None
        conditions = []
        var = "m1"
        command = "PRINT-ALL"
        for l in logical:
            if "WHICH" in l:
                var = l.split()[1]
                entity = l.split()[2]
                conditions.append(f"(MÁY_BAY {var})")
            elif "PRED" in l:
                parts = l.split("[")[1].split("]")[0].strip().split()
                if "AT-TIME" in l and len(parts) >= 4:
                    city = parts[1]
                    time = parts[3]
                    conditions.append(f"(ATIME {var} {city} {time})")
                elif "TO-LOC" in l and "FROM-LOC" in l:
                    start = parts[1]
                    end = parts[3]
                    time_var = "?t1" if "bao lâu" in query.lower() else parts[5] if len(parts) > 5 else "1:00HR"
                    conditions.append(f"(RUN-TIME {var} {start} {end} {time_var})")
                elif "TO-LOC" in l:
                    city = parts[1]
                    conditions.append(f"(ATIME {var} {city} ?)")
                elif "FROM-LOC" in l and "nào" not in query.lower() and re.match(r"VN\d+|VJ\d+", parts[0]):
                    plane = parts[0]
                    city = parts[1]
                    command = "TEST"
                    conditions.append(f"(DTIME {plane} {city} ?)")
                elif "FROM-LOC" in l:
                    city = parts[1]
                    conditions.append(f"(DTIME {var} {city} ?)")
                elif "RUN-TIME" in l and not "TO-LOC" in l and not "FROM-LOC" in l:
                    time_var = "?t1" if "bao lâu" in query.lower() else parts[1] if len(parts) > 1 else "1:00HR"
                    conditions.append(f"(RUN-TIME {var} ? ? {time_var})")
        return (command, var, *conditions)
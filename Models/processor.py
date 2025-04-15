from Models.parser import DependencyParser
import re

class QueryProcessor:
    def __init__(self):
        self.parser = DependencyParser()

    def process(self, query):
        """Process query through all steps."""
        print('Processing query:', query)
        tokens = self.parser.tokenize(query)
        dependencies = self.parser.get_dependencies(query) or []
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
        for dep in dependencies or []:
            if not isinstance(dep, str):
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
                    city_unit = "thành phố"
                    continue
                elif parts[0] != "đến" and parts[0] in self.parser.cities:
                    grammatical.append(["TO-LOC", "m1", parts[0].upper()])
                elif parts[0] == "đến" and parts[1] in self.parser.cities:
                    grammatical.append(["TO-LOC", "m1", parts[1].upper()])
                continue
            elif "nmod" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[0] == "thành phố" and parts[1] in self.parser.cities:
                    if city_unit:
                        grammatical.append(["TO-LOC", "m1", f"THÀNH PHỐ-{parts[1].upper()}"])
                        city_unit = None
                elif parts[1] == "mã hiệu":
                    grammatical.append(["NMOD", "m1", parts[1].upper()])
            elif "from-loc" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[0] == "từ" and parts[1] in self.parser.cities:
                    grammatical.append(["FROM-LOC", "m1", parts[1].upper()])
                elif parts[1] == "từ" and parts[0] in self.parser.cities:
                    grammatical.append(["FROM-LOC", "m1", parts[0].upper()])
            elif "at(" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["AT-TIME", "m1", parts[0].upper()])
            elif "at-time(" in dep:
                continue
            elif "wh-time" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[1] == "mất" or parts[1] == "bao lâu":
                    grammatical.append(["WH-TIME", "m1", parts[0].upper()])
            elif "discourse" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["DISCOURSE", "m1", parts[1].upper()])
            elif "aux" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["AUX", "m1", parts[1].upper()])
            elif "det" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["DET", "m1", parts[1].upper()])
            elif "question" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["QUESTION", "m1", parts[1].upper()])
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
                args.append(f"[WH-TIME {g[2]}]")
            elif g[0] == "NMOD" and g[2] == "MÃ HIỆU":
                args.append("[MÃ HIỆU]")
            elif g[0] == "DISCOURSE":
                args.append(f"[DISCOURSE {g[2]}]")
            elif g[0] == "AUX":
                args.append(f"[AUX {g[2]}]")
            elif g[0] == "DET":
                args.append(f"[DET {g[2]}]")
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
            if "FROM-LOC" in l and "TO-LOC" in l:
                from_match = re.search(r"FROM-LOC ([^\]\[]+)]", l)
                to_match = re.search(r"TO-LOC ([^\]\[]+)]", l)
                time_match = re.search(r"WH-TIME ([^\]\[]+)]", l)
                if from_match and to_match:
                    source = from_match.group(1).strip()
                    dest = to_match.group(1).strip()
                    time = time_match.group(1).strip() if time_match else "?time"
                    if "THÀNH PHỐ" in source:
                        source = source.split("-")[1]
                    if "THÀNH PHỐ" in dest:
                        dest = dest.split("-")[1]
                    source_short = self.parser.city_mappings.get(source.title(), source)
                    dest_short = self.parser.city_mappings.get(dest.title(), dest)
                    conditions.append(f"(RUN-TIME {var} {source_short} {dest_short} {time})")
            elif "FROM-LOC" in l and "AT-TIME" in l:
                city_match = re.search(r"FROM-LOC ([^\]\[]+)]", l)
                time_match = re.search(r"AT-TIME ([^\]\[]+)]", l)
                if city_match and time_match:
                    city = city_match.group(1).strip()
                    time = time_match.group(1).strip()
                    if "THÀNH PHỐ" in city:
                        city = city.split("-")[1]
                    city_short = self.parser.city_mappings.get(city.title(), city)
                    if time == "MẤY GIỜ":
                        conditions.append(f"(DTIME {var} {city_short} ?time)")
                    else:
                        conditions.append(f"(DTIME {var} {city_short} {time})")
            elif "TO-LOC" in l and "AT-TIME" in l:
                city_match = re.search(r"TO-LOC ([^\]\[]+)]", l)
                time_match = re.search(r"AT-TIME ([^\]\[]+)]", l)
                if city_match and time_match:
                    city = city_match.group(1).strip()
                    time = time_match.group(1).strip()
                    if "THÀNH PHỐ" in city:
                        city = city.split("-")[1]
                    city_short = self.parser.city_mappings.get(city.title(), city)
                    conditions.append(f"(ATIME {var} {city_short} {time})")
            elif "TO-LOC" in l and "AT-TIME" not in l:
                city_match = re.search(r"TO-LOC ([^\]\[]+)]", l)
                if city_match:
                    city = city_match.group(1).strip()
                    if "THÀNH PHỐ" in city:
                        city = city.split("-")[1]
                    city_short = self.parser.city_mappings.get(city.title(), city)
                    conditions.append(f"(ATIME {var} {city_short} ?time)")
        return ["PRINT-ALL", var] + conditions
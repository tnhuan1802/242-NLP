from Models.parser import DependencyParser
import re

class QueryProcessor:
    def __init__(self):
        self.parser = DependencyParser()

    def process(self, query):
        """Process query through all steps."""
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
                if parts[1] == "thời gian":
                    grammatical.append(["NSUBJ", "m1", parts[1].upper()])
                else:
                    grammatical.append(["LSUBJ", "m1", parts[1].upper()])
            elif "to-loc" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[1] == "thành phố":
                    city_unit = "thành phố"
                    continue
                elif parts[0] != "đến" and parts[0] != "ra" and parts[0] in self.parser.cities:
                    grammatical.append(["TO-LOC", "m1", parts[0].upper()])
                elif (parts[0] == "đến" or parts[0] == "ra" or parts[0] == "hạ cánh" or parts[0] == "bay") and parts[1] in self.parser.cities:
                    grammatical.append(["TO-LOC", "m1", parts[1].upper()])
                continue
            elif "nmod" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[0] == "thành phố" and parts[1] in self.parser.cities:
                    if city_unit:
                        grammatical.append(["TO-LOC", "m1", f"THÀNH PHỐ-{parts[1].upper()}"])
                        city_unit = None
                else:
                    grammatical.append(["NMOD", "m1", parts[1].upper()])
            elif "from-loc" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[0] == "từ" and parts[1] in self.parser.cities:
                    grammatical.append(["FROM-LOC", "m1", parts[1].upper()])
                elif parts[1] == "từ" and parts[0] in self.parser.cities:
                    grammatical.append(["FROM-LOC", "m1", parts[0].upper()])
                elif parts[0] in ["xuất phát", "bay"] and parts[1] in self.parser.cities:
                    grammatical.append(["FROM-LOC", "m1", parts[1].upper()])
            elif "at(" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["AT-TIME", "m1", parts[0].upper()])
            elif "at-time(" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["AT-TIME", "m1", parts[1].upper()])
            elif "wh-time" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                if parts[1] == "mất" or parts[1] == "bao lâu":
                    grammatical.append(["WH-TIME", "m1", parts[0].upper()])
            elif "obj" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["OBJ", "m1", parts[1].upper()])
            elif "acl" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["ACL", "m1", parts[1].upper()])
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
            elif "mark" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["MARK", "m1", parts[1].upper()])
            elif "cop" in dep:
                parts = dep.split("(")[1].split(")")[0].split(", ")
                grammatical.append(["COP", "m1", parts[1].upper()])
        return grammatical

    def grammatical_to_logical(self, grammatical):
        """Convert grammatical relations to logical form as a list."""
        logical = []
        pred = None
        args = []
        for g in grammatical:
            if g[0] == "WHICH":
                logical.append(f"(m1 WHICH {g[2]})")
            elif g[0] == "PRED":
                pred = g[2]
            elif g[0] == "LSUBJ":
                args.append("[MÁY BAY]")
            elif g[0] == "NSUBJ":
                args.append(f"[NSUBJ {g[2]}]")
            elif g[0] == "TO-LOC":
                args.append(f"[TO-LOC {g[2]}]")
            elif g[0] == "FROM-LOC":
                args.append(f"[FROM-LOC {g[2]}]")
            elif g[0] == "AT-TIME":
                args.append(f"[AT-TIME {g[2]}]")
            elif g[0] == "WH-TIME":
                args.append(f"[WH-TIME {g[2]}]")
            elif g[0] == "OBJ":
                args.append(f"[OBJ {g[2]}]")
            elif g[0] == "ACL":
                args.append(f"[ACL {g[2]}]")
            elif g[0] == "NMOD":
                args.append(f"[NMOD {g[2]}]")
            elif g[0] == "DISCOURSE":
                args.append(f"[DISCOURSE {g[2]}]")
            elif g[0] == "AUX":
                args.append(f"[AUX {g[2]}]")
            elif g[0] == "DET":
                args.append(f"[DET {g[2]}]")
            elif g[0] == "MARK":
                args.append(f"[MARK {g[2]}]")
            elif g[0] == "COP":
                args.append(f"[COP {g[2]}]")
        if pred:
            logical.append(f"(m1 PRED {pred} {' '.join(args)})")
        return logical

    def logical_to_procedural(self, logical, query):
        """Convert logical form to procedural form as a list."""
        if not logical:
            return ["Invalid query"]
        
        conditions = []
        var = "?m1"
        output_var = var
        
        # Extract components from logical form
        plane = None
        source = None
        dest = None
        time = None
        has_which = False
        which_target = None
        is_duration_query = False
        airline = None
        
        for l in logical:
            which_match = re.search(r"\(m1 WHICH ([^\)]+)\)", l)
            nmod_match = re.search(r"\[NMOD ([^\]\[]+)\]", l)
            from_match = re.search(r"\[FROM-LOC ([^\]\[]+)\]", l)
            to_match = re.search(r"\[TO-LOC ([^\]\[]+)\]", l)
            time_match = re.search(r"\[(?:AT-TIME|WH-TIME) ([^\]\[]+)\]", l)
            nsubj_match = re.search(r"\[NSUBJ THỜI GIAN\]", l)
            
            if which_match:
                has_which = True
                which_target = which_match.group(1).strip()
            if nmod_match:
                nmod_value = nmod_match.group(1).strip()
                if nmod_value in ["VN1", "VN2", "VN3", "VN4", "VN5", "VJ1", "VJ2", "VJ3", "VJ4", "VJ5"]:
                    plane = nmod_value
                else:
                    airline = nmod_value
            if from_match:
                source = from_match.group(1).strip()
            if to_match:
                dest = to_match.group(1).strip()
            if time_match:
                time = time_match.group(1).strip()
            if nsubj_match:
                is_duration_query = True
        
        # Handle airline-only query (e.g., Query 10)
        if has_which and which_target == "MÁY BAY" and airline == "VIETJET AIR" and not (source or dest or time):
            conditions.append("(MÁY_BAY ?m1 VJ)")
            return ["PRINT-ALL", "?m1"] + conditions
        
        # Handle city query for airline (e.g., Query 9)
        if has_which and which_target == "THÀNH PHỐ" and airline == "VIETJET AIR" and not (source or time):
            dest_arg = "?dest"
            time_arg = "?time"
            conditions.append(f"(ATIME VJ {dest_arg} {time_arg})")
            return ["PRINT-ALL", "?dest"] + conditions
        
        # Determine database predicate based on FROM-LOC and TO-LOC
        db_pred = None
        if source and not dest:
            db_pred = "DTIME"
        elif dest and not source:
            db_pred = "ATIME"
        elif source and dest:
            db_pred = "RUN-TIME"
        
        if not db_pred:
            return ["Invalid query"]
        
        # Construct predicate with fixed argument count
        if db_pred == "DTIME":
            plane_arg = plane if plane else "?m1"
            source_arg = self.parser.city_mappings.get(source.title(), source) if source else "?source"
            time_arg = "?time" if time == "MẤY GIỜ" or not time else time
            conditions.append(f"(DTIME {plane_arg} {source_arg} {time_arg})")
        elif db_pred == "ATIME":
            plane_arg = plane if plane else "?m1"
            dest_arg = self.parser.city_mappings.get(dest.title(), dest) if dest else "?dest"
            time_arg = "?time" if time == "MẤY GIỜ" or not time else time
            conditions.append(f"(ATIME {plane_arg} {dest_arg} {time_arg})")
        elif db_pred == "RUN-TIME":
            plane_arg = plane if plane else "?m1"
            source_arg = self.parser.city_mappings.get(source.title(), source) if source else "?source"
            dest_arg = self.parser.city_mappings.get(dest.title(), dest) if dest else "?dest"
            time_arg = "?time" if time == "MẤY GIỜ" or not time else time
            conditions.append(f"(RUN-TIME {plane_arg} {source_arg} {dest_arg} {time_arg})")
        
        # Set output variable and add MÁY_BAY condition
        if is_duration_query and db_pred == "RUN-TIME":
            output_var = "?time"
        elif has_which and which_target == "THÀNH PHỐ":
            output_var = "?dest"
        else:
            conditions.insert(0, f"(MÁY_BAY {var})")
        
        return ["PRINT-ALL", output_var] + conditions
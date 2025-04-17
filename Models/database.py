class FlightDatabase:
    def __init__(self, db_file):
        self.data = {"MÁY_BAY": [], "ATIME": [], "DTIME": [], "RUN-TIME": []}
        self.load_data(db_file)

    def load_data(self, db_file):
        """Load data from file."""
        try:
            with open(db_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("(MÁY_BAY"):
                        self.data["MÁY_BAY"].append(line.split()[1].strip(")"))
                    elif line.startswith("(ATIME"):
                        parts = line.split()
                        self.data["ATIME"].append((parts[1], parts[2], parts[3].strip(")")))
                    elif line.startswith("(DTIME"):
                        parts = line.split()
                        self.data["DTIME"].append((parts[1], parts[2], parts[3].strip(")")))
                    elif line.startswith("(RUN-TIME"):
                        parts = line.split()
                        self.data["RUN-TIME"].append((parts[1], parts[2], parts[3], parts[4].strip(")")))
        except FileNotFoundError:
            raise Exception("Database file not found")

    def parse_condition(self, condition):
        """Parse a condition string into predicate and arguments."""
        if not condition.startswith("(") or not condition.endswith(")"):
            return None, []
        content = condition[1:-1].strip()
        parts = content.split()
        if not parts:
            return None, []
        return parts[0], parts[1:]

    def query(self, procedure):
        """Query database based on procedural form list, handling variables."""
        if not procedure or procedure[0] not in ["PRINT-ALL"]:
            return "Invalid query"
        
        if len(procedure) < 2:
            return "Invalid query"
        
        conditions = procedure[2:]
        output_var = procedure[1]
        
        results = set()
        for condition in conditions:
            pred, args = self.parse_condition(condition)
            if not pred:
                continue
            if pred == "MÁY_BAY" and len(args) == 1:
                results = {p for p in self.data["MÁY_BAY"]}
            elif pred == "MÁY_BAY" and len(args) == 2 and args[1].startswith("VJ"):
                results = {p for p in self.data["MÁY_BAY"] if p.startswith("VJ")}
            elif pred == "ATIME" and len(args) >= 2:
                plane = args[0] if not args[0].startswith("?") else None
                city = args[1] if len(args) > 1 and not args[1].startswith("?") else None
                time = args[2] if len(args) > 2 and not args[2].startswith("?") else None
                matching_results = []
                if output_var == "?dest":
                    if not plane and not time:
                        matching_results = sorted(list({c for p, c, t in self.data["ATIME"] if (not results or p in results)}))
                        return matching_results if matching_results else "No results found"
                    elif plane and not time:
                        matching_results = sorted(list({c for p, c, t in self.data["ATIME"] if plane in p }))
                        return matching_results if matching_results else "No results found"
                matching_planes = set(self.data["MÁY_BAY"]) if not results else results
                if plane:
                    matching_planes = {p for p, c, t in self.data["ATIME"] if p == plane}
                if city:
                    matching_planes &= {p for p, c, t in self.data["ATIME"] if c == city}
                if time:
                    matching_planes &= {p for p, c, t in self.data["ATIME"] if t == time}
                results = matching_planes
            elif pred == "DTIME" and len(args) >= 2:
                plane = args[0] if not args[0].startswith("?") else None
                city = args[1] if len(args) > 1 and not args[1].startswith("?") else None
                time = args[2] if len(args) > 2 and not args[2].startswith("?") else None
                time_var = args[2] if len(args) > 2 and args[2].startswith("?") else None
                matching_results = []
                if city:
                    if time_var:
                        matching_results = [(p, t) for p, c, t in self.data["DTIME"] if c == city and (not results or p in results)]
                    else:
                        matching_planes = {p for p, c, t in self.data["DTIME"] if c == city and (time is None or t == time)}
                        results = matching_planes if not results else results & matching_planes
                if time_var and matching_results:
                    results = sorted(matching_results, key=lambda x: x[0])
                    return results if results else "No results found"
            elif pred == "RUN-TIME" and len(args) >= 2:
                plane = args[0] if not args[0].startswith("?") else None
                source = args[1] if len(args) > 1 and not args[1].startswith("?") else None
                dest = args[2] if len(args) > 2 and not args[2].startswith("?") else None
                time = args[3] if len(args) > 3 and not args[3].startswith("?") else None
                time_var = args[3] if len(args) > 3 and args[3].startswith("?") else None
                variable_count = sum(1 for arg in [plane, source, dest, time] if arg is None or arg.startswith("?"))
                matching_planes = set(self.data["MÁY_BAY"]) if not results else results
                if variable_count == 3:
                    results = sorted([(p, s, d, t) for p, s, d, t in self.data["RUN-TIME"]])
                    return results if results else "No results found"
                elif time_var and plane:
                    times = sorted(list({t for p, s, d, t in self.data["RUN-TIME"] if p == plane and (not source or s == source) and (not dest or d == dest)}))
                    return times if times else "No results found"
                else:
                    if source:
                        matching_planes &= {p for p, s, d, t in self.data["RUN-TIME"] if s == source}
                    if dest:
                        matching_planes &= {p for p, s, d, t in self.data["RUN-TIME"] if d == dest}
                    if time:
                        matching_planes &= {p for p, s, d, t in self.data["RUN-TIME"] if t == time}
                    results = matching_planes
            else:
                return "Invalid query"
        results = sorted(list(results))
        
        return results if results else "No results found"
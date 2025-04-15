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
        if not procedure or procedure[0] != "PRINT-ALL":
            return "Invalid query"
        
        if len(procedure) < 2:
            return "Invalid query"
        var = procedure[1]
        conditions = procedure[2:]
        
        results = []
        for condition in conditions:
            pred, args = self.parse_condition(condition)
            print(condition)
            if not pred:
                continue
            if pred == "MÁY_BAY" and len(args) == 1:
                var = args
                results = {p for p in self.data["MÁY_BAY"]}
            elif pred == "ATIME" and len(args) >= 2:
                plane_var = args[0]
                city = args[1] if len(args) > 1 and not args[1].startswith("?") else None
                time = args[2] if len(args) > 2 and not args[2].startswith("?") else None
                print(args, city, time)
                matching_results = results
                if city:
                    matching_results &= {p for p, c, t in self.data["ATIME"] if c == city}
                if time:
                    matching_results &= {p for p, c, t in self.data["ATIME"] if t == time}
                results &= matching_results
            elif pred == "DTIME" and len(args) >= 2:
                plane_var = args[0]
                city = args[1] if len(args) > 1 and not args[1].startswith("?") else None
                time = args[2] if len(args) > 2 and not args[2].startswith("?") else None
                time_var = args[2] if len(args) > 2 and args[2].startswith("?") else None
                matching_results = []
                if city:
                    if time_var:  # Return plane-time pairs if time is a variable
                        matching_results = [(p, t) for p, c, t in self.data["DTIME"] if c == city and p in results]
                        print(matching_results)
                    else:  # Filter results by concrete time
                        matching_results = {p for p, c, t in self.data["DTIME"] if c == city and (time is None or t == time)}
                        results &= matching_results
                if time_var and matching_results:
                    results = sorted(matching_results, key=lambda x: x[0])
                    return results if results else "No results found"
            elif pred == "RUN-TIME" and len(args) >= 2:
                plane_var = args[0]
                source = args[1] if len(args) > 1 and not args[1].startswith("?") else None
                dest = args[2] if len(args) > 2 and not args[2].startswith("?") else None
                time = args[3] if len(args) > 3 and not args[3].startswith("?") else None
                matching_results = set(self.data["MÁY_BAY"])
                if source:
                    matching_results &= {p for p, s, d, t in self.data["RUN-TIME"] if s == source}
                if dest:
                    matching_results &= {p for p, s, d, t in self.data["RUN-TIME"] if d == dest}
                if time:
                    matching_results &= {p for p, s, d, t in self.data["RUN-TIME"] if t == time}
                results &= matching_results
            else:
                return "Invalid query"
        results = sorted(list(results))
        
        return results if results else "No results found"
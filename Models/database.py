# Models/database.py
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

    def get_all_flights(self):
        """Get all unique flight IDs from ATIME, DTIME, RUN-TIME."""
        flights = set()
        for entry in self.data["ATIME"]:
            flights.add(entry[0])
        for entry in self.data["DTIME"]:
            flights.add(entry[0])
        for entry in self.data["RUN-TIME"]:
            flights.add(entry[0])
        return flights

    def query(self, procedure):
        """Query database based on procedural form."""
        if not procedure:
            return "Invalid query"
        
        command, var, *conditions = procedure
        results = []

        if command == "TEST":
            if len(conditions) == 1:
                pred, args = self.parse_condition(conditions[0])
                if pred == "DTIME" and len(args) >= 2:
                    plane, city = args[0], args[1]
                    time = args[2] if len(args) > 2 else "?"
                    if any(p == plane and c == city and (time == "?" or t == time) for p, c, t in self.data["DTIME"]):
                        return f"Yes, {plane} departs from {city}"
                    return f"No, {plane} does not depart from {city}"
            return "Invalid query"

        if command == "PRINT-ALL":
            # Start with all flights from ATIME, DTIME, RUN-TIME
            planes = self.get_all_flights()
            for condition in conditions:
                pred, args = self.parse_condition(condition)
                if not pred:
                    continue
                if pred == "MÁY_BAY":
                    continue  # Already started with all flights
                elif pred == "ATIME" and len(args) >= 3:
                    plane_var, city, time = args
                    matching_planes = {p for p, c, t in self.data["ATIME"] if c == city and (time == "?" or t == time)}
                    planes &= matching_planes
                elif pred == "RUN-TIME" and len(args) >= 4:
                    plane_var, source, dest, time = args
                    matching_planes = {p for p, s, d, t in self.data["RUN-TIME"] if s == source and d == dest and (time == "?" or t == time)}
                    planes &= matching_planes
                elif pred == "DTIME" and len(args) >= 3:
                    plane_var, city, time = args
                    matching_planes = {p for p, c, t in self.data["DTIME"] if c == city and (time == "?" or t == time)}
                    planes &= matching_planes
            results = sorted(list(planes))
        
        if any("?" in str(cond) for cond in conditions):
            time_results = []
            for condition in conditions:
                pred, args = self.parse_condition(condition)
                if pred == "RUN-TIME" and len(args) >= 4 and args[3] == "?":
                    plane_var, source, dest, _ = args
                    for p, s, d, t in self.data["RUN-TIME"]:
                        if p in results and s == source and d == dest:
                            time_results.append(f"{p}: {t}")
            if time_results:
                return time_results
        return results if results else "No results found"
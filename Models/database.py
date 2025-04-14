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

    def query(self, procedure):
        """Query database based on procedural form list."""
        if not procedure or procedure[0] != "PRINT-ALL":
            return "Invalid query"
        
        # Parse procedure list
        if len(procedure) < 2:
            return "Invalid query"
        var = procedure[1]
        conditions = procedure[2:]
        
        results = []
        # Start with all flights from ATIME
        planes = {p for p, _, _ in self.data["ATIME"]}
        for condition in conditions:
            pred, args = self.parse_condition(condition)
            if not pred:
                continue
            if pred == "MÁY_BAY":
                continue  # Already started with flights
            elif pred == "ATIME" and len(args) >= 3:
                plane_var, city, time = args
                matching_planes = {p for p, c, t in self.data["ATIME"] if c == city and t == time}
                planes &= matching_planes
            else:
                return "Invalid query"
        results = sorted(list(planes))
        
        return results if results else "No results found"
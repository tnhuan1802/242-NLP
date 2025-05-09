import os
from Models.processor import QueryProcessor
from Models.database import FlightDatabase

def write_output(filename, data):
    """Write data to output file, converting lists to strings."""
    with open(os.path.join("Output", filename), "a", encoding="utf-8") as f:
        if isinstance(data, list):
            if filename == "logical.txt":
                data_str = "".join(data)
            elif filename == "procedural.txt":
                if data[0] == "PRINT-ALL" and len(data) >= 2:
                    data_str = f"(PRINT-ALL {data[1]} {' '.join(data[2:])})"
                elif data[0] == "VERIFY" and len(data) >= 1:
                    data_str = f"(VERIFY {' '.join(data[1:])})"
                else:
                    data_str = str(data)
            elif filename == "answers.txt":
                if isinstance(data, list) and len(data) == 1 and not isinstance(data[0], tuple):
                    data_str = str(data[0])
                else:
                    data_str = str(data)
            else:
                data_str = str(data)
        else:
            data_str = str(data)
        f.write(data_str + "\n")

def main():
    os.makedirs("Output", exist_ok=True)
    for file in ["tokens.txt", "dependencies.txt", "grammatical.txt", "logical.txt", "procedural.txt", "answers.txt"]:
        open(os.path.join("Output", file), "w", encoding="utf-8").close()

    processor = QueryProcessor()
    db = FlightDatabase("Input/database.txt")

    with open("Input/query.txt", "r", encoding="utf-8") as f:
        queries = [line.strip() for line in f if line.strip()]

    for query in queries:
        result = processor.process(query)
        write_output("tokens.txt", result["tokens"])
        write_output("dependencies.txt", result["dependencies"])
        write_output("grammatical.txt", result["grammatical"])
        write_output("logical.txt", result["logical"])
        write_output("procedural.txt", result["procedural"])
        answer = db.query(result["procedural"])
        write_output("answers.txt", f"{answer}")

if __name__ == "__main__":
    main()
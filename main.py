# main.py
import os
from Models.processor import QueryProcessor
from Models.database import FlightDatabase

def write_output(filename, data):
    """Write data to output file."""
    with open(os.path.join("Output", filename), "a", encoding="utf-8") as f:
        f.write(str(data) + "\n")

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
        write_output("answers.txt", f"Query: {query}\nAnswer: {answer}\n")

if __name__ == "__main__":
    main()
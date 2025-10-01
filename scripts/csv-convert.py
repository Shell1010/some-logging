
import json, csv, pathlib

# Input/output paths
input_file = pathlib.Path("data/ioda_count.json")
output_file = pathlib.Path("data/ioda_count.csv")

with open(input_file, "r", encoding="utf-8") as f:
    data = (json.load(f))["data"]

# Expecting a list of lists
if not (isinstance(data, list) and all(isinstance(row, list) for row in data)):
    raise ValueError("Unexpected JSON structure")

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(data)


print(f"Converted {input_file} -> {output_file}")

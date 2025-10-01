
import json, csv, sys, pathlib

# Input/output paths
input_file = pathlib.Path("data/ioda_count.json")
output_file = pathlib.Path("data/ioda_count.csv")

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Normalize: if object, wrap in list
if isinstance(data, dict):
    data = [data]

if not isinstance(data, list) or not data:
    print("Unexpected JSON structure", file=sys.stderr)
    sys.exit(1)

# Flatten JSON to CSV
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)

print(f"Converted {input_file} -> {output_file}")

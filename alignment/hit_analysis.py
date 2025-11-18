import json
import os

import ROOT

# Step 1: Load the selection functions and declared objects from the helper script.
ROOT.gInterpreter.ProcessLine(".L selection.C+")

# Step 2: Load coordinates and initialize the uninitialize std::map
with open("digi_coordinates.json") as f:
    digi_coords = json.load(f)

for ch, (x, y) in digi_coords.items():
    ROOT.digiCoordMap[int(ch)] = ROOT.std.pair("float", "float")(x, y)


# Step 3: Loop over files.
search_base = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/prompt/"

found_file_path = []
for dirpath, _, filenames in os.walk(search_base):
    for filename in filenames:
        if "NANO" in filename and filename.endswith(".root"):
            full_path = os.path.join(dirpath, filename)
            found_file_path.append(full_path)

"""
# Loop over found ROOT files
for filename in found_file_path:
    print(f"Opening file: {filename}")

    # Create an RDataFrame for the "Events" tree
    rdf = ROOT.RDataFrame("Events", filename)

    # Example: print how many events are in the tree
    n_events = rdf.Count().GetValue()
    print(f"  → Number of events: {n_events}")
"""

# Debug Section
rdf = ROOT.RDataFrame("Events", found_file_path).Define("entry", "rdfentry_")
rdf_sel = (
    rdf.Filter(
        "HGCMetaData_trigTime >= 18 && HGCMetaData_trigTime <= 21", "TrigTime selection"
    )
    .Filter("UniqueLayersCheck(HGCHit_layer)", "Unique layers >= 5")
    .Filter("MaxHitsPerLayerCheck(HGCHit_layer)", "No layer with >= 4 hits")
    .Filter(
        "ArrayMatchCheck(HGCHit_layer, HGCDigi_channel)", "Layer/channel array match"
    )
    .Filter(
        "AdjacentHitsCheck(HGCHit_layer, HGCDigi_channel)",
        "Adjacent hit geometry check",
    )
)

n_total = rdf.Count().GetValue()
n_pass = rdf_sel.Count().GetValue()

print("Total events:", n_total)
print("Passed selection:", n_pass)

entries = rdf_sel.AsNumpy(["entry"])["entry"]

"""
with open("passed_event_index.txt","w") as file:
    for entry in entries:
        file.write(f"{entry}\n")
"""

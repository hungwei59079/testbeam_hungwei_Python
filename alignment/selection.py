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

print(f"found {len(found_file_path)} files. Processing......")


rdf = ROOT.RDataFrame("Events", found_file_path).Define("entry", "rdfentry_")

# Comment the previous line and uncomment the following lines if you just want to test one file.
# filename = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/prompt/NANO_112149_999.root"
# rdf = ROOT.RDataFrame("Events", filename).Define("entry", "rdfentry_")

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
    .Define("x_hits", "WeightedX(HGCHit_layer, HGCDigi_channel, HGCHit_energy)")
    .Define("y_hits", "WeightedY(HGCHit_layer, HGCDigi_channel, HGCHit_energy)")
)

print("Counting number of passed events...")

n_total = rdf.Count().GetValue()
n_pass = rdf_sel.Count().GetValue()

print("Total events:", n_total)
print("Passed selection:", n_pass)


out_file = "selected_hits.root"
out_tree = "HitCoords"  # name of the output tree

print(f"Saving selected coordinates to {out_file}...")

cols_to_save = ROOT.std.vector("string")()
cols_to_save.push_back("x_hits")
cols_to_save.push_back("y_hits")

rdf_sel.Snapshot(out_tree, out_file, cols_to_save)

print("Done. File saved.")

"""
event_index = rdf_sel.Take[rdf_sel.GetColumnType("entry")]("entry").GetValue()
coords_x = rdf_sel.Take[rdf_sel.GetColumnType("x_hits")]("x_hits").GetValue()
coords_y = rdf_sel.Take[rdf_sel.GetColumnType("y_hits")]("y_hits").GetValue()

for i in range(5):
    print(f"Event {event_index[i]}:")
    for j in range(1, 11):
        print(f"Layer {j}; X = {coords_x[i][j-1]}, Y = {coords_y[i][j-1]}")
    print("-" * 30)


#uncomment this if you want to export the entries for inspection use
with open("passed_event_index.txt","w") as file:
    for entry in entries:
        file.write(f"{entry}\n")
"""

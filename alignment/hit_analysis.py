import os

import ROOT

search_base = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/prompt/"

found_file_path = []
for dirpath, _, filenames in os.walk(search_base):
    for filename in filenames:
        if "NANO" in filename and filename.endswith(".root"):
            full_path = os.path.join(dirpath, filename)
            found_file_path.append(full_path)

# Loop over found ROOT files
for filename in found_file_path:
    print(f"Opening file: {filename}")

    # Create an RDataFrame for the "Events" tree
    rdf = ROOT.RDataFrame("Events", filename)

    # Example: print how many events are in the tree
    n_events = rdf.Count().GetValue()
    print(f"  → Number of events: {n_events}")

import argparse

import uproot

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="file_to_inspect")
parser.add_argument("start_entry", type=int, help="event_number_to_inspect")
parser.add_argument("end_entry", type=int, help="event_number_to_inspect")
args = parser.parse_args()

# --- Open the ROOT file and tree ---
with uproot.open(args.filename) as file:
    if "Events" not in file:
        raise RuntimeError("Could not find TTree 'Events' in the file.")
    tree = file["Events"]

    start_entry = int(args.start_entry)
    end_entry = int(args.end_entry)
    if start_entry >= end_entry:
        raise IndexError("end_entry has to be larger than start_entry.")
    if start_entry < 0 or end_entry >= tree.num_entries:
        raise IndexError(f"Event numbers out of range (max = {tree.num_entries - 1})")

    # --- Read only the branches you need, for a single entry ---
    arrays = tree.arrays(
        ["HGCHit_layer", "HGCHit_energy", "HGCMetaData_trigTime"],
        entry_start=start_entry,
        entry_stop=end_entry,
    )

# print(arrays)

# --- Extract the data ---
for i in range(end_entry - start_entry):
    layers = arrays["HGCHit_layer"][i]
    energies = arrays["HGCHit_energy"][i]
    trigtime = arrays["HGCMetaData_trigTime"][i]

    # --- Print info ---
    print(f"Trigger time: {trigtime}")
    print("Layers:", layers)
    print("Energies:", energies)

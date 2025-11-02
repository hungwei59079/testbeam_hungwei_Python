import argparse

import uproot

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="file_to_inspect")
parser.add_argument("event_number", type=int, help="event_number_to_inspect")
args = parser.parse_args()

# --- Open the ROOT file and tree ---
with uproot.open(args.filename) as file:
    if "Events" not in file:
        raise RuntimeError("Could not find TTree 'Events' in the file.")
    tree = file["Events"]

    entry = int(args.event_number)
    if entry < 0 or entry >= tree.num_entries:
        raise IndexError(
            f"Event number {entry} out of range (max = {tree.num_entries - 1})"
        )

    # --- Read only the branches you need, for a single entry ---
    arrays = tree.arrays(
        ["HGCHit_layer", "HGCHit_energy", "HGCMetaData_trigTime"],
        entry_start=entry,
        entry_stop=entry + 10,
    )

# print(arrays)

# --- Extract the data ---
for i in range(10):
    layers = arrays["HGCHit_layer"][i]
    energies = arrays["HGCHit_energy"][i]
    trigtime = arrays["HGCMetaData_trigTime"][i]

    # --- Print info ---
    print(f"Trigger time: {trigtime}")
    print("Layers:", layers)
    print("Energies:", energies)

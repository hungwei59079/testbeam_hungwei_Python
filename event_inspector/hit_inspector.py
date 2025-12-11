import argparse
import os
import shutil
import subprocess

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import uproot

# --- CLI setup ---
parser = argparse.ArgumentParser()
parser.add_argument(
    "--clean", help="clean up intermediate files or not", action="store_true"
)
parser.add_argument("filename", help="file_to_inspect")
parser.add_argument("start_entry", type=int, help="event_number_to_inspect")
parser.add_argument("end_entry", type=int, help="event_number_to_inspect")
args = parser.parse_args()

print(args.start_entry)
print(args.end_entry)
print(args.filename)
with uproot.open(args.filename) as file:
    if "Events" not in file:
        raise RuntimeError("Could not find TTree 'Events' in the file.")
    tree = file["Events"]

    start_entry, end_entry = args.start_entry, args.end_entry
    if start_entry >= end_entry:
        raise IndexError("end_entry has to be larger than start_entry.")
    if start_entry < 0 or end_entry >= tree.num_entries:
        raise IndexError(f"Event numbers out of range (max = {tree.num_entries - 1})")

    arrays = tree.arrays(
        [
            "HGCHit_layer",
            "HGCHit_energy",
            "HGCMetaData_trigTime",
            "HGCDigi_channel",
            "HGCDenseIndex_digiIdx",
            "HGCHit_denseIndex",
        ],
        entry_start=start_entry,
        entry_stop=end_entry,
    )

os.makedirs("inspector_output", exist_ok=True)
os.chdir("inspector_output")

for i in range(end_entry - start_entry):
    event_number = i + start_entry
    channels = arrays["HGCDigi_channel"][i]
    layers = arrays["HGCHit_layer"][i]
    energies = arrays["HGCHit_energy"][i]
    trigtime = arrays["HGCMetaData_trigTime"][i]
    DenseIndex = arrays["HGCHit_denseIndex"][i]
    Dense_to_Digi = arrays["HGCDenseIndex_digiIdx"][i]
    good_entry = True

    if len(DenseIndex) != len(layers) or len(layers) != len(energies):
        os.makedirs(f"hitplot_event_{event_number}_bad", exist_ok=True)
        print(
            f"Warning: Array size mismatch between DenseIndex, layers, and energies detected in event {event_number}. Skipping with an empty directory created."
        )
        continue

    selected_channels = []
    for dense_id in DenseIndex:
        digi_index = Dense_to_Digi[dense_id]
        if digi_index < 0 or digi_index >= len(channels):
            print(
                f"Warning: Digi_index out of range in event {event_number}. Skipping."
            )
            good_entry = False
            continue
        else:
            selected_channels.append(channels[digi_index])

    if not good_entry:
        os.makedirs(f"hitplot_event_{event_number}_bad", exist_ok=True)
        continue

    print(f"Inspecting event {event_number}, trigger time: {trigtime}")
    print(f"Layers: {layers}")
    print(f"Channels: {selected_channels}")
    print(f"Energies: {energies}")

    os.makedirs(f"hitplot_event_{event_number}/values", exist_ok=True)
    for layer in range(1, 11):
        # Extract per-layer energies here
        values = np.zeros(222)
        mask = layers == layer
        if np.any(mask):
            ch = selected_channels[mask]
            en = energies[mask]
            values[ch] = en

        # Save temporary array
        values_file = f"hitplot_event_{event_number}/values/values_layer_{layer}.txt"
        np.savetxt(values_file, values)

        name = f"hitplot_event_{event_number}/Event_{event_number}_layer_{layer}.png"  # Captalized E used intentionally. Convenient for cleaning.
        command = (
            f'root -l -b -q \'../../hexaplot_helper.C("{values_file}", "{name}")\''
        )
        print(f"Executing command: {command}")
        subprocess.call(command, shell=True)

    print("Event processing complete. Merging figures......")
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))  # 2 rows × 5 columns
    axes = axes.flatten()
    for layer in range(1, 11):
        img_path = (
            f"hitplot_event_{event_number}/Event_{event_number}_layer_{layer}.png"
        )
        img = mpimg.imread(img_path)
        axes[layer - 1].imshow(img)
        axes[layer - 1].set_title(f"Layer {layer}")
        axes[layer - 1].axis("off")

    plt.tight_layout()
    plt.savefig(f"event_{event_number}_all_layers.png", dpi=200)

    if args.clean:
        # for layer in range(1, 11):
        # os.remove(f"hitplot_event_{event_number}/Event_{event_number}_layer_{layer}.png")

        shutil.rmtree(f"hitplot_event_{event_number}")

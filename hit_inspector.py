import argparse
import logging
import os
import shutil
import subprocess

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import uproot

# --- Logger setup ---
logging.basicConfig(
    filename="hit_inspector.log",
    filemode="w",
    level=logging.DEBUG,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

# --- CLI setup ---
parser = argparse.ArgumentParser()
parser.add_argument(
    "--clean", help="clean up intermediate files or not", action="store_true"
)
parser.add_argument("filename", help="file_to_inspect")
parser.add_argument("start_entry", type=int, help="event_number_to_inspect")
parser.add_argument("end_entry", type=int, help="event_number_to_inspect")
args = parser.parse_args()

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
        ["HGCHit_layer", "HGCHit_energy", "HGCMetaData_trigTime", "HGCDigi_channel"],
        entry_start=start_entry,
        entry_stop=end_entry,
    )

os.makedirs("inspector_output", exist_ok=True)
os.chdir("inspector_output")

for i in range(end_entry - start_entry):
    channels = arrays["HGCDigi_channel"][i]
    layers = arrays["HGCHit_layer"][i]
    energies = arrays["HGCHit_energy"][i]
    trigtime = arrays["HGCMetaData_trigTime"][i]
    logger.info(f"Inspecting event {i}, trigger time: {trigtime}")
    logger.debug(f"Layers: {layers}")
    logger.debug(f"Channels: {channels}")
    logger.debug(f"Energies: {energies}")

    if len(channels) != len(layers) or len(channels) != len(energies):
        os.makedirs(f"hitplot_event_{i}_bad", exist_ok=True)
        logger.info(
            f"Warning: Array size mismatch detected in event {i}. Skipping with an empty directory created."
        )
        continue

    os.makedirs(f"hitplot_event_{i}/values", exist_ok=True)
    for layer in range(1, 11):
        # Extract per-layer energies here
        values = np.zeros(222)
        mask = layers == layer
        if np.any(mask):
            ch = channels[mask]
            en = energies[mask]
            values[ch] = en

        # Save temporary array
        values_file = f"hitplot_event_{i}/values/values_layer_{layer}.txt"
        np.savetxt(values_file, values)

        name = f"hitplot_event_{i}/Event_{i}_layer_{layer}.png"  # Captalized E used intentionally. Convenient for cleaning.
        command = f'root -l -b -q \'../hexaplot_helper.C("{values_file}", "{name}")\''
        logger.info(f"Executing command: {command}")
        subprocess.call(command, shell=True)

    logger.info("Event processing complete. Merging figures......")
    fig, axes = plt.subplots(2, 5, figsize=(15, 6))  # 2 rows × 5 columns
    axes = axes.flatten()
    for layer in range(1, 11):
        img_path = f"hitplot_event_{i}/Event_{i}_layer_{layer}.png"
        img = mpimg.imread(img_path)
        axes[layer - 1].imshow(img)
        axes[layer - 1].set_title(f"Layer {layer}")
        axes[layer - 1].axis("off")

    plt.tight_layout()
    plt.savefig(f"hitplot_event_{i}/event_{i}_all_layers.png", dpi=200)

    if args.clean:
        for layer in range(1, 11):
            os.remove(f"hitplot_event_{i}/Event_{i}_layer_{layer}.png")

        shutil.rmtree(f"hitplot_event_{i}/values")

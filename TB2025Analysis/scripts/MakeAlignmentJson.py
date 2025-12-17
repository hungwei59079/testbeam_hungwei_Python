import pandas as pd
import os
import json

runregistryfile = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/selected_runregistry_updated_validated.xlsx"

# muon runs
Runs = [
   112146, 112147, 112148, 112149
]
# Runs = [112149]

runregistry = pd.read_excel(runregistryfile, "Sheet1")
runregistry = runregistry[runregistry.Run.isin(Runs)]

specs = {"samples": {}}

for _, row in runregistry.iterrows():
    run    = int(row["Run"])
    energy = int(row["Energy"])
    outdir = str(row["Output"])

    fixed_d = outdir.replace("/v1", "/v4")
#    fixed_d = outdir.replace("/v1","/prompt")
    sample_key = f"Run{run}"

    sample = specs["samples"].setdefault(
        sample_key,
        {
            "trees": ["Events"],
            "files": [],
            "metadata": {
                "NominalEnergy": energy,
                "isMC": 0,
            },
        },
    )

    try:
        fnames = os.listdir(fixed_d)
    except FileNotFoundError:
        print(f"WARNING: directory {fixed_d} does not exist, skipping this row")
        continue

    for fname in fnames:
        if fname.startswith("NANO") and fname.endswith(".root"):
            fullpath = "root://eosuser.cern.ch/" + os.path.join(fixed_d, fname)
            if fullpath not in sample["files"]:
                sample["files"].append(fullpath)

output_dir = "configs"
os.makedirs(output_dir, exist_ok=True)

output_path = os.path.join(output_dir, "SpecAlignment.json")
with open(output_path, "w") as outfile:
    json.dump(specs, outfile, indent=4)

print("Wrote SpecAlignment.json with", len(specs["samples"]), "samples")

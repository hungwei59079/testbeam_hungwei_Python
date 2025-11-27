import pandas as pd
import os
import pprint
import json
# make spec file for energy scan

runregistryfile = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025//selected_runregistry_updated_validated.xlsx"

Runs = [112045, 112046, 112047, 112048, 112049, 112050, 112051, 112052, 112053, 112054, 112055, 112056, 112057, 112058, 112059, 112060, 112061, 112062, 112063, 112064, 112065, 112066, 112067, 112068, 112069, 112070, 112071, 112072, 112073, 112074]

runregistry = pd.read_excel(runregistryfile,"Sheet1")
runregistry = runregistry[runregistry.Run.isin(Runs)]

grouped_registry = runregistry.groupby("Energy")

specs = {"samples":{}}
for group in grouped_registry:
    Energy=group[0]
    df=group[1]
    #print("Energy",Energy)
    specs["samples"][f"Data{Energy}GeV"] = {
        "trees": ["Events"],
        "files": [],
        "metadata": {"NominalEnergy":Energy, "isMC":0}
    }

    #print("Dirs",df.Output.to_list())
    for d in df.Output.to_list():
        fixed_d = d.replace("/v1","/v3")
        fnames=[]
        try: 
            fnames = os.listdir(fixed_d)
        except FileNotFoundError:
            print(f"WARNING: The directory {fixed_d} does not exist. I will skip it")
        for fname in fnames:
            if fname.startswith("NANO") and fname.endswith(".root"):
                specs["samples"][f"Data{Energy}GeV"]["files"].append("root://eosuser.cern.ch/"+os.path.join(fixed_d,fname))
                #specs["samples"][f"Data{Energy}GeV"]["trees"].append("Events")
    #print(group)
#pprint.pprint(specs)
with open("SpecEnergyScanv3.json","w") as outfile:
    json.dump(specs,outfile,indent=3)

#print(runregistry.head())  # print first 5 rows of the dataframe

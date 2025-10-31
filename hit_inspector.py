import argparse
import ROOT

parser = argparse.ArgumentParser()
parser.add_argument("filename", help="file_to_inspect")
parser.add_argument("event_number", help="event_number_to_inspect")

args = parser.parse_args()
f1 = ROOT.TFile.Open(args.filename)
tree = f1.Get("Events")
# --- Enable only selected branches ---
tree.SetBranchStatus("*", 0)
tree.SetBranchStatus("HGCHit_layer", 1)
tree.SetBranchStatus("HGCHit_energy", 1)
tree.SetBranchStatus("HGCMetaData_trigTime", 1)

# --- Create containers to read into ---
# In PyROOT, you use ROOT.std.vector or array.array instead of raw C arrays
layer = ROOT.std.vector("int")()
energy = ROOT.std.vector("float")()
trigtime = ROOT.std.vector("unsigned int")()

# --- Set branch addresses ---
tree.SetBranchAddress("HGCHit_layer", layer)
tree.SetBranchAddress("HGCHit_energy", energy)
tree.SetBranchAddress("HGCMetaData_trigTime", trigtime)

# --- Get the desired event ---
entry = args.event_number
if entry < 0 or entry >= tree.GetEntries():
    raise IndexError(f"Event number {entry} out of range (max = {tree.GetEntries()-1})")

tree.GetEntry(entry)

# --- Print info ---
print(f"Trigger time: {trigtime}")
print("Layers:", list(layer))
print("Energies:", list(energy))

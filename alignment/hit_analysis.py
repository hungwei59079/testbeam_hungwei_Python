import json
import os
from collections import Counter

import numpy as np
import ROOT

# Step 1: Load coordinates and save them as ROOT objects
with open("digi_coordinates.json") as f:
    digi_coords = json.load(f)

ROOT.gInterpreter.Declare("""
std::map<int, std::pair<float,float>> digiCoordMap;
""")
for ch, (x,y) in digi_coords.items():
    ROOT.digiCoordMap[int(ch)] = ROOT.std.pair("float","float")(x, y)

#Step 2: C++ selection helper function.
ROOT.gInterpreter.Declare(R"cpp(

// ------------------------------------------------------------
// 1. Unique-layer selection
// Event must have >= 5 unique HGCHit_layer values
// ------------------------------------------------------------
bool UniqueLayersCheck(const std::vector<int>& layers) {
    std::set<int> uniq(layers.begin(), layers.end());
    return uniq.size() >= 5;
}

// ------------------------------------------------------------
// 2. Max-per-layer selection
// No layer can have >= 4 hits
// ------------------------------------------------------------
bool MaxHitsPerLayerCheck(const std::vector<int>& layers) {
    std::map<int,int> freq;
    for (int l : layers) freq[l]++;
    for (auto& kv : freq)
        if (kv.second >= 4)
            return false;
    return true;
}

// ------------------------------------------------------------
// 3. Size consistency check
// Arrays must be same size
// ------------------------------------------------------------
bool ArrayMatchCheck(const std::vector<int>& layers,
                     const std::vector<int>& channels)
{
    return layers.size() == channels.size();
}

// ------------------------------------------------------------
// 4. Adjacent-hit check using digiCoordMap
// For layers with 2–3 hits, check channel distance
// ------------------------------------------------------------
bool AdjacentHitsCheck(const std::vector<int>& layers,
                       const std::vector<int>& channels,
                       double maxDist = 20.0)
{
    std::map<int,int> freq;
    for (int l : layers) freq[l]++;

    for (auto& kv : freq) {
        int layer = kv.first;
        int count = kv.second;

        if (count <= 1) continue;

        if (count <= 3) {
            std::vector<int> chs;
            for (size_t i = 0; i < layers.size(); i++)
                if (layers[i] == layer)
                    chs.push_back(channels[i]);

            for (size_t i = 0; i < chs.size(); i++) {
                for (size_t j = i+1; j < chs.size(); j++) {

                    auto p1 = digiCoordMap[chs[i]];
                    auto p2 = digiCoordMap[chs[j]];

                    double dx = p1.first  - p2.first;
                    double dy = p1.second - p2.second;
                    double dist = std::sqrt(dx*dx + dy*dy);

                    if (dist > maxDist)
                        return false;
                }
            }
        }
    }

    return true;
}

)cpp");


#Step 3: Loop over files.

"""
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

"""

#Debug Section 

filename = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/prompt/NANO_112149_999.root"
rdf = ROOT.RDataFrame("Events", filename)

rdf_sel = (
    rdf
    .Filter("HGCMetaData_trigTime >= 18 && HGCMetaData_trigTime <= 21",
            "TrigTime selection")

    .Filter("UniqueLayersCheck(HGCHit_layer)",
            "Unique layers >= 5")

    .Filter("MaxHitsPerLayerCheck(HGCHit_layer)",
            "No layer with >= 4 hits")

    .Filter("ArrayMatchCheck(HGCHit_layer, HGCDigi_channel)",
            "Layer/channel array match")

    .Filter("AdjacentHitsCheck(HGCHit_layer, HGCDigi_channel)",
            "Adjacent hit geometry check")
)

n_total = rdf.Count().GetValue()
n_pass  = rdf_sel.Count().GetValue()

print("Total events:", n_total)
print("Passed selection:", n_pass)

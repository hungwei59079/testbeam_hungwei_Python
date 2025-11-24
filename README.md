## **User's guide**
This package provides several utilities for alignment analysis for HGCAL test_beam.  

### **Get_started:**
To obtain the wafermap used in `hexaplot_helper.C`, please follow the instruction on CMSSW to install `HGCAL_Commissioning` first. See more details on [link](https://gitlab.cern.ch/ykao/hgcal-comm)

After that, please follow the [instructions](https://gitlab.cern.ch/ykao/hgcal-comm/-/tree/master/DQM/extern?ref_type=heads) to create the wafermap needed. In HGCAL testbeam, ML_F is used. 

Finally, please go open `hexaplot_helper.C` and modify the following lines:
```
TString project_dir = "~/CMSSW_16_0_0_pre1/src/HGCalCommissioning/DQM/extern/";
TString wafermap_fname = project_dir + "output/geometry/geometry_ML_F_wafer.root";
```
to where you actually stored your wafermap.

### **Event_inspector:**
Creates hexaplots for each event that shows the hit position and energy in each event by muon runs. 

#### Normal mode:
Run the python script independently on login node. 
##### Usage:
```
python3 {filename} {event_start} {event_end} [--clean]
```

##### Example:
```
python3 hit_inspector.py /eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/prompt/NANO_112149_999.root 4 5 --clean
```

##### Explanation:
- `filename`: `.root` file to inspect. Currently only support single file input.
- `event_start` and `event_end`: Create hexplots for ```event_start``` to ```event_end```. For example, if one want to see the hexaplots for event 3, 4, and 5, please use `python3 {filename} 3 6`
- `--clean`: Only keep the final product.

#### Batch mode:
##### Step 1:
Open `create_job_array.py`. Right in the beginning of the document, modify the following paramters as you want:
```
filename = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/prompt/NANO_112149_999.root"
event_per_batch = 3
event_start = 0
number_of_jobs = 100
```
In the above example, after the steps are finished, the given filename will be inspected, and the hexplots for event 0~300 (300 excluded) will be generated.
After modifying the parameters, simply run:
```
python3 create_job_array.py
```
The file `hit_inspector_jobs.txt` will be created/overwritten.

##### Step 2:
Submit the jobs by:
```
condor_submit hit_inspector.sub
```
HTC condor will read the txt file just created and run the jobs using the arguments in it. `--clean` tag is used in batch mode by default to avoid flushing the repo with too many files.


### **Alignment:**
The alignment analysis is simply done by running.
```
cd alignment
python3 selection.py
python3 alignment_analysis.py
```

The first script `selection.py` selects the events, and save the coordinates of the hits in each layer of the selected events in the root file `selected_hits.root`. This script takes around ~20 mins, so don't rerun it unless it's necessary to reselect the events.

If you want to do small scale testing, you could uncomment the block 

```
# filename = "/eos/cms/store/group/dpg_hgcal/tb_hgcal/2025/SepTestBeam2025/Run112149/65ed5258-ab32-11f0-a4b8-04d9f5f94829/prompt/NANO_112149_999.root"
#rdf = ROOT.RDataFrame("Events", filename).Define("entry", "rdfentry_")
```
and the block

```
event_index = rdf_sel.Take[rdf_sel.GetColumnType("entry")]("entry").GetValue()
coords_x = rdf_sel.Take[rdf_sel.GetColumnType("x_hits")]("x_hits").GetValue()
coords_y = rdf_sel.Take[rdf_sel.GetColumnType("y_hits")]("y_hits").GetValue()

for i in range(5):
    print(f"Event {event_index[i]}:")
    for j in range(1, 11):
        print(f"Layer {j}; X = {coords_x[i][j-1]}, Y = {coords_y[i][j-1]}")
    print("-" * 30)

with open("passed_event_index.txt","w") as file:
    for entry in entries:
        file.write(f"{entry}\n")
```

to analyze one single root file and export the event indices to the event_inspector to inspect on the events.

The second script `alignment_analysis.py` make use of the produced root file, does the linear fitting in each event to retrieve residuals in each layer, and Gaussian fit on the histograms of residuals of each layer to retrieve the displacement. The fitted histograms will be exported to another root file `residual_hists.root`.



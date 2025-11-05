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

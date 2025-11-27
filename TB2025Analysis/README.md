# TB data analysis

This is a modular analysis based on RDataFrame. The user defines at runtime the modules to run, their order, and can customize by the mean of a configuration file. The master script is `Analyzer.py`.
```
usage: Analyzer.py [-h] [--infile INFILE] [--outdir OUTDIR] [--label LABEL] [--Nmax NMAX] [--eventSelection EVENTSELECTION] [--modules MODULES]
                   [--config CONFIG] [--multithread] [--dask]

optional arguments:
  -h, --help            show this help message and exit
  --infile INFILE       Json file compatible with RDataFrame::FromSpec
  --outdir OUTDIR       Output directory for plots
  --label LABEL         Additional label to identify this specific analysis iteration
  --Nmax NMAX           Maximum number of events to process
  --eventSelection EVENTSELECTION
                        Event selection, e.g. "HGCMetaData_trigTime>=116 && HGCMetaData_trigTime<=118"
  --modules MODULES     Ordered list of python modules to run
  --config CONFIG       Extra settings for the modules
  --multithread         Run in multithread, NOTE: this could saturate the memory usage
  --dask                Enable to process data with dask on HTCondor
```

## Definition of new analysis modules
The analysis modules provided as argument at runtime have to match python files with the same name under the `modules/` directory. The module should have a `run` function with a fixed set of input arguments. For example, this is a simple module which filters the events based on the number of hits in certain layers:
```
# filename: EMshowerSelection.py
import ROOT
from utils.PlottingUtils import PlotVarByChipHalf, PlotH2ByChannel
from utils.NanoUtils import DefineExtraColumns, GetInputList, GetModuleList, \
    GetH1, GetH2, GetH3, GetH4, GetProfilevsVar, GetProfile2DvsVar

def run(rdf, energies, areMC, outdir, modules, nLayers, Layer_min, Layer_max, cfg):

    nHits_min = cfg["EMshowerSelection"]["nHits_min"]
    
    rdf = rdf.Define("isMuon",f"return HGCLayer_nHits[3]<={nHits_min} && HGCLayer_nHits[4]<={nHits_min} && HGCLayer_nHits[5]<={nHits_min};")
    rdf = rdf.Define("isEarlyShower","return false;") #FIXME: TO DO
    rdf = rdf.Define("isGoodShower", "return (!isMuon) && (!isEarlyShower);")
    # TODO: the selections should be optimized.
    # Plots of energy sums before vs after the shower selection will help this optimization 

    rdf = rdf.Filter("isGoodShower")    
    return rdf

```

## Example 1: Energy study of EM showers
```
python3 Analyzer.py --infile configs/SpecEnergyScanv3.json --modules EMshowerSelection,EnergyStudy  --outdir ./ --eventSelection "HGCMetaData_trigTime>=116 && HGCMetaData_trigTime<=118" --config configs/ModuleSetting.yaml --multithread
```

## Example 2: Timewalk analysis
```
python3 Analyzer.py --infile configs/SpecTimingAnalysisv2.json --modules TWAnalysis  --outdir ./  --config configs/ModuleSetting.yaml
```

## Construct the Spec file
The spec file can be constructed using the utility `scripts/MakeSpecFile.py` customizing the selected runs and the grouping criteria


import ROOT
import argparse
import json
import numpy as np
import yaml
import os
from utils.NanoUtils import DefineExtraColumns, GetModuleList, GetLayersInfo

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetEndErrorSize(0)
ROOT.gStyle.SetOptStat(0)
#ROOT.gErrorIgnoreLevel=3000 # suppress TCanvas SaveAs messages 
#ROOT.gStyle.SetPaintTextFormat(".2f") # format for TH2 histos drawn with TEXT option
ROOT.gInterpreter.Declare('#include "utils/CPPUtils.h"')

#TODO:
# * support configuration file for modules -- DONE
# * support simulation -- DONE
# * module to filter events -- DONE
# * integrate timing analysis
# * cleanup utils -- DONE

parser = argparse.ArgumentParser()
parser.add_argument("--infile", help='Json file compatible with RDataFrame::FromSpec')
parser.add_argument("--outdir", help='Output directory for plots')
parser.add_argument("--label", default="", help='Additional label to identify this specific analysis iteration')
parser.add_argument("--Nmax", type=int, default=-1, help='Maximum number of events to process')
parser.add_argument("--eventSelection", default="", help='Event selection, e.g. "HGCMetaData_trigTime>=116 && HGCMetaData_trigTime<=118"')
parser.add_argument("--modules", help='Ordered list of python modules to run')
parser.add_argument("--config", default=None, help='Extra settings for the modules')
parser.add_argument("--multithread", action="store_true", default=False, help='Run in multithread, NOTE: this could saturate the memory usage')
parser.add_argument("--dask", action="store_true", default=False, help='Enable to process data with dask on HTCondor')
args=parser.parse_args()

if args.multithread:
    ROOT.ROOT.EnableImplicitMT()

if args.dask:
    raise NotImplemented("The combination Dask+FromSpec will be supported only as of ROOT v6.38")

# initialize dataframe
rdf = ROOT.RDF.Experimental.FromSpec(args.infile)

#extract layer information from a "quick" run over the data 
#Layer_max = rdf.Filter("event%100==0").Max("HGCHit_layer")
#Layer_min = rdf.Filter("event%100==0").Min("HGCHit_layer")
#Layer_max = Layer_max.GetValue()
#Layer_min = Layer_min.GetValue()
#nLayers = int(Layer_max-Layer_min+1)

#extract information on layers and modules in each layer from first nanoaod in the spec file
layers={}
with open(args.infile,"r") as fin:
    inputs = json.load(fin)
    firstkey=list(inputs["samples"].keys())[0]
    firstnano=inputs["samples"][firstkey]["files"][0]
    layers = GetLayersInfo(firstnano)

sorted_layers = list(layers.keys())
sorted_layers.sort()
print("Layer\tModule name\tReadout sequence")
for layer in sorted_layers:
    modinfo=layers[layer]
    print(f"{layer}\t{modinfo[0]}\t{modinfo[1]}")

Layer_min = sorted_layers[0]
Layer_max = sorted_layers[-1]
nLayers = int(Layer_max-Layer_min+1)

#define extra columns and apply requested selections 
rdf = DefineExtraColumns(rdf, nLayers, Layer_min, Layer_max)
if args.eventSelection:
    rdf = rdf.Filter(args.eventSelection)
if args.Nmax>0:
    rdf = rdf.Filter(f"event<{args.Nmax}") # FIXME: this ensures that events at all energies are processed but it is a bit unsafe 
    

#extract energy grid from spec file
NominalEnergies=[]
areMC=[]
with open(args.infile,"r") as fin:
    inputs = json.load(fin)
    for s,vals in inputs["samples"].items():
        NominalE = int(vals["metadata"]["NominalEnergy"])
        isMC = bool(vals["metadata"]["isMC"])
        NominalEnergies.append(NominalE)
        areMC.append(isMC)

#load cfg file with additional settings for the modules
cfg = None
if not(args.config is None):
    with open(args.config,'r') as cfgfile:
        cfg = yaml.safe_load(cfgfile)
        
# load modules and run them sequentially
for module in args.modules.split(","):
    print(f"Loading {module}")
    mod = __import__(f"modules.{module}", fromlist=[""])
    #print(mod)
    outdir=f"{args.outdir}/{args.label}/{module}/"
    os.system(f"mkdir -p {outdir}")
    rdf = mod.run(rdf, NominalEnergies=NominalEnergies, areMC=areMC, outdir=outdir, layers=layers, nLayers=nLayers, Layer_min=Layer_min, Layer_max=Layer_max, cfg=cfg)
    if rdf is None:
        raise ValueError(f"{module}.run should return a RDataFrame")

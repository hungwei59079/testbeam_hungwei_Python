import ROOT
from utils.PlottingUtils import PlotVarByChipHalf, PlotH2ByChannel
from utils.NanoUtils import DefineExtraColumns, GetInputList, GetModuleList, \
    GetH1, GetH2, GetH3, GetH4, GetProfilevsVar, GetProfile2DvsVar

def run(rdf, NominalEnergies, areMC, outdir, layers, nLayers, Layer_min, Layer_max, cfg):

    nHits_min = cfg["EMshowerSelection"]["nHits_min"]
    
    rdf = rdf.Define("isMuon",f"return HGCLayer_nHits[3]<={nHits_min} && HGCLayer_nHits[4]<={nHits_min} && HGCLayer_nHits[5]<={nHits_min};")
    rdf = rdf.Define("isEarlyShower","return false;") #FIXME: TO DO
    rdf = rdf.Define("isGoodShower", "return (!isMuon) && (!isEarlyShower);")
    # TODO: the selections should be optimized.
    # Plots of energy sums before vs after the shower selection will help this optimization 

    rdf = rdf.Filter("isGoodShower")    
    return rdf

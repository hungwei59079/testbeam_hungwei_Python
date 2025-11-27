import ROOT
import glob
import uproot
import numpy as np
from math import sqrt

def DefineExtraColumns(rdf, nLayers, Layer_min, Layer_max):
    """defines the dataframe to be used for the analysis of DIGIs in NANOAOD"""

    rdf = rdf.DefinePerSample("NominalBeamEnergy", 'rdfsampleinfo_.GetI("NominalEnergy")')
    rdf = rdf.DefinePerSample("isMC",              'rdfsampleinfo_.GetI("isMC")')

    rdf = rdf.Define('good_digiadc',              'HGCDigi_flags!=0xFFFF && HGCDigi_tctp<3') \
             .Define('good_digitot',              'HGCDigi_flags!=0xFFFF && HGCDigi_tctp==3') \
             .Define('good_digi',                 'good_digiadc || good_digitot') \
             .Define('digi_ch',                   'HGCDigi_channel[good_digi]') \
             .Define('digi_module',               'HGCDigi_fedReadoutSeq[good_digi]') \
             .Define('digi_toa',                  'HGCDigi_toa[good_digi]') \
             .Define('digi_adc',                  "HGCDigi_adc[good_digiadc]") \
             .Define('HGCDigi_toaGC',             'return floor(( HGCDigi_toa / 256));') \
             .Define('HGCDigi_toaCTDC',           'return floor(( HGCDigi_toa % int(pow(2,8)))/int(pow(2,3)));') \
             .Define('HGCDigi_toaFTDC',           'return HGCDigi_toa % int(pow(2,3));') \

    rdf = rdf.Define('HGCHit_digiIdx',            'GetDigiIdx(HGCDigi_denseIndex, HGCHit_denseIndex)') \
             .Define('HGCHit_channel',            'Take(HGCDigi_channel, HGCHit_digiIdx, (unsigned short)-1)') \
             .Define('HGCHit_module',             'Take(HGCDigi_fedReadoutSeq, HGCHit_digiIdx, (unsigned short)-1)') \
             .Define('HGCHit_toa',                'Take(HGCDigi_toa, HGCHit_digiIdx, (unsigned short)-1)') \
             .Define('HGCHit_toaGC',              'Take(HGCDigi_toaGC, HGCHit_digiIdx, (double)-1)') \
             .Define('HGCHit_toaCTDC',            'Take(HGCDigi_toaCTDC, HGCHit_digiIdx, (double)-1)') \
             .Define('HGCHit_toaFTDC',            'Take(HGCDigi_toaFTDC, HGCHit_digiIdx, (int)-1)')

    rdf = rdf.Define('HGCCluster_nmips_RawSum',   'Sum(HGCHit_nmips)') \
             .Define('HGCCluster_energy_RawSum',  'Sum(HGCHit_energy)')    
    
    rdf = rdf.Define('toa_hitfilter',             'HGCHit_toa>0') \
             .Define('HGCToaHit_channel',         'HGCHit_channel[toa_hitfilter]') \
             .Define('HGCToaHit_module',          'HGCHit_module[toa_hitfilter]') \
             .Define('HGCToaHit_layer',           'HGCHit_layer[toa_hitfilter]') \
             .Define('HGCToaHit_toa',             'HGCHit_toa[toa_hitfilter]') \
             .Define('HGCToaHit_toaGC',           'HGCHit_toaGC[toa_hitfilter]') \
             .Define('HGCToaHit_toaCTDC',         'HGCHit_toaCTDC[toa_hitfilter]') \
             .Define('HGCToaHit_toaFTDC',         'HGCHit_toaFTDC[toa_hitfilter]') \
             .Define('HGCToaHit_nmips',           'HGCHit_nmips[toa_hitfilter]')

    rdf = rdf.Define("HGCLayer_nmips_RawSum",  f"GetLayerEnergy({nLayers}, {Layer_min}, HGCHit_layer, HGCHit_nmips)") \
             .Define("HGCLayer_energy_RawSum", f"GetLayerEnergy({nLayers}, {Layer_min}, HGCHit_layer, HGCHit_energy)") \
             .Define("HGCLayer_nHits",         f"GetLayerNhits({nLayers}, {Layer_min}, HGCHit_layer)") \
             .Define("HGCLayer_layer",         f"GetLayerId({nLayers}, {Layer_min})")
    
    return rdf

def GetProfilevsVar(rdf, var_x, var_y, Nbinsx=222, xmin=0, xmax=222):
    p_model = ROOT.RDF.TProfile1DModel("p", "p", Nbinsx, xmin, xmax)
    p = rdf.Profile1D(p_model, var_x, var_y)
    return p

def GetProfile2DvsVar(rdf, var_x, var_y, var_z, Nbinsx, xmin, xmax, Nbinsy, ymin, ymax):
    p_model = ROOT.RDF.TProfile2DModel("p2", "p2", Nbinsx, xmin, xmax, Nbinsy, ymin, ymax)
    p = rdf.Profile2D(p_model, var_x, var_y, var_z)
    return p

def GetH1(rdf, var_x, Nbinsx, xmin, xmax,name='h'):
    h_model = ROOT.RDF.TH1DModel(name, name, Nbinsx, xmin, xmax)
    h = rdf.Histo1D(h_model, var_x)
    return h

def GetH2(rdf, var_x, var_y, Nbinsx, xmin, xmax, Nbinsy, ymin, ymax):
    h2_model = ROOT.RDF.TH2DModel("h2", "h2", Nbinsx, xmin, xmax, Nbinsy, ymin, ymax)
    h2 = rdf.Histo2D(h2_model, var_x, var_y)
    return h2

def GetH3(rdf, var_x, var_y, var_z, Nbinsx, xmin, xmax, Nbinsy, ymin, ymax, Nbinsz, zmin, zmax):
    h3_model = ROOT.RDF.TH3DModel("h3", "h3", Nbinsx, xmin, xmax, Nbinsy, ymin, ymax, Nbinsz, zmin, zmax)
    h3 = rdf.Histo3D(h3_model, var_x, var_y, var_z)
    return h3

def GetH4(rdf, var_x, var_y, var_z, var_t,
          Nbinsx, xmin, xmax,
          Nbinsy, ymin, ymax,
          Nbinsz, zmin, zmax,
          Nbinst, tmin, tmax):
    nbins = np.array([Nbinsx, Nbinsy, Nbinsz, Nbinst], dtype=np.int32)
    xmins = np.array([xmin, ymin, zmin, tmin], dtype=np.float64)
    xmaxs = np.array([xmax, ymax, zmax, tmax], dtype=np.float64)
    h4_model = ROOT.RDF.THnDModel("h4", "h4", 4, nbins, xmins, xmaxs)
    h4 = rdf.HistoND(h4_model, [var_x, var_y, var_z, var_t])
    return h4

def GetInputList(indir):
    return glob.glob(f"{indir}/NANO_*.root") # for now very simple but it could grow in complexity

def GetModuleList(fn):
    if fn.startswith("root://eosuser.cern.ch/"):
        fn = fn.replace("root://eosuser.cern.ch/","")
    infotree = uproot.open(f"{fn}:Runs")
    modules_branchnames = [ k for k in infotree.keys() if k.startswith("HGCTypeCodes") ]
    #print("modules_names",modules_names)
    moduleidxmap = infotree.arrays(modules_branchnames, library="np")
    moduleidxmap = { name:idx[0][0] for name,idx in moduleidxmap.items() }
    print("moduleidxmap",moduleidxmap)
    #print("moduleidxmap.values",moduleidxmap.values())
    readouseq = infotree.arrays("HGCReadout_Seq", library="np")["HGCReadout_Seq"][0]
    print("readouseq",readouseq)
    module_seqmap = { name:readouseq[idx] for name,idx in moduleidxmap.items() } 
    print("module_seqmap",module_seqmap)
    modules_branchnames.sort(key = lambda x: module_seqmap[x])
    modules_names = [ x.replace("HGCTypeCodes_","") for x in modules_branchnames ]
    return modules_names

def GetLayersInfo(fn):
    if fn.startswith("root://eosuser.cern.ch/"):
        fn = fn.replace("root://eosuser.cern.ch/","")
    print(f"Extracting layer info from {fn}")
    infotree = uproot.open(f"{fn}:Runs")
    modules_branchnames = [ k for k in infotree.keys() if k.startswith("HGCTypeCodes") ]
    #print("modules_names",modules_names)
    moduleidxmap = infotree.arrays(modules_branchnames, library="np")
    moduleidxmap = { name:idx[0][0] for name,idx in moduleidxmap.items() }
    #print("moduleidxmap",moduleidxmap)
    #print("moduleidxmap.values",moduleidxmap.values())
    readouseq = infotree.arrays("HGCReadout_Seq", library="np")["HGCReadout_Seq"][0]
    #print("readouseq",readouseq)
    layers = infotree.arrays("HGCReadout_Layer", library="np")["HGCReadout_Layer"][0]
    #print("layers",layers)
    return {layers[idx]:(name.replace("HGCTypeCodes_",""),readouseq[idx]) for name,idx in moduleidxmap.items() } #FIXME: this won't support layers with multiple modules!!!


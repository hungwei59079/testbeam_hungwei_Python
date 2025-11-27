import ROOT
import numpy as np
from utils.PlottingUtils import PlotVarByChipHalf, PlotH2ByChannel
from utils.NanoUtils import DefineExtraColumns, GetInputList, GetModuleList, \
    GetH1, GetH2, GetH3, GetH4, GetProfilevsVar, GetProfile2DvsVar

def run(rdf, energies, areMC, outdir, modules, nLayers, Layer_min, Layer_max, cfg):

    # initialize canvases for plots
    longcanvas = ROOT.TCanvas("longcanvas","longcanvas",1000,400)
    tallcanvas = ROOT.TCanvas("tallcanvas","tallcanvas",800,1000)
    squaredcanvas = ROOT.TCanvas("squaredcanvas","squaredcanvas",500,500)
    squaredcanvas.SetRightMargin(0.15)
    squaredcanvas.SetLeftMargin(0.15)
    squaredcanvas.SetBottomMargin(0.15)

    # 1st loop over events:
    #   * identify channels in the beam spot
    #   * count N toa hits per module
    #   * figure out the range of the trigtime variable
    #   * plot toa turn-on vs rechit energy for each module

    rdf_short = rdf.Filter("event%100==0")
    print(f"1st loop over events")
    p_charge_vs_ch_mod = GetProfile2DvsVar(rdf_short, 'HGCDigi_channel', 'HGCDigi_fedReadoutSeq', 'HGCHit_energy', 222, 0, 222, len(modules), 0, len(modules))
    h2_toa_mod = GetH2(rdf_short, 'modtoa', 'toa', len(modules), 0, len(modules), 1, 1, 1024)
    h2_energy_mod = GetH2(rdf_short, 'HGCDigi_fedReadoutSeq', 'HGCHit_energy', len(modules), 0, len(modules), 256, 1, 1024)
    h2_energy_mod_toa = GetH2(rdf_short, 'modtoa', 'energy', len(modules), 0, len(modules), 256, 1, 1024)
    trigtime_min = None
    trigtime_max = None
if "HGCMetaData_trigTime" in rdf_short.GetColumnNames():
    trigtime_min = rdf_short.Filter("HGCMetaData_trigTime>0").Min("HGCMetaData_trigTime")
    trigtime_max = rdf_short.Filter("HGCMetaData_trigTime>0").Max("HGCMetaData_trigTime")

# plot energy vs channel and extract the beamspot channels
beamspot_chs = {}
for imod in range(len(modules)):
    p_charge_ch = p_charge_vs_ch_mod.ProfileX(f"p_charge_vs_ch_{imod}", imod+1, imod+1)
    bincontent = [ p_charge_ch.GetBinContent(i) for i in range(1,p_charge_ch.GetNbinsX()+1) ]
    sorted_chidx = [ v[0] for v in sorted( enumerate(bincontent), key=lambda x: x[1], reverse=True )]
    print( f"The channels with largest charge in module {imod} are ",  sorted_chidx[:10] )
    beamspot_chs[imod] = sorted_chidx[:10]
    longcanvas.cd()
    p_charge_ch.SetTitle(f"Module {modules[imod]}")
    p_charge_ch.Draw()
    p_charge_ch.GetXaxis().SetTitle("Channel")
    p_charge_ch.GetYaxis().SetTitle("<Energy>")
    longcanvas.SaveAs(f"{args.outdir}/charge_vs_ch_module{imod}.png")
    longcanvas.SaveAs(f"{args.outdir}/charge_vs_ch_module{imod}.pdf")
    longcanvas.SaveAs(f"{args.outdir}/charge_vs_ch_module{imod}.root")    
    for ch in beamspot_chs[imod]:
        ROOT.selectedch.AddChannel(imod, ch)

# plot toa turn-on curve
squaredcanvas.cd()
for imod in range(len(modules)):
    h_energy = h2_energy_mod.ProjectionY(f"h_energy_mod{imod}",imod+1,imod+1)
    h_energy_toa = h2_energy_mod_toa.ProjectionY(f"h_energy_mod{imod}_toa",imod+1,imod+1)
    h_energy.SetTitle("Module {modules[imod]}")
    h_energy_toa.SetLineColor(2)
    h_energy.Draw()
    h_energy_toa.Draw("same")
    h_energy.GetXaxis().SetTitle(f"RecHit energy")
    h_energy.GetYaxis().SetTitle(f"Counts")
    l=ROOT.TLegend(0.6,0.7,0.8,0.8)
    l.AddEntry(h_energy,"All hits","l")
    l.AddEntry(h_energy,"Hits with toa")
    l.Draw()
    squaredcanvas.SaveAs(f"{args.outdir}/energy_module{imod}.png")
    squaredcanvas.SaveAs(f"{args.outdir}/energy_module{imod}.pdf")
    squaredcanvas.SaveAs(f"{args.outdir}/energy_module{imod}.root")

    h_eff = ROOT.TEfficiency(h_energy_toa,h_energy)
    h_eff.SetTitle(f"Module {modules[imod]}")
    h_eff.Draw("AP")
    ROOT.gPad.Update()
    h_eff.GetPaintedGraph().GetXaxis().SetTitle("RecHit energy")
    h_eff.GetPaintedGraph().GetYaxis().SetTitle("Toa efficiency")
    h_eff.Draw("AP")
    squaredcanvas.SaveAs(f"{args.outdir}/toa_turnon_module{imod}.png")
    squaredcanvas.SaveAs(f"{args.outdir}/toa_turnon_module{imod}.pdf")
    squaredcanvas.SaveAs(f"{args.outdir}/toa_turnon_module{imod}.root")
    
# plot N toa hits vs module
Nhits_mod = h2_toa_mod.ProjectionX("Nhits_mod", 1, h2_toa_mod.GetNbinsY())
squaredcanvas.cd()
Nhits_mod.SetMarkerStyle(20)
Nhits_mod.SetMarkerColor(1)
Nhits_mod.SetLineColor(1)
Nhits_mod.Draw("E1")
for imod in range(len(modules)):
    Nhits_mod.GetXaxis().SetBinLabel(imod+1, modules[imod])
Nhits_mod.GetYaxis().SetTitle("N toa hits")
squaredcanvas.SaveAs(f"{args.outdir}/Ntoahits_vs_module.png")
squaredcanvas.SaveAs(f"{args.outdir}/Ntoahits_vs_module.pdf")
squaredcanvas.SaveAs(f"{args.outdir}/Ntoahits_vs_module.root")

# Define energy sum of all channels in the beamspot
rdf = rdf.Define("energy_sum_beamspot", "return GetEnergySum(chtoa,modtoa,energy);")
        
# 2nd loop over events:
#   * toa distributions for each channel in the beamspot
#   * toa vs trigtime for each channel in the beamspot
#   * energy vs trigtime for each channel in the beamspot
#   * energy vs toa for each channel in the beamspot
#   * energy sum of all channels in the beamspot vs trigtime
#
# TODO: If trigtime is not available I can promote the toa in one channel to be the "trigtime"
# but I have to restrict the analysis to events with large energy deposits in that channel 

Nmax2ndloop = min(args.Nmax, 100000)
if Nmax2ndloop>0:
    rdf_short = rdf.Range(Nmax2ndloop)
else:
    rdf_short = rdf
    
h2_energytot_trigtime = None
if "HGCMetaData_trigTime" in rdf_short.GetColumnNames():
    h2_toa_trigtime = {}
    h2_energy_trigtime = {}
    trigtime_min = trigtime_min.GetValue()
    trigtime_max = trigtime_max.GetValue()
    if trigtime_min<trigtime_max:
        trigtime_range = int(trigtime_max-trigtime_min)
        h2_energytot_trigtime = GetH2(rdf_short, "HGCMetaData_trigTime", "energy_sum_beamspot", trigtime_range, trigtime_min, trigtime_max, 512, 0, 8192)
    
print(f"2nd loop over {Nmax2ndloop} events")
h3_toa_ch_mod = GetH3(rdf_short, 'modtoa', 'chtoa', 'toa',
              len(modules), 0, len(modules),
              222, 0, 222,
              1024, 0, 1024)

h3_toa_CTDC_ch_mod = GetH3(rdf_short, 'modtoa', 'chtoa', 'toa_CTDC',
                           len(modules), 0, len(modules),
                           222, 0, 222,
                           32, 0, 32)

if not(h2_energytot_trigtime is None):
    h3_energytot_trigtime_mod = GetH3(rdf_short, 'modtoa', "HGCMetaData_trigTime", "energy_sum_beamspot",
                                      len(modules), 0, len(modules),                                  
                                      trigtime_range, trigtime_min, trigtime_max,
                                      512, 0, 8192)

    h4_toa_trigtime_ch_mod = GetH4(rdf_short, 'modtoa', 'chtoa', 'HGCMetaData_trigTime', 'toa',
                                   len(modules), 0, len(modules),
                                   222, 0, 222,
                                   trigtime_range, trigtime_min, trigtime_max,
                                   1024, 0, 1024)

    h4_energy_trigtime_ch_mod = GetH4(rdf_short, 'modtoa', 'chtoa', 'HGCMetaData_trigTime', 'energy',
                                      len(modules), 0, len(modules),
                                      222, 0, 222,
                                      trigtime_range, trigtime_min, trigtime_max,
                                      256, 0, 1024)

# plot the toa distributions
PlotVarByChipHalf(h3_toa_ch_mod, modules, tallcanvas, args.outdir, label="toa", selected_channels=beamspot_chs)
PlotVarByChipHalf(h3_toa_CTDC_ch_mod, modules, tallcanvas, args.outdir, label="toa_CTDC", selected_channels=beamspot_chs)

# plot the distributions of toa vs trigtime and energy vs trigtime by channel
if not(h2_energytot_trigtime is None):
    PlotH2ByChannel(h4_energy_trigtime_ch_mod, modules, squaredcanvas, args.outdir, label="energy_vs_trigtime", selected_channels=beamspot_chs, xlabel="Trigger phase", ylabel="Energy")
    PlotH2ByChannel(h4_toa_trigtime_ch_mod, modules, squaredcanvas, args.outdir, label="toa_vs_trigtime", selected_channels=beamspot_chs, xlabel="Trigger phase", ylabel="Toa code")
            
# find the best trigtime as the value maximizing the energy sum over all channels in the beam spot of all modules
h2_energy_trigtime_tot = None
if not(h2_energytot_trigtime is None):
    squaredcanvas.cd()
    h2_energytot_trigtime.GetXaxis().SetTitle("Trigger phase")
    h2_energytot_trigtime.GetYaxis().SetTitle("Energy sum over all modules")
    p_energytot_trigtime = h2_energytot_trigtime.ProfileX("p_energytot_trigtime",2,-1)
    h2_energytot_trigtime.Draw("COLZ")
    p_energytot_trigtime.SetLineWidth(2)
    p_energytot_trigtime.SetLineColor(2)
    p_energytot_trigtime.Draw("SAME")
    besttrigtime = p_energytot_trigtime.GetXaxis().GetBinLowEdge( p_energytot_trigtime.GetMaximumBin() )
    print(f"Optimal trigtime = {besttrigtime}")
    squaredcanvas.SaveAs(f"{args.outdir}/energy_tot_vs_trigtime.png")
    squaredcanvas.SaveAs(f"{args.outdir}/energy_tot_vs_trigtime.pdf")
    squaredcanvas.SaveAs(f"{args.outdir}/energy_tot_vs_trigtime.root")

#define a rdf with cut on trigtime
if not(h2_energytot_trigtime is None):
    trigtimecutlow = besttrigtime-args.trigtimeRange
    trigtimecuthigh = besttrigtime+args.trigtimeRange
    rdf_trigtimecut = rdf.Filter(f"HGCMetaData_trigTime>={trigtimecutlow} && HGCMetaData_trigTime<={trigtimecuthigh}")
else:
    rdf_trigtimecut = rdf

#loop again over events to extract the timewalk curve
print("3rd loop")
h4_toa_energy_ch_mod = GetH4(rdf_trigtimecut, 'modtoa', 'chtoa', 'energy', 'toa',
                             len(modules), 0, len(modules),
                             222, 0, 222,
                             512, 0, 2048,
                             256, 0, 1024)

# plot the toa vs energy distribution
PlotH2ByChannel(h4_toa_energy_ch_mod, modules, squaredcanvas, args.outdir, label="toa_vs_energy", selected_channels=beamspot_chs, xlabel="Energy", ylabel="Toa code")

# extract a timewalk correction from the toa vs energy distribution
for ix in range(1,h4_toa_energy_ch_mod.GetAxis(0).GetNbins()+1):
    imod = int(h4_toa_energy_ch_mod.GetAxis(0).GetBinLowEdge(ix))
    for iy in range(1,h4_toa_energy_ch_mod.GetAxis(1).GetNbins()+1):
        ch = int(h4_toa_energy_ch_mod.GetAxis(1).GetBinLowEdge(iy))
        if not (beamspot_chs is None):
            if not( ch in beamspot_chs[imod]):
                continue
        h4_toa_energy_ch_mod.GetAxis(0).SetRange(ix,ix)
        h4_toa_energy_ch_mod.GetAxis(1).SetRange(iy,iy)
        h2_toa_energy = h4_toa_energy_ch_mod.Projection(3,2) #project 4D histogram onto its 3rd and 2nd axes, corresponding to energy and trigtime
        h_toa = h2_toa_energy.ProjectionY("_py", h2_toa_energy.GetXaxis().FindBin(args.energy_cut), -1)
        if h_toa.Integral(1,h_toa.GetNbinsX())>10:
            prob=np.array([0.5])
            q=np.array([0.])
            h_toa.GetQuantiles(1,q,prob)
            median = q[0]
            ROOT.twmediancorrs.AddCorr(imod,ch,median)

ROOT.twmediancorrs.PrintCorrs()
rdf_trigtimecut = rdf_trigtimecut.Define(f"toa_twcorr",f"return TWcorr(chtoa,modtoa,energy,toa)")        

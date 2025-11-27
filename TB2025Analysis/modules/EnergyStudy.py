import ROOT
from utils.PlottingUtils import PlotVarByChipHalf, PlotH2ByChannel
from utils.NanoUtils import GetH1, GetH2, GetH3, GetH4, GetProfilevsVar, GetProfile2DvsVar

def FillHistosFromG4sim(fn, nLayers, Layer_min, Layer_max):
    f = ROOT.TFile(fn,"READ")
    t = f.Get("energyTree")
    t.Draw("measuredE_L1+measuredE_L2+measuredE_L3+measuredE_L4+measuredE_L5+measuredE_L6+measuredE_L7+measuredE_L8+measuredE_L9+measuredE_L11>>h_sum(400,0,12000)")
    h_sum = ROOT.gDirectory.Get("h_sum")
    h_sum.SetDirectory(0)

    h2_nmips_vs_layer_mc = ROOT.TH2F("h2_nmips_vs_layer_mc","h2_nmips_vs_layer_mc", nLayers, Layer_min-0.5, Layer_max+0.5, 100, 0, 2500)
    for ilayer,MClayer in enumerate([1,2,3,4,5,6,7,8,9,11]):
        t.Draw(f"measuredE_L{MClayer}:{ilayer+Layer_min} >>+ h2_nmips_vs_layer_mc")
    h2_nmips_vs_layer_mc.SetDirectory(0)

    p_nmips_vs_layer_mc = ROOT.TProfile("p_nmips_vs_layer_mc","p_nmips_vs_layer_mc", nLayers, Layer_min-0.5, Layer_max+0.5)
    for ilayer,MClayer in enumerate([1,2,3,4,5,6,7,8,9,11]):
        t.Draw(f"measuredE_L{MClayer}:{ilayer+Layer_min} >>+ p_nmips_vs_layer_mc")
    p_nmips_vs_layer_mc.SetDirectory(0)
    
    return h_sum, h2_nmips_vs_layer_mc, p_nmips_vs_layer_mc


def run(rdf, NominalEnergies, areMC, outdir, layers, nLayers, Layer_min, Layer_max, cfg):
    ROOT.gStyle.SetPalette(ROOT.kCool)
    try:
        ROOT.RDF.Experimental.AddProgressBar(rdf)
    except:
        rdf = ROOT.RDF.AsRNode(rdf)
        ROOT.RDF.Experimental.AddProgressBar(rdf)

    Nominal2ActualBeamE = cfg["EnergyStudy"]["Nominal2ActualBeamE"] # Nominal2ActualBeamE[NominalBeamEnergy] = ActualBeamEnergy
        
    squaredcanvas = ROOT.TCanvas("squaredcanvas","squaredcanvas",500,500)
    squaredcanvas.SetRightMargin(0.15)
    squaredcanvas.SetLeftMargin(0.15)
    squaredcanvas.SetBottomMargin(0.15)
    
    hs_nmips_rawsum_data = {}
    hs_energy_rawsum_data = {}
    ps_nhits_vs_layer_data = {}
    ps_nmips_vs_layer_data = {}
    h2_nhits_vs_layer_data = {}
    h2_nmips_vs_layer_data = {}

    hs_nmips_rawsum_mc = {}
    ps_nhits_vs_layer_mc = {}
    ps_nmips_vs_layer_mc = {}
    h2_nmips_vs_layer_mc = {}    

    if "G4simInputs" in cfg["EnergyStudy"]:
        for E,fn in cfg["EnergyStudy"]["G4simInputs"].items():
            hs_nmips_rawsum_mc[E],h2_nmips_vs_layer_mc[E],ps_nmips_vs_layer_mc[E] = FillHistosFromG4sim(fn, nLayers, Layer_min, Layer_max)
            #print("E=",E,"hs_nmips_rawsum_mc[E].Integral()=",hs_nmips_rawsum_mc[E].Integral(),"hs_nmips_rawsum_mc[E].GetMean()=",hs_nmips_rawsum_mc[E].GetMean())
            #print("h2_nmips_vs_layer_mc[E].Integral()=",h2_nmips_vs_layer_mc[E].Integral())
    
    for isample,E in enumerate(NominalEnergies):
        isMC=areMC[isample]
        if not(isMC):
            hs_nmips_rawsum_data[E] = GetH1(rdf.Filter(f"NominalBeamEnergy=={E} && isMC==0"),"HGCCluster_nmips_RawSum",400,0,12000)
            hs_energy_rawsum_data[E] = GetH1(rdf.Filter(f"NominalBeamEnergy=={E} && isMC==0"),"HGCCluster_energy_RawSum",400,0,400)            
            h2_nmips_vs_layer_data[E] = GetH2(rdf.Filter(f"NominalBeamEnergy=={E} && isMC==0"),
                                              "HGCLayer_layer", "HGCLayer_nmips_RawSum",
                                              nLayers, Layer_min-0.5, Layer_max+0.5,
                                              100,0,2500)
            ps_nmips_vs_layer_data[E] = GetProfilevsVar(rdf.Filter(f"NominalBeamEnergy=={E} && isMC==0"),
                                                        "HGCLayer_layer", "HGCLayer_nmips_RawSum", nLayers, Layer_min-0.5, Layer_max+0.5 )
            h2_nhits_vs_layer_data[E] = GetH2(rdf.Filter(f"NominalBeamEnergy=={E} && isMC==0"),
                                              "HGCLayer_layer", "HGCLayer_nHits",
                                              nLayers, Layer_min-0.5, Layer_max+0.5,
                                              100,0,100)
            ps_nhits_vs_layer_data[E] = GetProfilevsVar(rdf.Filter(f"NominalBeamEnergy=={E} && isMC==0"),
                                                        "HGCLayer_layer", "HGCLayer_nHits", nLayers, Layer_min-0.5, Layer_max+0.5 )
        else:
            pass # here I should fill the histograms for MC

        
    # compare total rechit energy sum at different beam NominalEnergies 
    l=ROOT.TLegend(0.6,0.7,0.9,0.9)
    href=None
    ymax=-1
    for i,(E,h) in enumerate(hs_nmips_rawsum_data.items()):
        h = h.GetValue()
        h.SetLineWidth(2)
        print(E,"GeV; ",h.Integral()," entries; ",h.GetMean(),"of mean")
        if h.Integral()>0:
            h.Scale(1.0/h.Integral())
        if i==0:
            h.Draw("hist PLC")
            href=h
        else:
            h.Draw("hist PLC same")
        ymax=max(ymax, h.GetMaximum())
        l.AddEntry(h,f"{E} GeV", "l")
    href.GetYaxis().SetRangeUser(0,ymax*1.2)
    href.GetXaxis().SetTitle("Energy sum (N_{MIPs})")
    href.GetYaxis().SetTitle("Counts")
    h_dummyline = ROOT.TH1F("dummyline","dummyline",1,0,1)
    h_dummyline.SetLineColor(1)
    l.AddEntry(h_dummyline,"Data","l")
    h_dummymarker = ROOT.TH1F("dummymarker","dummymarker",1,0,1)
    h_dummymarker.SetMarkerColor(1)
    h_dummymarker.SetMarkerStyle(20)
    h_dummymarker.SetMarkerSize(0.5)
    l.AddEntry(h_dummymarker,"Simulation","p")
    l.Draw()
    ROOT.gPad.Update()
    for i,(E,h) in enumerate(hs_nmips_rawsum_data.items()):
        if E in hs_nmips_rawsum_mc:
            h_mc = hs_nmips_rawsum_mc[E]
            if h_mc.Integral()>0:
                h_mc.Scale(1.0/h_mc.Integral())
            h_mc.SetMarkerStyle(20)
            h_mc.SetMarkerSize(0.5)
            h_mc.SetMarkerColor( h.GetLineColor() )
            h_mc.Draw("E1 same")

    squaredcanvas.SaveAs(f"{outdir}/Esum.png")
    squaredcanvas.SaveAs(f"{outdir}/Esum.pdf")
    squaredcanvas.SaveAs(f"{outdir}/Esum.root")    

    href=None
    ymax=-1
    for i,(E,h) in enumerate(hs_energy_rawsum_data.items()):
        h = h.GetValue()
        h.SetLineWidth(2)
        print(E,"GeV; ",h.Integral()," entries; ",h.GetMean(),"of mean")
        if h.Integral()>0:
            h.Scale(1.0/h.Integral())
        if i==0:
            h.Draw("hist PLC")
            href=h
        else:
            h.Draw("hist PLC same")
        ymax=max(ymax, h.GetMaximum())
    href.GetYaxis().SetRangeUser(0,ymax*1.2)
    href.GetXaxis().SetTitle("Energy sum (GeV)")
    href.GetYaxis().SetTitle("Counts")
    l.Draw()
    squaredcanvas.SaveAs(f"{outdir}/Esum_GeV.png")
    squaredcanvas.SaveAs(f"{outdir}/Esum_GeV.pdf")
    squaredcanvas.SaveAs(f"{outdir}/Esum_GeV.root")    
    
    # compare energy deposits in each layer for different beam NominalEnergies
    href=None
    ymax=-1
    for ilayer in range(1,nLayers+1):
        histos_data={}
        for isample,E in enumerate(NominalEnergies):
            isMC=areMC[isample]
            if not(isMC):
                # extract histo of energy distribution in layer "ilayer" at beam energy "E"
                h = h2_nmips_vs_layer_data[E].ProjectionY(f"data_nmips_{E}GeV_{ilayer}",ilayer,ilayer)
                h.SetLineWidth(2)
                if h.Integral()>0:
                    h.Scale(1.0/h.Integral())
                if isample==0:
                    h.Draw("hist PLC")
                    href=h
                else:
                    h.Draw("hist PLC same")
                histos_data[E]=h
                ymax = max(ymax, h.GetMaximum())
        href.GetYaxis().SetRangeUser(0,ymax*1.3)
        href.GetXaxis().SetTitle(f"Energy in layer {Layer_min+ilayer-1} (N_{{MIPs}})")
        href.GetYaxis().SetTitle("Counts")
        l.Draw()
        ROOT.gPad.Update()
        for E,h in histos_data.items():
            if E in h2_nmips_vs_layer_mc:
                h2_mc = h2_nmips_vs_layer_mc[E]
                h_mc = h2_mc.ProjectionY(f"mc_nmips_{E}GeV_{ilayer}",ilayer,ilayer)
                if h_mc.Integral()>0:
                    h_mc.Scale(1.0/h_mc.Integral())
                h_mc.SetMarkerStyle(20)
                h_mc.SetMarkerSize(0.5)
                h_mc.SetMarkerColor( h.GetLineColor() )
                h_mc.Draw("E1 same")
        
        squaredcanvas.SaveAs(f"{outdir}/Esum_layer{Layer_min+ilayer-1}.png")
        squaredcanvas.SaveAs(f"{outdir}/Esum_layer{Layer_min+ilayer-1}.pdf")
        squaredcanvas.SaveAs(f"{outdir}/Esum_layer{Layer_min+ilayer-1}.root")

    # compare Nhits in each layer for different beam NominalEnergies
    href=None
    ymax=-1
    for ilayer in range(1,nLayers+1):
        for isample,E in enumerate(NominalEnergies):
            isMC=areMC[isample]
            if not(isMC):
                # extract histo of energy distribution in layer "ilayer" at beam energy "E"
                h = h2_nhits_vs_layer_data[E].ProjectionY(f"data_nhits_{E}GeV_{ilayer}",ilayer,ilayer)
                h.SetLineWidth(2)
                if h.Integral()>0:
                    h.Scale(1.0/h.Integral())
                if isample==0:
                    h.Draw("hist PLC")
                    href=h
                else:
                    h.Draw("hist PLC same")
                ymax = max(ymax, h.GetMaximum())
        href.GetYaxis().SetRangeUser(0,ymax*1.3)
        href.GetXaxis().SetTitle(f"Nhits in layer {Layer_min+ilayer-1}")
        href.GetYaxis().SetTitle("Counts")
        l.Draw()
        squaredcanvas.SaveAs(f"{outdir}/Nhits_layer{Layer_min+ilayer-1}.png")
        squaredcanvas.SaveAs(f"{outdir}/Nhits_layer{Layer_min+ilayer-1}.pdf")
        squaredcanvas.SaveAs(f"{outdir}/Nhits_layer{Layer_min+ilayer-1}.root")
        
    # average energy deposit vs layer for different beam NominalEnergies
    l=ROOT.TLegend(0.6,0.7,0.9,0.9)
    href=None
    ymax=-1
    for i,(E,p) in enumerate(ps_nmips_vs_layer_data.items()):
        p = p.GetValue()
        p.SetMarkerStyle(20)
        if i==0:
            p.Draw("E1 PLC PMC")
            href=p
        else:
            p.Draw("E1 PLC PMC same")
        ymax=max(ymax, p.GetMaximum())
        l.AddEntry(p,f"{E} GeV", "pl")
    href.GetYaxis().SetRangeUser(0,ymax*1.3)
    href.GetXaxis().SetTitle("Layer")
    href.GetYaxis().SetTitle("<Energy sum> (N_{MIPs})")

    h_dummymarker20 = ROOT.TH1F("dummymarker20","dummymarker20",1,0,1)
    h_dummymarker20.SetMarkerColor(1)
    h_dummymarker20.SetMarkerStyle(20)
    l.AddEntry(h_dummymarker20,"Data","pl")
    h_dummymarker33 = ROOT.TH1F("dummymarker33","dummymarker33",1,0,1)
    h_dummymarker33.SetMarkerColor(1)
    h_dummymarker33.SetMarkerStyle(33)
    l.AddEntry(h_dummymarker33,"Simulation","pl")
    
    l.Draw()
    ROOT.gPad.Update()
    for i,(E,h) in enumerate(ps_nmips_vs_layer_data.items()):
        if E in ps_nmips_vs_layer_mc:
            p_mc = ps_nmips_vs_layer_mc[E]
            p_mc.SetMarkerStyle(33)
            p_mc.SetMarkerColor( h.GetLineColor() )
            p_mc.SetLineColor( h.GetLineColor() )
            p_mc.Draw("E1 same")
    squaredcanvas.SaveAs(f"{outdir}/Esum_vs_layer.png")
    squaredcanvas.SaveAs(f"{outdir}/Esum_vs_layer.pdf")
    squaredcanvas.SaveAs(f"{outdir}/Esum_vs_layer.root")    

    # average Nhits vs layer for different beam NominalEnergies
    href=None
    ymax=-1
    for i,(E,p) in enumerate(ps_nhits_vs_layer_data.items()):
        p = p.GetValue()
        p.SetMarkerStyle(20)
        if i==0:
            p.Draw("E1 PLC PMC")
            href=p
        else:
            p.Draw("E1 PLC PMC same")
        ymax=max(ymax, p.GetMaximum())
    href.GetYaxis().SetRangeUser(0,ymax*1.3)
    href.GetXaxis().SetTitle("Layer")
    href.GetYaxis().SetTitle("<Nhits>")
    l.Draw()
    squaredcanvas.SaveAs(f"{outdir}/Nhits_vs_layer.png")
    squaredcanvas.SaveAs(f"{outdir}/Nhits_vs_layer.pdf")
    squaredcanvas.SaveAs(f"{outdir}/Nhits_vs_layer.root")    

    print(Nominal2ActualBeamE)
        

    
    return rdf

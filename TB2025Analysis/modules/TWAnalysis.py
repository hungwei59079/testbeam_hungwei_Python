import ROOT
import numpy as np
from utils.PlottingUtils import PlotVarByChipHalf, PlotH2ByChannel, GetMedianToaVSEnergy
from utils.NanoUtils import DefineExtraColumns, GetInputList, GetModuleList, \
    GetH1, GetH2, GetH3, GetH4, GetProfilevsVar, GetProfile2DvsVar


def run(rdf, NominalEnergies, areMC, outdir, layers, nLayers, Layer_min, Layer_max, cfg):

    modules=[]
    for layer in range(Layer_min, Layer_max+1):
        modules.append(layers[layer][0])
    print(modules)
    
    try:
        ROOT.RDF.Experimental.AddProgressBar(rdf)
    except:
        rdf = ROOT.RDF.AsRNode(rdf)
        ROOT.RDF.Experimental.AddProgressBar(rdf)

    ROOT.gInterpreter.Declare("""    
    struct channels
    {
    std::vector< std::pair<int,int> > chlist;
    void AddChannel(int mod, int chidx) 
    { 
    //std::cout<<"Adding "<<mod<<" "<<chidx<<std::endl;
    std::pair<int,int> ch(mod,chidx);
    chlist.push_back(ch);
    }
    bool FindChannel(int mod, int chidx) 
    {
    for( unsigned i=0; i<chlist.size(); ++i )
    if( chlist.at(i).first==mod && chlist.at(i).second==chidx )
    return true;
    return false;
    } 
    void PrintChannels()
    {
    for( unsigned i=0; i<chlist.size(); ++i )
    std::cout<<chlist.at(i).first<<" "<<chlist.at(i).second<<std::endl;
    } 
    };
    
    channels selectedch;
    """)

    
    ROOT.gStyle.SetPaintTextFormat(".2f") # format for TH2 histos drawn with TEXT option

    # initialize canvases for plots
    longcanvas = ROOT.TCanvas("longcanvas","longcanvas",1000,400)
    tallcanvas = ROOT.TCanvas("tallcanvas","tallcanvas",800,1000)
    squaredcanvas = ROOT.TCanvas("squaredcanvas","squaredcanvas",500,500)
    squaredcanvas.SetRightMargin(0.15)
    squaredcanvas.SetLeftMargin(0.15)
    squaredcanvas.SetBottomMargin(0.15)

    rdf_short = rdf.Filter("event%100==0")
    
    print(f"1st loop over events")
    p_energy_vs_ch_mod = GetProfile2DvsVar(rdf_short, 'HGCHit_channel', 'HGCHit_module', 'HGCHit_nmips', 222, 0, 222, len(modules), 0, len(modules))
    h2_toa_mod = GetH2(rdf_short,        'HGCToaHit_module', 'HGCToaHit_toa', len(modules), 0, len(modules), 1, 1, 1024)
    h2_energy_mod = GetH2(rdf_short,     'HGCHit_module', 'HGCHit_nmips', len(modules), 0, len(modules), 100, 0, 100)
    h2_energy_mod_toa = GetH2(rdf_short, 'HGCToaHit_module', 'HGCToaHit_nmips', len(modules), 0, len(modules), 100, 0, 100)
    trigtime_min = rdf_short.Filter("HGCMetaData_trigTime>0").Min("HGCMetaData_trigTime")
    trigtime_max = rdf_short.Filter("HGCMetaData_trigTime>0").Max("HGCMetaData_trigTime")

    # plot energy vs channel and extract the beamspot channels
    beamspot_chs = {}
    for imod in range(len(modules)):
        p_energy_ch = p_energy_vs_ch_mod.ProfileX(f"p_energy_vs_ch_{imod}", imod+1, imod+1)
        bincontent = [ p_energy_ch.GetBinContent(i) for i in range(1,p_energy_ch.GetNbinsX()+1) ]
        sorted_chidx = [ v[0] for v in sorted( enumerate(bincontent), key=lambda x: x[1], reverse=True )]
        print( f"The channels with largest energy in module {imod} are ",  sorted_chidx[:10] )
        beamspot_chs[imod] = sorted_chidx[:10]
        longcanvas.cd()
        p_energy_ch.SetTitle(f"Module {modules[imod]}")
        p_energy_ch.Draw()
        p_energy_ch.GetXaxis().SetTitle("Channel")
        p_energy_ch.GetYaxis().SetTitle("<Energy> (N_{MIPs})")
        longcanvas.SaveAs(f"{outdir}/energy_vs_ch_module{imod}.png")
        longcanvas.SaveAs(f"{outdir}/energy_vs_ch_module{imod}.pdf")
        longcanvas.SaveAs(f"{outdir}/energy_vs_ch_module{imod}.root")    
        for ch in beamspot_chs[imod]:
            ROOT.selectedch.AddChannel(imod, ch)

    # plot toa turn-on curve
    squaredcanvas.cd()
    for imod in range(len(modules)):
        h_energy = h2_energy_mod.ProjectionY(f"h_energy_mod{imod}",imod+1,imod+1)
        h_energy_toa = h2_energy_mod_toa.ProjectionY(f"h_energy_mod{imod}_toa",imod+1,imod+1)
        h_energy.SetTitle(f"Module {modules[imod]}")
        h_energy_toa.SetLineColor(2)
        h_energy.Draw()
        h_energy_toa.Draw("same")
        h_energy.GetXaxis().SetTitle("RecHit energy (N_{MIPs})")
        h_energy.GetYaxis().SetTitle("Counts")
        l=ROOT.TLegend(0.6,0.7,0.8,0.8)
        l.AddEntry(h_energy,"All hits","l")
        l.AddEntry(h_energy,"Hits with toa")
        l.Draw()
        squaredcanvas.SaveAs(f"{outdir}/energy_module{imod}.png")
        squaredcanvas.SaveAs(f"{outdir}/energy_module{imod}.pdf")
        squaredcanvas.SaveAs(f"{outdir}/energy_module{imod}.root")

        h_eff = ROOT.TEfficiency(h_energy_toa,h_energy)
        h_eff.SetTitle(f"Module {modules[imod]}")
        h_eff.Draw("AP")
        ROOT.gPad.Update()
        h_eff.GetPaintedGraph().GetXaxis().SetTitle("RecHit energy (N_{MIPs})")
        h_eff.GetPaintedGraph().GetYaxis().SetTitle("Toa efficiency")
        h_eff.Draw("AP")
        squaredcanvas.SaveAs(f"{outdir}/toa_turnon_module{imod}.png")
        squaredcanvas.SaveAs(f"{outdir}/toa_turnon_module{imod}.pdf")
        squaredcanvas.SaveAs(f"{outdir}/toa_turnon_module{imod}.root")
    
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
    squaredcanvas.SaveAs(f"{outdir}/Ntoahits_vs_module.png")
    squaredcanvas.SaveAs(f"{outdir}/Ntoahits_vs_module.pdf")
    squaredcanvas.SaveAs(f"{outdir}/Ntoahits_vs_module.root")

    # 2nd loop over events:
    #   * toa distributions for each channel in the beamspot
    #   * toa vs trigtime for each channel in the beamspot
    #   * energy vs trigtime for each channel in the beamspot
    #   * energy vs toa for each channel in the beamspot
    #   * energy sum of all channels in the beamspot vs trigtime
    try:
        ROOT.RDF.Experimental.AddProgressBar(rdf)
    except:
        rdf = ROOT.RDF.AsRNode(rdf)
        ROOT.RDF.Experimental.AddProgressBar(rdf)

    rdf_short = rdf.Filter("event%100==0")
    h2_energytot_trigtime = None
    h2_toa_trigtime = {}
    h2_energy_trigtime = {}
    trigtime_min = trigtime_min.GetValue()
    trigtime_max = trigtime_max.GetValue()
    if trigtime_min<trigtime_max:
        trigtime_range = int(trigtime_max-trigtime_min)
        h2_energytot_trigtime = GetH2(rdf_short, "HGCMetaData_trigTime", "HGCCluster_nmips_RawSum", trigtime_range, trigtime_min, trigtime_max, 500, 0, 2000)
    
    print(f"2nd loop over events")
    h3_toa_ch_mod = GetH3(rdf_short, 'HGCToaHit_module', 'HGCToaHit_channel', 'HGCToaHit_toa',
                          len(modules), 0, len(modules),
                          222, 0, 222,
                          1024, 0, 1024)

    h3_toa_CTDC_ch_mod = GetH3(rdf_short, 'HGCToaHit_module', 'HGCToaHit_channel', 'HGCToaHit_toaCTDC',
                               len(modules), 0, len(modules),
                               222, 0, 222,
                               32, 0, 32)

    h3_energytot_trigtime_mod = GetH3(rdf_short, 'HGCToaHit_module', "HGCMetaData_trigTime", "HGCCluster_nmips_RawSum",
                                      len(modules), 0, len(modules),                                  
                                      trigtime_range, trigtime_min, trigtime_max,
                                      512, 0, 8192)

    h4_toa_trigtime_ch_mod = GetH4(rdf_short, 'HGCToaHit_module', 'HGCToaHit_channel', 'HGCMetaData_trigTime', 'HGCToaHit_toa',
                                   len(modules), 0, len(modules),
                                   222, 0, 222,
                                   trigtime_range, trigtime_min, trigtime_max,
                                   1024, 0, 1024)

    h4_energy_trigtime_ch_mod = GetH4(rdf_short, 'HGCToaHit_module', 'HGCToaHit_channel', 'HGCMetaData_trigTime', 'HGCToaHit_nmips',
                                      len(modules), 0, len(modules),
                                      222, 0, 222,
                                      trigtime_range, trigtime_min, trigtime_max,
                                      200, 0, 500)

    # plot the toa distributions
    PlotVarByChipHalf(h3_toa_ch_mod, modules, tallcanvas, outdir, label="toa", selected_channels=beamspot_chs)
    PlotVarByChipHalf(h3_toa_CTDC_ch_mod, modules, tallcanvas, outdir, label="toa_CTDC", selected_channels=beamspot_chs)

    # plot the distributions of toa vs trigtime and energy vs trigtime by channel
    PlotH2ByChannel(h4_energy_trigtime_ch_mod, modules, squaredcanvas, outdir, label="energy_vs_trigtime", selected_channels=beamspot_chs, xlabel="Trigger phase", ylabel="Energy (N_{MIPs})")
    PlotH2ByChannel(h4_toa_trigtime_ch_mod, modules, squaredcanvas, outdir, label="toa_vs_trigtime", selected_channels=beamspot_chs, xlabel="Trigger phase", ylabel="Toa code")
            
    # find the best trigtime as the value maximizing the energy sum over all channels in the beam spot of all modules
    squaredcanvas.cd()
    h2_energytot_trigtime.GetXaxis().SetTitle("Trigger phase")
    h2_energytot_trigtime.GetYaxis().SetTitle("Energy sum over all modules (N_{MIPs})")
    p_energytot_trigtime = h2_energytot_trigtime.ProfileX("p_energytot_trigtime",2,-1)
    h2_energytot_trigtime.Draw("COLZ")
    p_energytot_trigtime.SetLineWidth(2)
    p_energytot_trigtime.SetLineColor(2)
    p_energytot_trigtime.Draw("SAME")
    besttrigtime = p_energytot_trigtime.GetXaxis().GetBinLowEdge( p_energytot_trigtime.GetMaximumBin() )
    print(f"Optimal trigtime = {besttrigtime}")
    squaredcanvas.SaveAs(f"{outdir}/energy_tot_vs_trigtime.png")
    squaredcanvas.SaveAs(f"{outdir}/energy_tot_vs_trigtime.pdf")
    squaredcanvas.SaveAs(f"{outdir}/energy_tot_vs_trigtime.root")

    #define a rdf with cut on trigtime
    besttrigtime = cfg["TWAnalysis"]["besttrigtime"]
    trigtimeRange = cfg["TWAnalysis"]["trigtimeRange"]
    trigtimecutlow = besttrigtime-trigtimeRange
    trigtimecuthigh = besttrigtime+trigtimeRange
    rdf_trigtimecut = rdf.Filter(f"HGCMetaData_trigTime>={trigtimecutlow} && HGCMetaData_trigTime<={trigtimecuthigh}")

    #loop again over events to extract the timewalk curve
    rdf_trigtimecut = ROOT.RDF.AsRNode(rdf_trigtimecut)
    ROOT.RDF.Experimental.AddProgressBar(rdf_trigtimecut)
        
    print("3rd loop")
    h4_toa_energy_ch_mod = GetH4(rdf_trigtimecut, 'HGCToaHit_module', 'HGCToaHit_channel', 'HGCToaHit_nmips', 'HGCToaHit_toa',
                                 len(modules), 0, len(modules),
                                 222, 0, 222,
                                 300, 0, 300,
                                 256, 0, 1024)

    # plot the toa vs energy distribution
    #PlotH2ByChannel(h4_toa_energy_ch_mod, modules, squaredcanvas, outdir, label="toa_vs_energy", selected_channels=beamspot_chs, xlabel="Energy (N_{MIPs})", ylabel="Toa code")

    # extract a timewalk correction from the toa vs energy distribution
    f_log = ROOT.TF1("f_log","[0]+[1]*log(x-[2])",8,300)
    f_pow= ROOT.TF1("f_pow","[0]/x+[1]",8,300)
    f_log.SetLineColor(2)
    f_log.SetLineWidth(2)
    f_pow.SetLineColor(3)
    f_pow.SetLineWidth(2)

    h_redchi2_log = ROOT.TH1F("h_redchi2_log", "h_redchi2_log", 100, 0, 5)
    h_redchi2_pow = ROOT.TH1F("h_redchi2_pow", "h_redchi2_pow", 100, 0, 5)

    h_fitstatus_log = ROOT.TH1F("h_fitstatus_log", "h_fitstatus_log", 5, -0.5, 4.5)
    h_fitstatus_pow = ROOT.TH1F("h_fitstatus_pow", "h_fitstatus_pow", 5, -0.5, 4.5)

    hs_p0_pow = {}
    hs_p1_pow = {}
    fs_pow = {}
    g_p0_p1_pow = {}

    p0_pow_min=None
    p0_pow_max=None
    p1_pow_min=None
    p1_pow_max=None

    for ix in range(1,h4_toa_energy_ch_mod.GetAxis(0).GetNbins()+1):
        imod = int(h4_toa_energy_ch_mod.GetAxis(0).GetBinLowEdge(ix))

        hs_p0_pow[imod] = ROOT.TH1F(f"h_p0_mod{imod}_pow", "h_p0_mod{imod}_pow", 100, 0, 3000)
        hs_p1_pow[imod] = ROOT.TH1F(f"h_p1_mod{imod}_pow", "h_p1_mod{imod}_pow", 100, 0, 1000)
        fs_pow[imod] = []
        g_p0_p1_pow[imod] = ROOT.TGraphErrors()
    
        for iy in range(1,h4_toa_energy_ch_mod.GetAxis(1).GetNbins()+1):
            ch = int(h4_toa_energy_ch_mod.GetAxis(1).GetBinLowEdge(iy))
            if not (beamspot_chs is None):
                if not( ch in beamspot_chs[imod]):
                    continue
            h4_toa_energy_ch_mod.GetAxis(0).SetRange(ix,ix)
            h4_toa_energy_ch_mod.GetAxis(1).SetRange(iy,iy)
            h2_toa_energy = h4_toa_energy_ch_mod.Projection(3,2) #project 4D histogram onto its 3rd and 2nd axes, corresponding to energy and trigtime
            g_medtoa_energy = GetMedianToaVSEnergy(h2_toa_energy)

            f_log.SetParameters(488, -28, 8.7)
            fitstatus = g_medtoa_energy.Fit(f_log,"RS")
            h_fitstatus_log.Fill(int(fitstatus.Status()))
            print(f"fitstatus log {int(fitstatus.Status())}")
            if int(fitstatus)==0:
                h_redchi2_log.Fill(f_log.GetChisquare()/f_log.GetNDF())
            
            f_pow.SetParameters(1265,353)
            fitstatus = g_medtoa_energy.Fit(f_pow,"RS+")
            h_fitstatus_pow.Fill(int(fitstatus.Status()))
            print(f"fitstatus pow {int(fitstatus.Status())}")
            if int(fitstatus)==0:
                h_redchi2_pow.Fill(f_pow.GetChisquare()/f_pow.GetNDF())
                hs_p0_pow[imod].Fill(f_pow.GetParameter(0))
                hs_p1_pow[imod].Fill(f_pow.GetParameter(1))
                fs_pow[imod].append(f_pow.Clone(f"f_pow_mod{imod}_ch{ch}"))
                g_p0_p1_pow[imod].SetPoint(g_p0_p1_pow[imod].GetN(), f_pow.GetParameter(0), f_pow.GetParameter(1))
                g_p0_p1_pow[imod].SetPointError(g_p0_p1_pow[imod].GetN()-1, f_pow.GetParError(0), f_pow.GetParError(1))

                if (p0_pow_min is None):
                    p0_pow_min = p0_pow_max = f_pow.GetParameter(0)
                    p1_pow_min = p1_pow_max = f_pow.GetParameter(1)
                else:
                    p0_pow_min = min(p0_pow_min, f_pow.GetParameter(0))
                    p0_pow_max = max(p0_pow_max, f_pow.GetParameter(0))
                    p1_pow_min = min(p1_pow_min, f_pow.GetParameter(1))
                    p1_pow_max = max(p1_pow_max, f_pow.GetParameter(1))
                    
            squaredcanvas.cd()
            h2_toa_energy.Draw("COLZ")
            g_medtoa_energy.SetMarkerStyle(20)
            g_medtoa_energy.SetMarkerColor(1)
            g_medtoa_energy.SetLineColor(1)
            #g_medtoa_energy.SetLineWidth(2)
            g_medtoa_energy.Draw("P same")
            squaredcanvas.SaveAs(f"{outdir}/toa_vs_energy_fit_module{imod}_ch{ch}.png")
            squaredcanvas.SaveAs(f"{outdir}/toa_vs_energy_fit_module{imod}_ch{ch}.pdf")
            squaredcanvas.SaveAs(f"{outdir}/toa_vs_energy_fit_module{imod}_ch{ch}.root")
        
            #h_toa = h2_toa_energy.ProjectionY("_py", h2_toa_energy.GetXaxis().FindBin(args.energy_cut), -1)
            #if h_toa.Integral(1,h_toa.GetNbinsX())>10:
            #    prob=np.array([0.5])
            #    q=np.array([0.])
            #    h_toa.GetQuantiles(1,q,prob)
            #    median = q[0]
            #    ROOT.twmediancorrs.AddCorr(imod,ch,median)
            h2_toa_energy.Delete()

    squaredcanvas.cd()
    h_fitstatus_pow.SetLineColor(1)
    h_fitstatus_pow.SetTitle("fit function [A]/E+[C]")
    h_fitstatus_pow.Draw()
    h_fitstatus_log.SetLineColor(2)
    h_fitstatus_log.SetTitle("fit function [A]*log(x-[B])+[C]")
    h_fitstatus_log.Draw("same")
    squaredcanvas.BuildLegend()
    squaredcanvas.Draw()
    squaredcanvas.SaveAs(f"{outdir}/fitstatus.png")
    squaredcanvas.SaveAs(f"{outdir}/fitstatus.pdf")
    squaredcanvas.SaveAs(f"{outdir}/fitstatus.root")

    squaredcanvas.cd()
    h_redchi2_pow.SetLineColor(1)
    h_redchi2_pow.SetTitle("fit function [A]/E+[C]")
    h_redchi2_pow.Draw()
    h_redchi2_log.SetLineColor(2)
    h_redchi2_log.SetTitle("fit function [A]*log(x-[B])+[C]")
    h_redchi2_log.Draw("same")
    squaredcanvas.BuildLegend()
    squaredcanvas.SaveAs(f"{outdir}/redchi2.png")
    squaredcanvas.SaveAs(f"{outdir}/redchi2.pdf")
    squaredcanvas.SaveAs(f"{outdir}/redchi2.root")

    squaredcanvas.cd()
    l = ROOT.TLegend(0.7,0.4,0.9,0.9)
    ymax=0.
    href=None
    for imod,h in hs_p0_pow.items():
        if imod==0:
            h.Draw("PLC")
            h.GetXaxis().SetTitle("A [Toa code/N_{MIPs}]")
            h.GetYaxis().SetTitle("Counts")
            ymax = h.GetMaximum()
            href=h
        else:
            h.Draw("PLC same")
            ymax = max(ymax, h.GetMaximum())
        l.AddEntry(h,f"Layer {imod}","l")
    href.GetYaxis().SetRangeUser(0,ymax*1.25)
    l.Draw()
    squaredcanvas.SaveAs(f"{outdir}/h_p0_pow.png")
    squaredcanvas.SaveAs(f"{outdir}/h_p0_pow.pdf")
    squaredcanvas.SaveAs(f"{outdir}/h_p0_pow.root")

    squaredcanvas.cd()
    ymax=0.
    href=None
    for imod,h in hs_p1_pow.items():
        if imod==0:
            h.Draw("PLC")
            h.GetXaxis().SetTitle("C [Toa code]")
            h.GetYaxis().SetTitle("Counts")
            ymax = h.GetMaximum()
            href=h
        else:
            h.Draw("PLC same")
            ymax = max(ymax, h.GetMaximum())        
    href.GetYaxis().SetRangeUser(0,ymax*1.25)
    l.Draw()
    squaredcanvas.SaveAs(f"{outdir}/h_p1_pow.png")
    squaredcanvas.SaveAs(f"{outdir}/h_p1_pow.pdf")
    squaredcanvas.SaveAs(f"{outdir}/h_p1_pow.root")

    squaredcanvas.cd()
    href=squaredcanvas.DrawFrame(0.9*p0_pow_min, 0.9*p1_pow_min, 1.3*p0_pow_max, 1.1*p1_pow_max)
    href.GetXaxis().SetTitle("A [Toa code/N_{MIPs}]")
    href.GetYaxis().SetTitle("C [Toa code]")
    l = ROOT.TLegend(0.7,0.4,0.9,0.9)
    for imod,g in g_p0_p1_pow.items():
        g.SetMarkerStyle(20)
        g.Draw("P PLC PMC same")
        l.AddEntry(g,f"Layer {imod}","pl")    
    l.Draw()
    squaredcanvas.SaveAs(f"{outdir}/g_p0_p1_pow.png")
    squaredcanvas.SaveAs(f"{outdir}/g_p0_p1_pow.pdf")
    squaredcanvas.SaveAs(f"{outdir}/g_p0_p1_pow.root")


    squaredcanvas.cd()
    for imod,fs in fs_pow.items():
        for idxf,f in enumerate(fs):
            if idxf==0:
                #f.SetFillStyle(3003)
                f.Draw("")
            else:
                f.Draw("same")
        squaredcanvas.SaveAs(f"{outdir}/f_pow_mod{imod}.png")
        squaredcanvas.SaveAs(f"{outdir}/f_pow_mod{imod}.pdf")
        squaredcanvas.SaveAs(f"{outdir}/f_pow_mod{imod}.root")
        

    return rdf


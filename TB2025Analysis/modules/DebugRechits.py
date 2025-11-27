import ROOT
from utils.PlottingUtils import PlotVarByChipHalf, PlotH2ByChannel
from utils.NanoUtils import DefineExtraColumns, GetInputList, GetModuleList, \
    GetH1, GetH2, GetH3, GetH4, GetProfilevsVar, GetProfile2DvsVar

def run(rdf, NominalEnergies, areMC, outdir, layers, nLayers, Layer_min, Layer_max, cfg):
    squaredcanvas = ROOT.TCanvas("squaredcanvas","squaredcanvas",500,500)
    squaredcanvas.SetRightMargin(0.15)
    squaredcanvas.SetLeftMargin(0.15)
    squaredcanvas.SetBottomMargin(0.15)

    hs_nmips_rawsum = {}
    for E in NominalEnergies:
        hs_nmips_rawsum[E] = GetH1(rdf.Filter(f"NominalBeamEnergy=={E}"),"HGCCluster_nmips_RawSum",400,12400,12800)

    rdf = rdf.Define('HGCHit_digiIdx',            'GetDigiIdx(HGCDigi_denseIndex, HGCHit_denseIndex)') \
             .Define('HGCHit_adc',                'Take(HGCDigi_adc, HGCHit_digiIdx, (unsigned short)0)') \
             .Define('HGCHit_tot',                'Take(HGCDigi_tot, HGCHit_digiIdx, (unsigned short)0)') \
             .Define('HGCHit_tctp',               'Take(HGCDigi_tctp, HGCHit_digiIdx, (unsigned short)4)')
             #.Define('HGCHit_adc',                'Take(HGCDigi_adc, HGCHit_denseIndex)') \
             #.Define('HGCHit_tot',                'Take(HGCDigi_tot, HGCHit_denseIndex)') \
             #.Define('HGCHit_tctp',               'Take(HGCDigi_tctp, HGCHit_denseIndex)')


    
    #rdf = rdf.Define('HGCHit_adc',               'MatchDigiToHit(HGCDigi_adc, HGCDigi_denseIndex, HGCHit_denseIndex)') \
    #         .Define('HGCHit_tot',               'MatchDigiToHit(HGCDigi_tot, HGCDigi_denseIndex, HGCHit_denseIndex)') \
    #         .Define('HGCHit_tctp',              'MatchDigiToHit(HGCDigi_tctp, HGCDigi_denseIndex, HGCHit_denseIndex)')

    rdf = rdf.Define('good_hitadc',              'HGCHit_tctp<3') \
             .Define('good_hittot',              'HGCHit_tctp==3')
    
    rdf = rdf.Define('HGCTotHit_tot',      'HGCHit_tot[good_hittot]') \
             .Define('HGCTotHit_nmips',    'HGCHit_nmips[good_hittot]') \
             .Define('HGCAdcHit_adc',      'HGCHit_adc[good_hitadc]') \
             .Define('HGCAdcHit_nmips',    'HGCHit_nmips[good_hitadc]')

    
    #ROOT.gInterpreter.Declare("""    
    #using ROOT::RVecI;
    #using ROOT::RVecF;
    #struct PrintSuspiciousHits {
    #    void operator() (const int &event, const RVec<unsigned short> &HGCAdcHit_adc, const RVecF &HGCAdcHit_nmips)
    #    {
    #        for( unsigned iHit=0; iHit<HGCAdcHit_adc.size(); ++iHit) {
    #            float energy = HGCAdcHit_nmips[iHit];
    #            float adc = HGCAdcHit_adc[iHit]; 
    #            cout<<"energy="<<energy<<"\tadc="<<adc<<endl;
    #            if( adc>500 && energy<50 )
    #                cout<<"suspicious event number = "<<event<<endl;
    #        }
    #    }
    #};
    #""")
    #rdf.Foreach(ROOT.PrintSuspiciousHits(),["event","HGCAdcHit_adc","HGCAdcHit_nmips"]) # Define("isSuspicious","PrintSuspiciousHits(event,HGCAdcHit_adc,HGCAdcHit_nmips)")

    ROOT.gInterpreter.Declare("""    
    using ROOT::RVecI;
    using ROOT::RVecF;
    bool GetSuspiciousHits(const int &event, const RVec<unsigned short> &HGCAdcHit_adc, const RVecF &HGCAdcHit_nmips)
    {
        for( unsigned iHit=0; iHit<HGCAdcHit_adc.size(); ++iHit) {
            auto energy = HGCAdcHit_nmips[iHit];
            auto adc = HGCAdcHit_adc[iHit]; 
            if( adc>500 && energy<50 ) {
                cout<<"suspicious event number = "<<event<<endl;
                cout<<"iHit="<<iHit<<"; energy="<<energy<<"; adc="<<adc<<endl;
                return true;
            }
        }
        return false;
    }
    """)

    #ds = rdf.Filter("return GetSuspiciousHits(event,HGCAdcHit_adc,HGCAdcHit_nmips);").Display(["event"])    
    #ds.Print()
    
    rdf300 = rdf#.Filter("HGCCluster_nmips_RawSum<12650 && NominalBeamEnergy==300")
    #rdf300 = rdf.Filter("NominalBeamEnergy==300")
    #h2_E_vs_adc = GetH2(rdf300, "HGCAdcHit_adc","HGCAdcHit_nmips", 100, 0, 1024, 100, 0, 100)
    #h2_E_vs_tot = GetH2(rdf300, "HGCTotHit_tot","HGCTotHit_nmips", 100, 0, 500, 100, 0, 150)
    h2_E_vs_adc = GetH2(rdf300, "HGCAdcHit_adc","HGCAdcHit_nmips", 100, 0, 1024, 100, 0, 1024)
    h2_E_vs_tot = GetH2(rdf300, "HGCTotHit_tot","HGCTotHit_nmips", 100, 0, 500, 100, 0, 500)

    HGCAdcHit_nmips_max = rdf300.Max("HGCAdcHit_nmips")
    HGCTotHit_nmips_max = rdf300.Max("HGCTotHit_nmips")
    
    h2_E_vs_adc = h2_E_vs_adc.GetValue()
    #g_E_vs_adc.SetMarkerStyle(20)
    squaredcanvas.cd()
    h2_E_vs_adc.Draw("COLZ")
    h2_E_vs_adc.GetXaxis().SetTitle("RecHit ADC")
    h2_E_vs_adc.GetYaxis().SetTitle("RecHit Energy (N_{MIPs})")
    squaredcanvas.SaveAs(f"{outdir}/h2_E_vs_adc2.png")
    squaredcanvas.SaveAs(f"{outdir}/h2_E_vs_adc2.pdf")
    squaredcanvas.SaveAs(f"{outdir}/h2_E_vs_adc2.root")    

    #h2_E_vs_tot.SetMarkerStyle(20)
    squaredcanvas.cd()
    h2_E_vs_tot.Draw("COLZ")
    h2_E_vs_tot.GetXaxis().SetTitle("RecHit TOT")
    h2_E_vs_tot.GetYaxis().SetTitle("RecHit Energy (N_{MIPs})")
    squaredcanvas.SaveAs(f"{outdir}/h2_E_vs_tot2.png")
    squaredcanvas.SaveAs(f"{outdir}/h2_E_vs_tot2.pdf")
    squaredcanvas.SaveAs(f"{outdir}/h2_E_vs_tot2.root")    

    print("HGCAdcHit_nmips_max",HGCAdcHit_nmips_max.GetValue())
    print("HGCTotHit_nmips_max",HGCTotHit_nmips_max.GetValue())

    
        
    l=ROOT.TLegend(0.6,0.7,0.9,0.9)
    href=None
    ymax=-1
    for i,(E,h) in enumerate(hs_nmips_rawsum.items()):
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
    l.Draw()
    
    squaredcanvas.SaveAs(f"{outdir}/Esum.png")
    squaredcanvas.SaveAs(f"{outdir}/Esum.pdf")
    squaredcanvas.SaveAs(f"{outdir}/Esum.root")    



    
    return rdf

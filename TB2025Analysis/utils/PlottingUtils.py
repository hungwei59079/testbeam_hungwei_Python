import ROOT
import glob
import uproot
import numpy as np
from math import sqrt

def GetChip(ch):
    return ch//74

def GetHalf(ch):
    return int((ch//74)>36)

def PlotVarByChipHalf(h3_var_ch_mod, modules, canvas, outdir, label="", selected_channels=None):
    zmin = h3_var_ch_mod.GetZaxis().GetXmin()
    zmax = h3_var_ch_mod.GetZaxis().GetXmax()
    for ix in range(1,h3_var_ch_mod.GetNbinsX()+1):
        imod = int(h3_var_ch_mod.GetXaxis().GetBinLowEdge(ix))
        canvas.Clear()
        canvas.cd()
        canvas.Divide(2,3)
        maxs = [0]*6
    
        #initialize canvases
        hs=[]
        legends=[]
        for i in range(6):
            canvas.cd(1+i)
            hs.append(ROOT.gPad.DrawFrame(zmin,0,zmax,1))    
            hs[-1].GetXaxis().SetTitle("Toa code")
            hs[-1].GetYaxis().SetTitle("Nevents (norm=1)")
            hs[-1].SetTitle(f"(chip,half)=({i//2}, {i%2}) of {modules[imod]}")
            legends.append(ROOT.TLegend(0.7,0.7,0.85,0.85))
            
        for iy in range(1,h3_var_ch_mod.GetNbinsY()+1):
            ch = int(h3_var_ch_mod.GetYaxis().GetBinLowEdge(iy))
            if not (selected_channels is None):
                if not( ch in selected_channels[imod]):
                    continue

            h_toa = h3_var_ch_mod.ProjectionZ(f"toa_mod{imod}_ch{ch}", ix, ix, iy, iy)
        
            # normalize toa histograms
            Nev = h_toa.Integral()
            if Nev>0:
                h_toa.Scale(1.0/Nev)
            #get on the right canvas and draw 
            chip = GetChip(ch)
            half = GetHalf(ch)
            canvas.cd(1+chip*2+half)
            if h_toa.GetMaximum() > maxs[chip*2+half]:
                maxs[chip*2+half] = h_toa.GetMaximum()
            h_toa.SetLineWidth(2)
            h_toa.Draw("hist SAME pmc plc")
            legends[chip*2+half].AddEntry(h_toa,f"ch = {ch}","l")
            
        for i in range(6):
            canvas.cd(i+1)
            ROOT.gPad.RedrawAxis()
            if maxs[i]>0:
                hs[i].GetYaxis().SetRangeUser(0, 1.25*maxs[i])
            legends[i].Draw()
    
        canvas.SaveAs(f"{outdir}/{label}_module{imod}.png")
        canvas.SaveAs(f"{outdir}/{label}_module{imod}.pdf")
        canvas.SaveAs(f"{outdir}/{label}_module{imod}.root")

def PlotH2ByChannel(h4_var2_var1_ch_mod, modules, canvas, outdir, label="", selected_channels=None, xlabel=None, ylabel=None):
    for ix in range(1,h4_var2_var1_ch_mod.GetAxis(0).GetNbins()+1):
        imod = int(h4_var2_var1_ch_mod.GetAxis(0).GetBinLowEdge(ix))
        for iy in range(1,h4_var2_var1_ch_mod.GetAxis(1).GetNbins()+1):
            ch = int(h4_var2_var1_ch_mod.GetAxis(1).GetBinLowEdge(iy))
            #print("label",label,"ix",ix,"imod",imod,"iy",iy,"ch",ch)
            if not (selected_channels is None):
                if not( ch in selected_channels[imod]):
                    continue
            canvas.cd()
            h4_var2_var1_ch_mod.GetAxis(0).SetRange(ix,ix)
            h4_var2_var1_ch_mod.GetAxis(1).SetRange(iy,iy)
            h2_var2_var1 = h4_var2_var1_ch_mod.Projection(3,2) #project 4D histogram onto its 3rd and 2nd axes, corresponding to energy and trigtime 
            h2_var2_var1.SetTitle(f"ch {ch} of {modules[imod]}")
            if not(xlabel is None):
                h2_var2_var1.GetXaxis().SetTitle(xlabel)
            if not(ylabel is None):
                h2_var2_var1.GetYaxis().SetTitle(ylabel)
            h2_var2_var1.Draw("COLZ")
            canvas.SaveAs(f"{outdir}/{label}_module{imod}_ch{ch}.png")
            canvas.SaveAs(f"{outdir}/{label}_module{imod}_ch{ch}.pdf")
            canvas.SaveAs(f"{outdir}/{label}_module{imod}_ch{ch}.root")

def GetMedianToaVSEnergy(h2_toa_energy, Nmin=100, Nmin_lastbin=30):

    def quantile_from_histogram(cdf, bin_edges, q):
        return np.interp(q, cdf, bin_edges[1:])

    
    g_toa_energy = ROOT.TGraphAsymmErrors()
    ix_max=1
    ix_min=1
    h_energy = h2_toa_energy.ProjectionX()
    entries_counts=[]
    entries_energy=[]
    for ix in range(1, h_energy.GetNbinsX()+1):
        #print(f"Scanning bin {ix}")
        #print(f"ix_min = {ix_min}; ix_max = {ix_max}")
        ix_max=ix
        entries_counts.append( h_energy.GetBinContent(ix) )
        entries_energy.append( h_energy.GetXaxis().GetBinLowEdge(ix) )
        
        if (sum(entries_counts)>Nmin) or ((ix_max==h_energy.GetNbinsX()) and (sum(entries_counts)>Nmin_lastbin)):
            #print(f"Closing energy interval ({ix_min}, {ix_max}) with {sum(entries_counts)} entries")

            entries_energy.append( h_energy.GetXaxis().GetBinUpEdge(ix) )
            cdf = np.cumsum(entries_counts)
            cdf = cdf / cdf[-1]
            Emin = quantile_from_histogram(cdf, entries_energy, 0.16)
            Emed = quantile_from_histogram(cdf, entries_energy, 0.50)
            Emax = quantile_from_histogram(cdf, entries_energy, 0.84)
            #print(f"   (Emin,Emed,Emax)=({Emin},{Emed},{Emax})")

            
            h_toa = h2_toa_energy.ProjectionY("_py", ix_min, ix_max)
            print
            prob=np.array([0.16, 0.5, 0.84])
            q=np.array([0., 0., 0.])
            h_toa.ComputeIntegral()
            h_toa.GetQuantiles(3, q, prob);
            tmin, tmed, tmax = q[0], q[1], q[2]
            #print(f"   (tmin,tmed,tmax)=({tmin},{tmed},{tmax})")

            sqrtN = sqrt(1.0*sum(entries_counts))*0.4
            g_toa_energy.SetPoint( g_toa_energy.GetN(), Emed, tmed )
            g_toa_energy.SetPointError(g_toa_energy.GetN()-1, (Emed-Emin), (Emax-Emed), (tmed-tmin)/sqrtN, (tmax-tmed)/sqrtN)

            entries_counts=[]
            entries_energy=[]
            ix_min=ix+1

            
    return g_toa_energy
    

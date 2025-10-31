//---------------------------------------------------------------------------------------------------- 
// This tutorial code deomonstrate the usage of a TH2Poly object.
//----------------------------------------------------------------------------------------------------

void hexaplot_helper(const std::vector<double>& values = {}, 
                     bool skip_irrelevant_channels = true)
{
    gROOT->SetBatch(kTRUE);
    TString project_dir = "~/CMSSW_16_0_0_pre1/src/HGCalCommissioning/DQM/extern/";
    TString fname = project_dir + "output/geometry/geometry_ML_F_wafer.root";
    TString figure = "./test.png";

    TCanvas *c1 = new TCanvas("c1", "", 900, 900);
    c1->SetRightMargin(0.15);

    TH2Poly *p = new TH2Poly("hexagonal histograms", "", -14, 14, -14, 14);
    p->SetStats(0); // remove stat pad
    p->SetMarkerSize(0.7); // adjust text size on the bins
    p->GetXaxis()->SetTitle("x (cm)");
    p->GetYaxis()->SetTitle("y (cm)");
    p->GetYaxis()->SetTitleOffset(1.1);

    // load a geometry root file
    TFile *f = TFile::Open(fname,"R");

    // retrieves a TList of all keys in the current directory
    TGraph *gr;
    TKey *key;
    TIter nextkey(gDirectory->GetListOfKeys());

    // register polygonal bins 
    while ((key = (TKey*)nextkey())) {
        TObject *obj = key->ReadObj();
        if(obj->InheritsFrom("TGraph")) {
            gr = (TGraph*) obj;
            p->AddBin(gr);
        }
    }

    // fill values
    int values_index = 0;
    int nBins = p->GetNcells()-9;
    if (values.size() == 0) {
        for (int i = 0; i < nBins; ++i) {
            p->SetBinContent(i + 1, (float)i);
        }
    } 
    else if (skip_irrelevant_channels == true) {
        if (values.size() != 222) {
            throw std::runtime_error("The number of channels (222) does not match the size of the vector");
        }

        for (int i = 0; i < nBins; ++i) {
            if (i % 39 == 37 || i % 39 == 38) {
                continue;
            }
            int values_index = i - 2 * (i / 39);
            p->SetBinContent(i + 1, (float)values[values_index]);
        }
    } 
    else {
        if (values.size() != 234) {
            throw std::runtime_error("The number of total channels (234) does not match the size of the vector");
        }
        for (int i = 0; i < nBins; ++i) {
            p->SetBinContent(i + 1, (float)values[i]);
        }
    }
    std::cout<<"Ncells"<<p->GetNcells()<<std::endl;
    // create a plot
    gStyle->SetPaintTextFormat(".0f");
    p->Draw("colz;text");
    c1->SaveAs(figure);
    f->Close();
}

void hexaplot_helper(const char *values_filename = "",
                     const char *output_name = "test.png",
                     bool skip_irrelevant_channels = true) {
  gROOT->SetBatch(kTRUE);

  // --- Load geometry ---
  TString project_dir =
      "~/CMSSW_16_0_0_pre1/src/HGCalCommissioning/DQM/extern/";
  TString wafermap_fname =
      project_dir + "output/geometry/geometry_ML_F_wafer.root";
  TFile *f = TFile::Open(wafermap_fname, "READ");
  if (!f || f->IsZombie()) {
    Error("hexaplot_helper", "Failed to open wafermap file: %s",
          wafermap_fname.Data());
    return;
  }

  // --- Read values from text file ---
  std::vector<double> values;
  if (std::strlen(values_filename) > 0) {
    std::ifstream infile(values_filename);
    if (!infile.is_open()) {
      Error("hexaplot_helper", "Cannot open values file: %s", values_filename);
      return;
    }
    double x;
    while (infile >> x)
      values.push_back(x);
    infile.close();
  } else {
    Warning("hexaplot_helper",
            "No values file provided — filling test pattern.");
  }

  // --- Create canvas ---
  TString figure = output_name;
  TCanvas *c1 = new TCanvas("c1", "", 900, 900);
  c1->SetRightMargin(0.15);

  // --- Create hexagonal TH2Poly ---
  TH2Poly *p = new TH2Poly("hexagonal histograms", "", -14, 14, -14, 14);
  p->SetStats(0);
  p->SetMarkerSize(0.7);
  p->GetXaxis()->SetTitle("x (cm)");
  p->GetYaxis()->SetTitle("y (cm)");
  p->GetYaxis()->SetTitleOffset(1.1);

  // --- Load polygons from geometry file ---
  TKey *key;
  TIter nextkey(f->GetListOfKeys());
  while ((key = (TKey *)nextkey())) {
    TObject *obj = key->ReadObj();
    if (obj->InheritsFrom("TGraph")) {
      TGraph *gr = (TGraph *)obj;
      p->AddBin(gr);
    }
  }

  // --- Fill hexagonal bins ---
  int nBins = p->GetNcells() - 9; // geometry-specific offset?

  if (values.empty()) {
    for (int i = 0; i < nBins; ++i)
      p->SetBinContent(i + 1, (float)i);
  } else if (skip_irrelevant_channels) {
    if (values.size() != 222) {
      Error("hexaplot_helper", "Expected 222 channels, but got %zu from %s",
            values.size(), values_filename);
      f->Close();
      return;
    }

    for (int i = 0; i < nBins; ++i) {
      if (i % 39 == 37 || i % 39 == 38)
        continue;
      int values_index = i - 2 * (i / 39);
      if (values_index >= 0 && values_index < (int)values.size())
        p->SetBinContent(i + 1, (float)values[values_index]);
    }
  } else {
    if (values.size() != 234) {
      Error("hexaplot_helper", "Expected 234 channels (no skip), but got %zu",
            values.size());
      f->Close();
      return;
    }
    for (int i = 0; i < nBins; ++i)
      p->SetBinContent(i + 1, (float)values[i]);
  }

  // --- Draw and save ---
  gStyle->SetPaintTextFormat(".0f");
  p->Draw("colz;text");
  c1->SaveAs(figure);

  f->Close();
  delete c1;
}

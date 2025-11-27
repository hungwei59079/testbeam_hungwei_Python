import numpy as np
import ROOT

# Open file
f = ROOT.TFile.Open("selected_hits.root")
tree = f.Get("HitCoords")

x_hist_10 = ROOT.TH1F("x_residual_L10", "X residual layer 10", 40, -4, 4)

y_hist_10 = ROOT.TH1F("y_residual_L10", "Y residual layer 10", 40, -4, 4)

for event in tree:
    x = np.array(event.x_hits, dtype=float)
    y = np.array(event.y_hits, dtype=float)
    residual_x = x[9] - x[0]
    residual_y = y[9] - y[0]

    x_hist_10.Fill(residual_x)
    y_hist_10.Fill(residual_y)


print("x mean (hist):", x_hist_10.GetMean())
print("x RMS (hist):", x_hist_10.GetRMS())
print("y mean (hist):", y_hist_10.GetMean())
print("y RMS (hist):", y_hist_10.GetRMS())

output = ROOT.TFile("residual_hists_new.root", "RECREATE")

gaus_x = ROOT.TF1("gaus_x_L10", "gaus")
x_hist_10.Fit(gaus_x, "QS")
x_mean = gaus_x.GetParameter(1)
x_sigma = gaus_x.GetParameter(2)

# Fit y histogram
gaus_y = ROOT.TF1("gaus_y_L10", "gaus")
y_hist_10.Fit(gaus_y, "QS")
y_mean = gaus_y.GetParameter(1)
y_sigma = gaus_y.GetParameter(2)


results = {
    "x_mean": x_mean,
    "x_sigma": x_sigma,
    "y_mean": y_mean,
    "y_sigma": y_sigma,
}

print(results)

x_hist_10.Write()
y_hist_10.Write()

output.Close()

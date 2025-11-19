import numpy as np
import ROOT

# Open file
f = ROOT.TFile.Open("selected_hits.root")
tree = f.Get("HitCoords")

# Histograms indexed by their *actual* layer number
x_hists = {
    i: ROOT.TH1F(f"x_residual_L{i}", f"X residual layer {i}", 100, -0.2, 0.2)
    for i in range(2, 11)
}
y_hists = {
    i: ROOT.TH1F(f"y_residual_L{i}", f"Y residual layer {i}", 100, -0.5, 0.5)
    for i in range(2, 11)
}

layers = np.arange(1, 11, dtype=float)  # 1..10

# Event loop
for event in tree:
    x = np.array(event.x_hits, dtype=float)
    y = np.array(event.y_hits, dtype=float)

    # Fit slopes using all layers
    m_x, _ = np.polyfit(layers, x, 1)
    m_y, _ = np.polyfit(layers, y, 1)

    # Re-anchor to match layer 1 exactly
    b_x = x[0] - m_x * 1.0
    b_y = y[0] - m_y * 1.0

    # Predictions
    x_pred = m_x * layers + b_x
    y_pred = m_y * layers + b_y

    # Residuals
    x_res = x - x_pred
    y_res = y - y_pred

    # Fill layers 2..10
    for i in range(2, 11):
        x_hists[i].Fill(x_res[i - 1])
        y_hists[i].Fill(y_res[i - 1])


# ------------------------
#  FIT + SAVE RESULTS
# ------------------------

output = ROOT.TFile("residual_hists.root", "RECREATE")

print("===== Gaussian Fit Results =====")

results = {}

for i in range(2, 11):
    # Gaussian function
    gaus = ROOT.TF1("gaus", "gaus")

    # Fit quietly
    x_hists[i].Fit(gaus, "Q")
    y_hists[i].Fit(gaus, "Q")

    # Extract parameters
    x_mean = gaus.GetParameter(1)
    x_sigma = gaus.GetParameter(2)

    y_mean = gaus.GetParameter(1)
    y_sigma = gaus.GetParameter(2)

    results[i] = {
        "x_mean": x_mean,
        "x_sigma": x_sigma,
        "y_mean": y_mean,
        "y_sigma": y_sigma,
    }

    # Write histograms to file
    x_hists[i].Write()
    y_hists[i].Write()


# Close file
output.Close()

# Print results
for i in range(2, 11):
    print(
        f"Layer {i}: "
        f"x_mean = {results[i]['x_mean']:.5f}, x_sigma = {results[i]['x_sigma']:.5f},   "
        f"y_mean = {results[i]['y_mean']:.5f}, y_sigma = {results[i]['y_sigma']:.5f}"
    )

print("\nHistograms saved to: residual_hists.root")

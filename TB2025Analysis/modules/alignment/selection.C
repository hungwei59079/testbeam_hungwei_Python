#include <ROOT/RVec.hxx>
#include <cmath>
#include <map>
#include <set>
#include <unordered_map>
#include <vector>

using ROOT::VecOps::RVec;

// external global defined in Python
std::map<int, std::pair<float, float>> digiCoordMap;
// ------------------------------------------------------------
// 1. Unique layer check
// ------------------------------------------------------------
bool UniqueLayersCheck(const RVec<int> &layers,
                       const RVec<unsigned short> &channels) {
  std::set<int> uniq;

  const size_t n = layers.size();

  // Defensive: ensure parallel vectors
  if (channels.size() != n)
    return false;

  for (size_t i = 0; i < n; ++i) {
    // Skip hits with invalid digi/channel
    if (channels[i] == (unsigned short)-1)
      continue;

    // Skip disconnected layer
    if (layers[i] == 0)
      continue;

    uniq.insert(layers[i]);
  }

  return uniq.size() >= 5;
}

// ------------------------------------------------------------
// 2. Max hits per layer (< 4)
// ------------------------------------------------------------
bool MaxHitsPerLayerCheck(const RVec<int> &layers,
                          const RVec<unsigned short> &channels) {
  std::map<int, int> freq;
  for (size_t i = 0; i < layers.size(); ++i) {
    if (channels[i] == (unsigned short)-1)
      continue;
    if (layers[i] == 0)
      continue;
    freq[layers[i]]++;
  }
  for (auto &kv : freq)
    if (kv.second >= 4)
      return false;
  return true;
}

// ------------------------------------------------------------
// 3. Array size match
// ------------------------------------------------------------
bool ArrayMatchCheck(const RVec<int> &layers, const RVec<int> &channels) {
  return layers.size() == channels.size();
}

// ------------------------------------------------------------
// 4. Adjacent hit distance check
// ------------------------------------------------------------
bool AdjacentHitsCheck(const RVec<int> &layers,
                       const RVec<unsigned short> &channels,
                       double maxDist = 1.7) {
  std::map<int, int> freq;
  for (size_t i = 0; i < layers.size(); ++i) {
    if (channels[i] == (unsigned short)-1)
      continue;
    if (layers[i] == 0)
      continue;
    freq[layers[i]]++;
  }

  for (auto &kv : freq) {
    int layer = kv.first;
    int count = kv.second;

    if (count <= 1)
      continue;

    if (count <= 3) {
      std::vector<unsigned short> chs;
      for (size_t i = 0; i < layers.size(); i++){
        if (channels[i] == (unsigned short)-1)
          continue;
        if (layers[i] == layer)
        chs.push_back(channels[i]);
      }

      for (size_t i = 0; i < chs.size(); i++) {
        for (size_t j = i + 1; j < chs.size(); j++) {

          auto p1 = digiCoordMap[chs[i]];
          auto p2 = digiCoordMap[chs[j]];

          double dx = p1.first - p2.first;
          double dy = p1.second - p2.second;
          double dist = std::sqrt(dx * dx + dy * dy);

          if (dist > maxDist)
            return false;
        }
      }
    }
  }

  return true;
}

std::pair<RVec<float>, RVec<float>>
WeightedX(const RVec<int> &layers, const RVec<unsigned short> &channels,
          const RVec<float> &adcs) {
  constexpr int nLayers = 10;
  constexpr float pitch = 1.25f;
  const float singleHitSigma = pitch / std::sqrt(12.0f);

  RVec<float> x_out(nLayers, NAN);
  RVec<float> sigma_x_out(nLayers, NAN);

  std::unordered_map<int, float> sumA;
  std::unordered_map<int, float> sumAx;
  std::unordered_map<int, float> sumAx2;

  // --- Accumulate per-layer quantities ---
  for (size_t i = 0; i < layers.size(); ++i) {
    unsigned short ch = channels[i];
    if (ch == (unsigned short)-1)
      continue;

    int L = layers[i]; // expected 1..10
    float A = adcs[i];

    auto coord = digiCoordMap[ch];
    float x = coord.first;

    sumA[L] += A;
    sumAx[L] += A * x;
    sumAx2[L] += A * x * x;
  }

  // --- Compute centroid and RMS per layer ---
  for (int L = 1; L <= nLayers; ++L) {
    if (!sumA.count(L))
      continue;

    const int idx = L - 1;
    const float mean = sumAx[L] / sumA[L];

    float var = sumAx2[L] / sumA[L] - mean * mean;
    if (var < 0.0f) // numerical safety
      var = 0.0f;

    x_out[idx] = mean;

    // Geometry sign convention
    if (L == 2 || L == 4 || L == 6 || L == 8)
      x_out[idx] *= -1.0f;

    // Resolution proxy
    if (var > 0.0f)
      sigma_x_out[idx] = std::sqrt(var);
    else
      sigma_x_out[idx] = singleHitSigma;
  }

  return {x_out, sigma_x_out};
}

std::pair<RVec<float>, RVec<float>>
WeightedY(const RVec<int> &layers, const RVec<unsigned short> &channels,
          const RVec<float> &adcs) {
  constexpr int nLayers = 10;
  constexpr float pitch = 1.25f;
  const float singleHitSigma = pitch / std::sqrt(12.0f);

  RVec<float> y_out(nLayers, NAN);
  RVec<float> sigma_y_out(nLayers, NAN);

  std::unordered_map<int, float> sumA;
  std::unordered_map<int, float> sumAy;
  std::unordered_map<int, float> sumAy2;

  // --- Accumulate per-layer quantities ---
  for (size_t i = 0; i < layers.size(); ++i) {
    unsigned short ch = channels[i];
    if (ch == (unsigned short)-1)
      continue;

    int L = layers[i]; // expected 1..10
    float A = adcs[i];

    auto coord = digiCoordMap[ch];
    float y = coord.second;

    sumA[L] += A;
    sumAy[L] += A * y;
    sumAy2[L] += A * y * y;
  }

  // --- Compute centroid and RMS per layer ---
  for (int L = 1; L <= nLayers; ++L) {
    if (!sumA.count(L))
      continue;

    const int idx = L - 1;
    const float mean = sumAy[L] / sumA[L];

    float var = sumAy2[L] / sumA[L] - mean * mean;
    if (var < 0.0f) // numerical safety
      var = 0.0f;

    y_out[idx] = mean;

    // Resolution proxy
    if (var > 0.0f)
      sigma_y_out[idx] = std::sqrt(var);
    else
      sigma_y_out[idx] = singleHitSigma;
  }

  return {y_out, sigma_y_out};
}

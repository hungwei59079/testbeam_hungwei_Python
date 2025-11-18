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
bool UniqueLayersCheck(const RVec<int> &layers) {
  std::set<int> uniq(layers.begin(), layers.end());

  // Remove zero - which represents disconnected channels - if present
  uniq.erase(0);

  // Check if number of NONZERO unique elements is at least 5
  return uniq.size() >= 5;
}

// ------------------------------------------------------------
// 2. Max hits per layer (< 4)
// ------------------------------------------------------------
bool MaxHitsPerLayerCheck(const RVec<int> &layers) {
  std::map<int, int> freq;
  for (int l : layers)
    freq[l]++;
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
bool AdjacentHitsCheck(const RVec<int> &layers, const RVec<int> &channels,
                       double maxDist = 1.7) {
  std::map<int, int> freq;
  for (int l : layers)
    freq[l]++;

  for (auto &kv : freq) {
    int layer = kv.first;
    int count = kv.second;

    if (count <= 1)
      continue;

    if (count <= 3) {
      std::vector<int> chs;
      for (size_t i = 0; i < layers.size(); i++)
        if (layers[i] == layer)
          chs.push_back(channels[i]);

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

std::map<int, std::pair<float, float>>
WeightedLayerCoordinates(const ROOT::RVec<int> &layers,
                         const ROOT::RVec<int> &channels,
                         const ROOT::RVec<float> &adcs) {
  std::unordered_map<int, float> sumA;
  std::unordered_map<int, float> sumAx;
  std::unordered_map<int, float> sumAy;

  // Accumulate per-layer weighted sums
  for (size_t i = 0; i < layers.size(); i++) {
    int L = layers[i];
    int ch = channels[i];
    float A = adcs[i];

    auto coord = digiCoordMap[ch]; // pair<float,float>
    float x = coord.first;
    float y = coord.second;

    sumA[L] += A;
    sumAx[L] += A * x;
    sumAy[L] += A * y;
  }

  std::map<int, std::pair<float, float>> out;

  // Layers hit in this event → weighted average
  for (auto &kv : sumA) {
    int L = kv.first;
    float A = kv.second;
    if (A > 0) {
      float xw = sumAx[L] / A;
      float yw = sumAy[L] / A;
      out[L] = {xw, yw};
    }
  }

  // Now fill missing layers with NaN
  for (int L = 1; L <= 10; L++) {
    if (out.find(L) == out.end()) {
      out[L] = {NAN, NAN};
    }
  }

  return out;
}

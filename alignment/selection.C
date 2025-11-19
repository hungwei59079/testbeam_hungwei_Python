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

ROOT::RVec<float> WeightedX(const ROOT::RVec<int> &layers,
                            const ROOT::RVec<int> &channels,
                            const ROOT::RVec<float> &adcs) {
  ROOT::RVec<float> x_out(10, NAN);

  std::unordered_map<int, float> sumA, sumAx;

  for (size_t i = 0; i < layers.size(); i++) {
    int L = layers[i]; // 1..10
    int ch = channels[i];
    float A = adcs[i];

    auto coord = digiCoordMap[ch];
    float x = coord.first;

    sumA[L] += A;
    sumAx[L] += A * x;
  }

  for (int L = 1; L <= 10; L++) {
    if (sumA.count(L)) {
      x_out[L - 1] = sumAx[L] / sumA[L];
    }
    if (L == 2 || L == 4 || L == 6 || L == 8) {
      x_out[L - 1] *= -1;
    }
  }

  return x_out;
}

ROOT::RVec<float> WeightedY(const ROOT::RVec<int> &layers,
                            const ROOT::RVec<int> &channels,
                            const ROOT::RVec<float> &adcs) {
  ROOT::RVec<float> y_out(10, NAN);

  std::unordered_map<int, float> sumA, sumAy;

  for (size_t i = 0; i < layers.size(); i++) {
    int L = layers[i];
    int ch = channels[i];
    float A = adcs[i];

    auto coord = digiCoordMap[ch];
    float y = coord.second;

    sumA[L] += A;
    sumAy[L] += A * y;
  }

  for (int L = 1; L <= 10; L++) {
    if (sumA.count(L)) {
      y_out[L - 1] = sumAy[L] / sumA[L];
    }
  }

  return y_out;
}

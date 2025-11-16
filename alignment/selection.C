#include <ROOT/RVec.hxx>
#include <cmath>
#include <map>
#include <set>
#include <vector>

using ROOT::VecOps::RVec;

// external global defined in Python
extern std::map<int, std::pair<float, float>> digiCoordMap;

// ------------------------------------------------------------
// 1. Unique layer check
// ------------------------------------------------------------
bool UniqueLayersCheck(const RVec<int> &layers) {
  std::set<int> uniq(layers.begin(), layers.end());
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
                       double maxDist = 20.0) {
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

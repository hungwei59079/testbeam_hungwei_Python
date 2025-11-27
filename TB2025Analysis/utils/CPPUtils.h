#include <ROOT/RVec.hxx>

using namespace ROOT::VecOps;

using ROOT::RVecI;
using ROOT::RVecF;


RVecF GetLayerEnergy(const int &Nlayers, const int &layer_min, const RVecI &layer, const RVecF &energies)
{
  RVecF energy_sums(Nlayers, 0.0);
  for( unsigned i=0; i<energies.size(); ++i) {
    int ilayer = layer[i]-layer_min;
    energy_sums[ilayer] += energies[i];
  }
  return energy_sums;
}

RVecF GetLayerNhits(const int &Nlayers, const int &layer_min, const RVecI &layer)
{
  RVecI Nhits(Nlayers, 0);
  for( unsigned i=0; i<layer.size(); ++i) {
    int ilayer = layer[i]-layer_min;
    Nhits[ilayer]++;
  }
  return Nhits;
}

RVecI GetLayerId(const int &Nlayers, const int &layer_min)
{
  RVecI layers(Nlayers, 0);
  for( unsigned i=0; i<Nlayers; ++i) 
    layers[i]=i+layer_min;
  return layers;
}

RVecI GetDigiIdx(const RVecI &HGCDigi_denseIndex, const RVecI &HGCHit_denseIndex)
{
  RVecI digiIdx(HGCHit_denseIndex.size(), -1);

  for( unsigned iHit=0; iHit<HGCHit_denseIndex.size(); ++iHit) {
    int denseIdx = HGCHit_denseIndex[iHit];
    auto digiItr = std::find(HGCDigi_denseIndex.begin(), HGCDigi_denseIndex.end(), denseIdx);
    int iDigi = std::distance(HGCDigi_denseIndex.begin(), digiItr);
    digiIdx[iHit] = iDigi;
  }
  return digiIdx;
}

RVecI GetDigiIdxDebug(const RVecI &HGCDigi_denseIndex, const RVecI &HGCHit_denseIndex, const int &event)
{
  RVecI digiIdx(HGCHit_denseIndex.size(), -1);

  for( unsigned iHit=0; iHit<HGCHit_denseIndex.size(); ++iHit) {
    int denseIdx = HGCHit_denseIndex[iHit];
    auto digiItr = std::find(HGCDigi_denseIndex.begin(), HGCDigi_denseIndex.end(), denseIdx);
    if(digiItr==HGCDigi_denseIndex.end())
      std::cout<<"This is the end"<<std::endl;
    int iDigi = std::distance(HGCDigi_denseIndex.begin(), digiItr);
    if(iDigi==HGCDigi_denseIndex.size()) {
      std::cout<<"event="<<event<<"; This is the end"<<std::endl;
      std::cout<<"iHit="<<iHit
	       <<"; HGCHit_denseIndex[iHit]="<<denseIdx
	       <<"; iDigi="<<iDigi
	       <<"; HGCDigi_denseIndex[iDigi]="<<HGCDigi_denseIndex.at(iDigi)<<std::endl;
    }
    digiIdx[iHit] = iDigi;
  }
  return digiIdx;
}

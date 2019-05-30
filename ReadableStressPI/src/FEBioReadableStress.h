#pragma once
#include "FECore/FEMesh.h"
#include "FECore/FEPlotData.h"
#include "FEBioMech/FEElasticMaterial.h"
#include <iostream>
#include <fstream>

class FEPlotReadElementStress : public FEDomainData
{
public:
    FEPlotReadElementStress(FEModel* pfem) : FEDomainData(PLT_FLOAT, FMT_ITEM){}
    bool Save(FEDomain& dom, FEDataStream& a);
};

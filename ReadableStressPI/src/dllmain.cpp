#include "FECore/FECoreKernel.h"
#include "FEBioReadableStress.h"

FERegisterClass_T<FEPlotReadElementStress> febio_readstress_factory(FEPLOTDATA_ID, "stress_printout");

FECORE_EXPORT unsigned int GetSDKVersion()
{
    return FE_SDK_VERSION;
}

FECORE_EXPORT void PluginInitialize(FECoreKernel& fecore)
{
  FECoreKernel::SetInstance(&fecore);
}

FECORE_EXPORT int PluginNumClasses()
{
	return 1;
}

FECORE_EXPORT FECoreFactory* PluginGetFactory(int i)
{
  if (i == 0) return &febio_readstress_factory;
  return 0;
}

FECORE_EXPORT void PluginCleanup()
{

}

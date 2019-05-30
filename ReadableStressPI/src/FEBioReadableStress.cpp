#include "FEBioReadableStress.h"
#include <iostream>

bool FEPlotReadElementStress::Save(FEDomain& dom, FEDataStream& a)
{
  FESolidMaterial* pms = dynamic_cast<FESolidMaterial*>(dom.GetMaterial());
  if (pms == 0)
    {
      FEElasticMaterial* pme = dom.GetMaterial()->GetElasticMaterial();
      if ((pme == 0) || pme->IsRigid()) return false;
    }

  // write solid element data
  ofstream out_f;
  out_f.open("stress.out", std::ofstream::out | std::ofstream::trunc);
  // The above line makes sure that only the most recent stress is written

  ofstream out_pos;
  out_pos.open("position.out", std::ofstream::out | std::ofstream::trunc);

  ofstream out_disp;
  out_disp.open("displacement.out", std::ofstream::out | std::ofstream::trunc);

  FEMesh* mesh = dom.GetMesh();
  //mesh->Init();

  int N = dom.Elements();
  for (int i=0; i<N; ++i)
    {

      FEElement& el = dom.ElementRef(i);
      out_pos << i << ":";
      out_disp << i << ":";
      int nodes = el.Nodes();
      for (int n=0; n<nodes; n++)
        {
          FENode node = dom.Node(el.m_lnode[n]);
          out_pos << "("
                  << node.m_r0.x << ","
                  << node.m_r0.y << ","
                  << node.m_r0.z
                  << ")";
          out_disp << "("
                  << node.m_rt.x - node.m_r0.x << ","
                  << node.m_rt.y - node.m_r0.y << ","
                  << node.m_rt.z - node.m_r0.z
                  << ")";
        }
      out_pos << "\n";
      out_disp << "\n";
      mat3ds s; s.zero();
      int nint = el.GaussPoints();
      double f = 1.0 / (double) nint;

      // since the PLOT file requires floats we need to convert
      // the doubles to single precision
      // we output the average stress values of the gauss points
      for (int j=0; j<nint; ++j)
        {
          FEElasticMaterialPoint* ppt = (el.GetMaterialPoint(j)->ExtractData<FEElasticMaterialPoint>());
          if (ppt)
            {
              FEElasticMaterialPoint& pt = *ppt;
              s += pt.m_s;
            }
        }
      s *= f;

      out_f << i << ":"
            << s.xx() << ";"
            << s.yy() << ";"
            << s.zz() << ";"
            << s.xy() << ";"
            << s.yz() << ";"
            << s.xz() << "\n";

      a << s;
    }

  out_f.close();
  out_pos.close();
  out_disp.close();
  return true;
}

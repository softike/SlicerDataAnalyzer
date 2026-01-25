/*=========================================================================
  HPROJECT
  Copyright (c) Ernesto Durante, Julien de Siebenthal
  All rights reserved.
  See Copyrights.txt for details
  =========================================================================*/

#include "SboFIT.h"

#include "SboTPCatalogElement.h"
#include "SboTPCatalogList.h"
#include "SboMathLibBase.h"

#include <QDir>
#include <QIcon>

#define ICONSET_STR(s) QIcon(":/TPCatalogIcons/" s)

namespace XXXStem {
  const SboShape3UID LimaRangeStartAt=60000L + 750L;

  const QString CompanyName("LC");
  const QString ProductName("LC FIT");

  const QString RCCIdName("FIt");
  const QString RCCFileName("FITplugin.rcc");
  const QString RCCPath("/LC/FITMeshes");

  const QIcon   PartIcon=ICONSET_STR("generic_stem.png");
  const QString PartMenuText("");
  const QString PartTooltipText("");
  const QString ItemName("FIT");

  const QIcon   PartHeadIcon=ICONSET_STR("spcl_head.png");
  const QString PartHeadMenuText("");
  const QString PartHeadTooltipText("");

  enum class S3UID: SboShape3UID{
				 STEM_1_R = LimaRangeStartAt,
				 STEM_2_R,
				 STEM_3_R,
				 STEM_4_R,
				 STEM_5_R,
				 STEM_6_R,
				 STEM_7_R,
				 STEM_1_L,
				 STEM_2_L,
				 STEM_3_L,
				 STEM_4_L,
				 STEM_5_L,
				 STEM_6_L,
				 STEM_7_L,
				 CUTPLANE,
				 HEAD_M4,
				 HEAD_P0,
				 HEAD_P4,
				 HEAD_P8
  };

  const S3UID lowerS3UID=S3UID::STEM_1_R;
  const S3UID upperS3UID=S3UID::HEAD_P8;

  const S3UID defaultS3UID_R=S3UID::STEM_7_R;
  const S3UID defaultS3UID_L=S3UID::STEM_7_L;

  SboShape3Label s3( S3UID e)
  {
    return SboShape3Label(SboShape3Label::utype(e));
  }

  int getItemSize(SboShape3Label aLabel){

    if(aLabel == s3(S3UID::STEM_1_R) || aLabel == s3(S3UID::STEM_1_L)) return 1;
    if(aLabel == s3(S3UID::STEM_2_R) || aLabel == s3(S3UID::STEM_2_L)) return 2;
    if(aLabel == s3(S3UID::STEM_3_R) || aLabel == s3(S3UID::STEM_3_L)) return 3;
    if(aLabel == s3(S3UID::STEM_4_R) || aLabel == s3(S3UID::STEM_4_L)) return 4;
    if(aLabel == s3(S3UID::STEM_5_R) || aLabel == s3(S3UID::STEM_5_L)) return 5;
    if(aLabel == s3(S3UID::STEM_6_R) || aLabel == s3(S3UID::STEM_6_L)) return 6;

    //Right neck
    return 7;
  }

  int isRight(SboShape3Label aLabel){
    return SboML::in_closed_range<SboShape3Label>(aLabel,s3(lowerS3UID),s3(S3UID::STEM_7_R));
  }


}


QString SboFIT::productName() const
{
  return XXXStem::ProductName;
}

QString SboFIT::companyName() const
{
  return XXXStem::CompanyName;
}


QString SboFIT::setMeshInfoSearchPath(QString aPath)
{
  using namespace XXXStem;

  //http://doc.qt.io/qt-5/qdir.html#setSearchPaths
  //Load resource from the system file
  QString myRcc;
  if(meshInfoResourceFromRcc(myRcc))
    QDir::setSearchPaths(RCCIdName, QStringList(QString(":") + RCCPath));
  else
    QDir::setSearchPaths(RCCIdName, QStringList(aPath + RCCPath));

  return {};
}

bool SboFIT::meshInfoResourceFromRcc(QString& aRcc)
{
  aRcc=XXXStem::RCCFileName;
  return false;
}

bool SboFIT::meshInfoResourceFromFileSystem()
{
  return true;
}


void SboFIT::meshInfoRCList(SboMeshInfoRCList& rcList)
{
  using namespace XXXStem;
  auto next=[&](S3UID e,QString s) { rcList.push_back({s3(e),RCCIdName + QString(":") + s + ".wrl"});};

  //short R 26
  next(S3UID::STEM_1_R,"4211_25_110");
  next(S3UID::STEM_2_R,"4211_25_120");
  next(S3UID::STEM_3_R,"4211_25_130");
  next(S3UID::STEM_4_R,"4211_25_140");
  next(S3UID::STEM_5_R,"4211_25_150");
  next(S3UID::STEM_6_R,"4211_25_160");
  next(S3UID::STEM_7_R,"4211_25_170");

  next(S3UID::STEM_1_L,"4211_25_010");
  next(S3UID::STEM_2_L,"4211_25_020");
  next(S3UID::STEM_3_L,"4211_25_030");
  next(S3UID::STEM_4_L,"4211_25_040");
  next(S3UID::STEM_5_L,"4211_25_050");
  next(S3UID::STEM_6_L,"4211_25_060");
  next(S3UID::STEM_7_L,"4211_25_070");
}


void SboFIT::parts(SboTPCatalogList& prodList)
{
  using namespace XXXStem;

  auto stemRange= new SboTPCPartMonoStem(productName(),SboAnatomLocation::Right);
  stemRange->_iconSet=PartIcon;
  stemRange->_menuText=PartMenuText;
  stemRange->_tooltipText=PartTooltipText;
  stemRange->setDefaultLabel(s3(defaultS3UID_R));

  auto next=[&](S3UID e,QString s) { stemRange->push_back(new SboTPCatalogItem(stemRange,s3(e), ItemName,s));};

  //short R 17
  next(S3UID::STEM_1_R,"1");
  next(S3UID::STEM_2_R,"2");
  next(S3UID::STEM_3_R,"3");
  next(S3UID::STEM_4_R,"4");
  next(S3UID::STEM_5_R,"5");
  next(S3UID::STEM_6_R,"6");
  next(S3UID::STEM_7_R,"7");

  prodList.push_back(stemRange);


  stemRange= new SboTPCPartMonoStem(productName(),SboAnatomLocation::Left);
  stemRange->_iconSet=PartIcon;
  stemRange->_menuText=PartMenuText;
  stemRange->_tooltipText=PartTooltipText;
  stemRange->setDefaultLabel(s3(defaultS3UID_L));

  next(S3UID::STEM_1_L,"1");
  next(S3UID::STEM_2_L,"2");
  next(S3UID::STEM_3_L,"3");
  next(S3UID::STEM_4_L,"4");
  next(S3UID::STEM_5_L,"5");
  next(S3UID::STEM_6_L,"6");
  next(S3UID::STEM_7_L,"7");


  prodList.push_back(stemRange);

  //NOTE: Last argument S3UID::HEAD_P4 locates the CONE Lateral tip
  //default label must different from HEAD_P4 to compute the cone axis.
  auto headRange= new SboTPCPartHead(productName(),s3(S3UID::HEAD_P4));
  headRange->_iconSet=PartHeadIcon;
  headRange->_menuText=PartHeadMenuText;
  headRange->_tooltipText=PartHeadTooltipText;
  headRange->setDefaultLabel(s3(S3UID::HEAD_P0));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_M4),"Head","-4"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P0),"Head","0"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P4),"Head","+4"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P8),"Head","+8"));

  prodList.push_back(headRange);

  auto cutPlaneRange= new SboTPCPartCutPlane(productName());
  cutPlaneRange->setDefaultLabel(s3(S3UID::CUTPLANE));
  cutPlaneRange->push_back(new SboTPCatalogItem(cutPlaneRange,s3(S3UID::CUTPLANE),"Cutplane"));

  prodList.push_back(cutPlaneRange);

}


bool SboFIT::inRange(SboShape3Label aL)
{
  using namespace XXXStem;
  return SboML::in_closed_range<SboShape3Label>(aL,s3(lowerS3UID),s3(upperS3UID));
}

SboMatrix3 SboFIT::headToNeckMatrix(SboShape3Label aHeadLabel, SboShape3Label aNeckLabel)
{
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboFIT::neckToStemMatrix(SboShape3Label aNeckLabel, SboShape3Label aStemLabel, SboAnatomLocation aSide)
{
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboFIT::headToStemMatrix(SboShape3Label aHeadLabel, SboShape3Label aStemLabel)
{
  //Only for mono-block stem
  //In CPT_FRAME
  //Reference is diameter 36 (NB: 32 is the most common !?)

  //HEAD point in LOCAL_FRAE is at (0,0,0)
  //Compute the traffo to position the HEAD in CPT_FRAME

  using namespace XXXStem;

  float l=0.0f;
  if(aHeadLabel == s3(S3UID::HEAD_M4)) l+=-8.0f;
  else if(aHeadLabel == s3(S3UID::HEAD_P0)) l+=-4.0f;
  else if(aHeadLabel == s3(S3UID::HEAD_P4)) l+=0.f;
  else if(aHeadLabel == s3(S3UID::HEAD_P8)) l+=4.3f;

  return SboML::transMat3(l,0.f,0.f);

}

SboPlane3 SboFIT::cutPlane(SboShape3Label aStemLabel)
{
  //Return a R plane in CPT_FRAME
  //NOTE: the cut plane is used to position the component

  using namespace XXXStem;
  float l=-34.4f;
  if(getItemSize(aStemLabel) == 2) l=-36.5f;
  else if(getItemSize(aStemLabel) == 3) l=-38.0f;
  else if(getItemSize(aStemLabel) == 4) l=-39.5f;
  else if(getItemSize(aStemLabel) == 5) l=-41.5f;
  else if(getItemSize(aStemLabel) == 6) l=-43.4f;
  else if(getItemSize(aStemLabel) == 7) l=-45.6f;


  auto t=SboML::transMat3(l,0.f,0.f);
  return SboPlane3(SboPoint3(l,0.f,0.f),SboVector3(1.f,0.f,0.f));//.transform(t);
}

SboBbox3 SboFIT::cutPlaneBbox(SboShape3Label aStemLabel)
{
  //Return a bbox in CPT_FRAME
  //Bounding box containing the cut plane, required to draw the plane trace.
  //bbox must enclose the plane.
  //NOTE: if the intersection is empty, no trace of the plane is shown on the display

  using namespace XXXStem;

  SboPoint3 pmin(-25.0f,-25.0f,-25.0f);
  SboPoint3 pmax(25.0f,25.0f,25.0f);

  float l=-34.4f;
  if(getItemSize(aStemLabel) == 2) l=-36.5f;
  else if(getItemSize(aStemLabel) == 3) l=-38.0f;
  else if(getItemSize(aStemLabel) == 4) l=-39.5f;
  else if(getItemSize(aStemLabel) == 5) l=-41.5f;
  else if(getItemSize(aStemLabel) == 6) l=-43.4f;
  else if(getItemSize(aStemLabel) == 7) l=-45.6f;

  auto t=SboML::transMat3(l,0.f,0.f);
  pmin=t(pmin);
  pmax=t(pmax);

  return SboML::makeBbox3(pmin,pmax);
}

SboMatrix3 SboFIT::normalTrf(SboShape3Label aStemLabel, const SboPlane3 & aP3, const SboPoint3 & aO3)
{
  //Traffo from CPT_FRAME to NORMAL_FRAME
  //In NORMAL_FRAME,
  //Stem lives in the XZ plane
  //Stem axis must aligned with the Z axis
  //Stem head is pointing toward Z>0

  using namespace XXXStem;

  float l=34.4f;
  if(getItemSize(aStemLabel) == 2) l=36.5f;
  else if(getItemSize(aStemLabel) == 3) l=38.0f;
  else if(getItemSize(aStemLabel) == 4) l=39.5f;
  else if(getItemSize(aStemLabel) == 5) l=41.5f;
  else if(getItemSize(aStemLabel) == 6) l=43.4f;
  else if(getItemSize(aStemLabel) == 7) l=45.6f;

  auto t=SboML::transMat3(l,0.f,0.f);
  auto r1=SboML::rotMatX3(SboML::deg2Rad<float>(90.0f));
  auto r2=SboML::rotMatY3(SboML::deg2Rad<float>(-45.0f));

  //heuristic: stem axis be aligned with FF longitudinal axis
  auto r3=SboML::rotMatX3(SboML::deg2Rad<float>(isRight(aStemLabel) ? 5.0f: -5.0f));
  auto r4=SboML::rotMatY3(SboML::deg2Rad<float>(4.0f));
  return r4*r3*r2*r1*t;
}

SboVector3 SboFIT::offsetFF(SboShape3Label aStemLabel)
{

  //independently of the side
  //x > 0 is a medialization of the implant
  //y > 0 toward posterior
  //z > 0 toward superior

  using namespace XXXStem;

  //heuristic
  float l=15.0f;
  if(getItemSize(aStemLabel) == 2)      l=36.5f - 34.4f + 14.0f;
  else if(getItemSize(aStemLabel) == 3) l=38.0f - 34.4f + 13.0f;
  else if(getItemSize(aStemLabel) == 4) l=39.5f - 34.4f + 12.0f;
  else if(getItemSize(aStemLabel) == 5) l=41.5f - 34.4f + 11.0f;
  else if(getItemSize(aStemLabel) == 6) l=43.4f - 34.4f + 10.0f;
  else if(getItemSize(aStemLabel) == 7) l=45.6f - 34.4f + 9.0f;

  return {l,0.f,0.f};
}

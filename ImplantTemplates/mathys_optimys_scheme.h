/*=========================================================================
  HPROJECT
  Copyright (c) Ernesto Durante, Julien de Siebenthal
  All rights reserved.
  See Copyrights.txt for details
  =========================================================================*/

#include "SboOptimys.h"

#include "SboTPCatalogElement.h"
#include "SboTPCatalogList.h"
#include "SboMathLibBase.h"

#include <QDir>
#include <QIcon>

#define ICONSET_STR(s) QIcon(":/TPCatalogIcons/" s)

namespace XXXStem {
  const SboShape3UID MYSRangeStartAt =130000L + 500L;

  const QString CompanyName("MYS");
  const QString ProductName("MYS OPTIMYS");

  //NOTE: valid names for rcc id can contain only letters & numbers
  //NOTE: Because each RCCId name must be unique, we concatenate
  //CompanyName & ProductName
  const QString RCCIdName("MYSOPTIMYS");
  const QString RCCFileName("Optimys.rcc");
  const QString RCCPath("/MYS/OPTIMYSMeshes");

  const QIcon   PartIcon=ICONSET_STR("generic_stem.png");
  const QString PartMenuText("");
  const QString PartTooltipText("");
  const QString ItemName("Optimys");

  const QIcon   PartHeadIcon=ICONSET_STR("spcl_head.png");
  const QString PartHeadMenuText("");
  const QString PartHeadTooltipText("");

  enum class S3UID: SboShape3UID{
				 STEM_STD_1 = MYSRangeStartAt,
                                 STEM_STD_2,
                                 STEM_STD_3,
                                 STEM_STD_4,
                                 STEM_STD_5,
                                 STEM_STD_6,
                                 STEM_STD_7,
                                 STEM_STD_8,
                                 STEM_STD_9,
                                 STEM_STD_10,
                                 STEM_STD_11,
                                 STEM_STD_12,
                                 STEM_STD_13,
                                 STEM_STD_14,
                                 STEM_LAT_1,
                                 STEM_LAT_2,
                                 STEM_LAT_3,
                                 STEM_LAT_4,
                                 STEM_LAT_5,
                                 STEM_LAT_6,
                                 STEM_LAT_7,
                                 STEM_LAT_8,
                                 STEM_LAT_9,
                                 STEM_LAT_10,
                                 STEM_LAT_11,
                                 STEM_LAT_12,
                                 STEM_LAT_13,
                                 STEM_LAT_14,
				 CUTPLANE,
				 HEAD_M4,
				 HEAD_P0,
				 HEAD_P4,
				 HEAD_P8,
                                 RANGE_CCD_STD,
                                 RANGE_CCD_LAT,
  };

  const S3UID lowerS3UID=S3UID::STEM_STD_1;
  const S3UID upperS3UID=S3UID::RANGE_CCD_LAT;

  const S3UID defaultS3StemUID=S3UID::STEM_STD_7;
  const S3UID defaultS3HeadUID=S3UID::HEAD_P0;

  inline SboShape3Label s3( S3UID e) { return SboShape3Label(SboShape3Label::utype(e));}

  inline bool isCCD_STD(SboShape3Label l) {
   //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_STD_1),s3(S3UID::STEM_STD_14));
  }

  inline bool isCCD_LAT(SboShape3Label l) {
    //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_LAT_1),s3(S3UID::STEM_LAT_14));
  }

  inline bool isStem(SboShape3Label l) {
    return isCCD_STD(l) || isCCD_LAT(l);
  }

  inline bool isHead(SboShape3Label l){
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::HEAD_M4),s3(S3UID::HEAD_P8));
  }

  inline SboShape3Label nextPrevStem(SboShape3Label aL,bool aNext){
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    const auto nL= aL.next(aNext ? 1: -1);
    if(isCCD_LAT(aL))
        return isCCD_LAT(nL) ? nL: aL;

    return isCCD_STD(nL) ? nL: aL;
  }

  inline SboShape3Label getCCDRange(SboShape3Label aL){

    if(isCCD_STD(aL)) return s3(S3UID::RANGE_CCD_STD);
    if(isCCD_LAT(aL)) return s3(S3UID::RANGE_CCD_LAT);

    return {};
  }

  inline int getSimilarOffset(int aOffset, SboShape3Label /*aSourceR*/, SboShape3Label /*aTargetR*/ ){

    //NOTE: see ProductInfo to get the relation between sizes
    //[[hdoc:hproject/capture-hproj-implants.org::twinsys]]

    return aOffset;
  }

  inline int getSize(SboShape3Label aL){

    if(isCCD_STD(aL))
      return aL.uid() - s3(S3UID::STEM_STD_1).uid();

    if(isCCD_LAT(aL))
      return aL.uid() - s3(S3UID::STEM_LAT_1).uid();

    return 0;
  }

  inline float getHeadTop(SboShape3Label aL){

    if(aL == s3(S3UID::STEM_STD_1)) return 27.0f + 0 * 1.05f;
    if(aL == s3(S3UID::STEM_STD_2)) return 27.0f + 1 * 1.05f;
    if(aL == s3(S3UID::STEM_STD_3)) return 27.0f + 2 * 1.05f;
    if(aL == s3(S3UID::STEM_STD_4)) return 27.0f + 3 * 1.05f;
    if(aL == s3(S3UID::STEM_STD_5)) return 27.0f + 4 * 1.05f;
    if(aL == s3(S3UID::STEM_STD_6)) return 27.0f + 5 * 1.05f;
    if(aL == s3(S3UID::STEM_STD_7)) return 27.0f + 6 * 1.15f;
    if(aL == s3(S3UID::STEM_STD_8)) return 27.0f + 7 * 1.15f;
    if(aL == s3(S3UID::STEM_STD_9)) return 27.0f + 8 * 1.15f;
    if(aL == s3(S3UID::STEM_STD_10)) return 27.0f + 9 * 1.25f;
    if(aL == s3(S3UID::STEM_STD_11)) return 27.0f + 10 * 1.25f;
    if(aL == s3(S3UID::STEM_STD_12)) return 27.0f + 11 * 1.25f;
    if(aL == s3(S3UID::STEM_STD_13)) return 27.0f + 12 * 1.25f;
    if(aL == s3(S3UID::STEM_STD_14)) return 27.0f + 13 * 1.25f;

    if(aL == s3(S3UID::STEM_LAT_1)) return 31.0f + 0 * 1.05f;
    if(aL == s3(S3UID::STEM_LAT_2)) return 31.0f + 1 * 1.05f;
    if(aL == s3(S3UID::STEM_LAT_3)) return 31.0f + 2 * 1.05f;
    if(aL == s3(S3UID::STEM_LAT_4)) return 31.0f + 3 * 1.05f;
    if(aL == s3(S3UID::STEM_LAT_5)) return 31.0f + 4 * 1.05f;
    if(aL == s3(S3UID::STEM_LAT_6)) return 31.0f + 5 * 1.05f;
    if(aL == s3(S3UID::STEM_LAT_7)) return 31.0f + 6 * 1.15f;
    if(aL == s3(S3UID::STEM_LAT_8)) return 31.0f + 7 * 1.15f;
    if(aL == s3(S3UID::STEM_LAT_9)) return 31.0f + 8 * 1.15f;
    if(aL == s3(S3UID::STEM_LAT_10)) return 31.0f + 9 * 1.25f;
    if(aL == s3(S3UID::STEM_LAT_11)) return 31.0f + 10 * 1.25f;
    if(aL == s3(S3UID::STEM_LAT_12)) return 31.0f + 11 * 1.25f;
    if(aL == s3(S3UID::STEM_LAT_13)) return 31.0f + 12 * 1.25f;
    if(aL == s3(S3UID::STEM_LAT_14)) return 31.0f + 13 * 1.25f;

    return 0;
  }


}

int SboOptimys::rev() const
{
  return 1;
}

QString SboOptimys::productName() const
{
  return XXXStem::ProductName;
}

QString SboOptimys::companyName() const
{
  return XXXStem::CompanyName;
}

QString SboOptimys::message(int,const SboFemImplantConfig&) const
{
  return "Optimys";
}

QString SboOptimys::setMeshInfoSearchPath(QString aPath)
{
  using namespace XXXStem;

  //http://doc.qt.io/qt-5/qdir.html#setSearchPaths
  //Load resource from the system file
  QString myRcc;
  if(meshInfoResourceFromRcc(myRcc))
    QDir::setSearchPaths(RCCIdName, QStringList(QString(":") + RCCPath));
  else {
    //qDebug() << aPath + RCCPath + "/STD";
    QDir::setSearchPaths(RCCIdName, {aPath + RCCPath + "/STD",
                                     aPath + RCCPath + "/LAT"} );

  }

  return {};
}

bool SboOptimys::meshInfoResourceFromRcc(QString& aRcc)
{
  aRcc=XXXStem::RCCFileName;
  return false;
}

bool SboOptimys::meshInfoResourceFromFileSystem()
{
  return true;
}


void SboOptimys::meshInfoRCList(SboMeshInfoRCList& rcList)
{
  using namespace XXXStem;
  auto next=[&](S3UID e,QString s,QString aRCCId) { rcList.push_back({s3(e),aRCCId + QString(":") + s + ".wrl"});};

  next(S3UID::STEM_STD_1, "52_34_1165_50024772_V02",RCCIdName);
  next(S3UID::STEM_STD_2, "52_34_1166_50028325_V03",RCCIdName);
  next(S3UID::STEM_STD_3, "52_34_0191_10092331_V01",RCCIdName);
  next(S3UID::STEM_STD_4, "52_34_0192_10092332_V01",RCCIdName);
  next(S3UID::STEM_STD_5, "52_34_0193_10092333_V01",RCCIdName);
  next(S3UID::STEM_STD_6, "52_34_0194_10092334_V01",RCCIdName);
  next(S3UID::STEM_STD_7, "52_34_0195_10092335_V01",RCCIdName);
  next(S3UID::STEM_STD_8, "52_34_0196_10092336_V01",RCCIdName);
  next(S3UID::STEM_STD_9, "52_34_0197_10092337_V01",RCCIdName);
  next(S3UID::STEM_STD_10,"52_34_0198_10092338_V01",RCCIdName);
  next(S3UID::STEM_STD_11,"52_34_0199_10092339_V01",RCCIdName);
  next(S3UID::STEM_STD_12,"52_34_0200_10092340_V01",RCCIdName);
  next(S3UID::STEM_STD_13,"52_34_0211_10092351_V03",RCCIdName);
  next(S3UID::STEM_STD_14,"52_34_0212_10092352_V03",RCCIdName);

  next(S3UID::STEM_LAT_1, "52_34_1167_50028427_V02",RCCIdName);
  next(S3UID::STEM_LAT_2, "52_34_1168_50028426_V02",RCCIdName);
  next(S3UID::STEM_LAT_3, "52_34_0201_10092341_V01",RCCIdName);
  next(S3UID::STEM_LAT_4, "52_34_0202_10092342_V01",RCCIdName);
  next(S3UID::STEM_LAT_5, "52_34_0203_10092343_V01",RCCIdName);
  next(S3UID::STEM_LAT_6, "52_34_0204_10092344_V01",RCCIdName);
  next(S3UID::STEM_LAT_7, "52_34_0205_10092345_V01",RCCIdName);
  next(S3UID::STEM_LAT_8, "52_34_0206_10092346_V01",RCCIdName);
  next(S3UID::STEM_LAT_9, "52_34_0207_10092347_V01",RCCIdName);
  next(S3UID::STEM_LAT_10,"52_34_0208_10092348_V01",RCCIdName);
  next(S3UID::STEM_LAT_11,"52_34_0209_10092349_V01",RCCIdName);
  next(S3UID::STEM_LAT_12,"52_34_0210_10092350_V01",RCCIdName);
  next(S3UID::STEM_LAT_13,"52_34_0221_10092361_V03",RCCIdName);
  next(S3UID::STEM_LAT_14,"52_34_0222_10092362_V03",RCCIdName);

}


void SboOptimys::parts(SboTPCatalogList& prodList)
{
  using namespace XXXStem;

  auto stemRange= new SboTPCPartMonoStem(productName(),SboAnatomLocation::None);
  stemRange->_iconSet=PartIcon;
  stemRange->_menuText=PartMenuText;
  stemRange->_tooltipText=PartTooltipText;
  stemRange->setDefaultLabel(s3(defaultS3StemUID));

  struct CCD_Optimys : public SboTPCPartMonoStem::CCD {

    virtual RT range(SboShape3Label l) const override {
      if(isCCD_STD(l)) return _rSTD;
      if(isCCD_LAT(l)) return _rLAT;
      return {};
    }

    virtual SboShape3Label similarLabel(SboShape3Label aL, SboShape3Label aNextCCDRange) const{
      const auto v=ranges();
      const auto itCurrR=std::find_if(v.begin(),v.end(),[&](const RT& x) { return x.label == getCCDRange(aL); });
      const auto itNextR=std::find_if(v.begin(),v.end(),[&](const RT& x) { return x.label == aNextCCDRange; });

      const auto lower=s3(lowerS3UID);

      auto offset=aL.uid() - itCurrR->startIdx - lower.uid();
      offset=getSimilarOffset(offset,itCurrR->label,itNextR->label);
      return lower.next(offset + itNextR->startIdx);
    }

    //0 follow neck origin
    //1 keep transform
    virtual int strategy(SboShape3Label nextLabel, SboShape3Label currLabel) const {
      HPROJ_DCHECK(!"strategy should never be called in rev 1");
      return 0;
    }


    virtual std::vector<RT> ranges() const override { return {_rSTD,_rLAT};}

    const RT _rSTD={0,  13, s3(XXXStem::S3UID::RANGE_CCD_STD),"STD"};
    const RT _rLAT={14, 27, s3(XXXStem::S3UID::RANGE_CCD_LAT),"LAT"};
  };

  stemRange->_CCDPart = std::make_unique<CCD_Optimys>();


  auto next=[&](S3UID e,QString s) { stemRange->push_back(new SboTPCatalogItem(stemRange,s3(e), ItemName,s));};

  next(S3UID::STEM_STD_1,"STD XS");
  next(S3UID::STEM_STD_2,"STD 0");
  next(S3UID::STEM_STD_3,"STD 1");
  next(S3UID::STEM_STD_4,"STD 2");
  next(S3UID::STEM_STD_5,"STD 3");
  next(S3UID::STEM_STD_6,"STD 4");
  next(S3UID::STEM_STD_7,"STD 5");
  next(S3UID::STEM_STD_8,"STD 6");
  next(S3UID::STEM_STD_9,"STD 7");
  next(S3UID::STEM_STD_10,"STD 8");
  next(S3UID::STEM_STD_11,"STD 9");
  next(S3UID::STEM_STD_12,"STD 10");
  next(S3UID::STEM_STD_13,"STD 11");
  next(S3UID::STEM_STD_14,"STD 12");

  next(S3UID::STEM_LAT_1,"LAT XS");
  next(S3UID::STEM_LAT_2,"LAT 0");
  next(S3UID::STEM_LAT_3,"LAT 1");
  next(S3UID::STEM_LAT_4,"LAT 2");
  next(S3UID::STEM_LAT_5,"LAT 3");
  next(S3UID::STEM_LAT_6,"LAT 4");
  next(S3UID::STEM_LAT_7,"LAT 5");
  next(S3UID::STEM_LAT_8,"LAT 6");
  next(S3UID::STEM_LAT_9,"LAT 7");
  next(S3UID::STEM_LAT_10,"LAT 8");
  next(S3UID::STEM_LAT_11,"LAT 9");
  next(S3UID::STEM_LAT_12,"LAT 10");
  next(S3UID::STEM_LAT_13,"LAT 11");
  next(S3UID::STEM_LAT_14,"LAT 12");


  prodList.push_back(stemRange);


  //NOTE: Last argument S3UID::HEAD_P4 locates the CONE Lateral tip.
  //NOTE: The default label must be different from HEAD_P4 to be able to compute the cone axis.
  auto headRange= new SboTPCPartHead(productName(),s3(S3UID::HEAD_P4));
  headRange->_iconSet=PartHeadIcon;
  headRange->_menuText=PartHeadMenuText;
  headRange->_tooltipText=PartHeadTooltipText;
  headRange->setDefaultLabel(s3(defaultS3HeadUID));
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


bool SboOptimys::inRange(SboShape3Label aL)
{
  using namespace XXXStem;
  return SboML::in_closed_range<SboShape3Label>(aL,s3(lowerS3UID),s3(upperS3UID));
}

SboMatrix3 SboOptimys::headToNeckMatrix(SboShape3Label aHeadLabel, SboShape3Label aNeckLabel)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aHeadLabel);
  HPROJ_UNUSED(aNeckLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboOptimys::neckToStemMatrix(SboShape3Label aNeckLabel, SboShape3Label aStemLabel, SboAnatomLocation aSide)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aNeckLabel);
  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboOptimys::headToStemMatrix(SboShape3Label aHeadLabel, SboShape3Label aStemLabel)
{
  //NOTE: Requested for mono-block stem

  //NOTE: CS & scenegraph programming [[hdoch:capture-hproj-dev.org::EZCS]]

  //The HEAD point item has a default position at (0,0,0)
  //The HEAD point in CPT_FRAME is specified by the manufacturer

  //return the traffo that maps (0,0,0) to HEAD (including offset) in CPT_FRAME

  //Reference is diameter 36 (NB: 32 is the most common !?)

  using namespace XXXStem;

  const float tx=isCCD_STD(aStemLabel) ? -12.5f : -8.5f;

  float ty=getHeadTop(aStemLabel);
  if(aHeadLabel == s3(S3UID::HEAD_M4)) ty-=8.f;
  else if(aHeadLabel == s3(S3UID::HEAD_P0)) ty-=4.f;
  else if(aHeadLabel == s3(S3UID::HEAD_P8)) ty+=4.f;

  return SboML::rotMatZ3(SboML::deg2Rad<float>(-45.0f)) * SboML::transMat3(tx,ty,0);
}


SboPlane3 SboOptimys::cutPlane(SboShape3Label aStemLabel)
{
  //return the cutplane equation in CPT_FRAME

  //The cutplane is used to position the component in WORD_CS (STD_FRAME)

  //Default plane position and orientation: centered at (0,0,0) with normal (0,1,0)
  //Should return something like Plane3(Point3(0,0,0),Vector3(0,1,0)).transform(m)
  //Compute the TRAFFFO m

  //FIXME: Plane3 origin is supposed to be the neck origin

  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;

  //compute neck origin
  const float tx=isCCD_STD(aStemLabel) ? -12.5f : -8.5f;
  auto m0=SboML::rotMatZ3(SboML::deg2Rad<float>(-45.0f)) * SboML::transMat3(tx,0,0);
  auto neckO=m0(SboPoint3(0,0,0));

  //transform the plane
  auto m=SboML::transMat3(neckO) * SboML::rotMatZ3(SboML::deg2Rad<float>(-45.0f));
  return SboPlane3(SboPoint3(0,0,0), SboVector3(0,1,0)).transform(m);



  return {};

}

SboBbox3 SboOptimys::cutPlaneBbox(SboShape3Label aStemLabel)
{
  //return a bbox in CPT_FRAME that intersects the cutplane

  //NOTE: if the intersection is empty, the trace of the plane is not
  //visible.

  //Consider a bbox of dimensions (50,50,50) centered at (0,0,0)
  //Strategy the bbox center must be translated to the neck origin


  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;

  SboPoint3 pmin(-30.0f,-25.0f,-25.0f);
  SboPoint3 pmax(30.0f,25.0f,25.0f);

  //compute neck origin
  const float tx=isCCD_STD(aStemLabel) ? -12.5f : -8.5f;
  auto m0=SboML::rotMatZ3(SboML::deg2Rad<float>(-45.0f)) * SboML::transMat3(tx,0,0);
  auto neckO=m0(SboPoint3(0,0,0));

  auto m=SboML::transMat3(neckO);

  pmin=m(pmin);
  pmax=m(pmax);

  return SboML::makeBbox3(pmin,pmax);
}

SboMatrix3 SboOptimys::stemToStemMatrix(const SboFemImplantConfig& aOriginFemIC,const SboFemImplantConfig& aTargetFemIC)
{
  //NOTE: return a TRAFFO that transforms from aOriginStemLabel to aTargetStemLabel in CPT_FRAME
  //LINK: [[hdoch:capture-hproj-implants.org::REV_STEMTOSTEM]]

  HPROJ_UNUSED(aOriginFemIC);
  HPROJ_UNUSED(aTargetFemIC);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboOptimys::normalTrf(SboShape3Label aStemLabel, const SboPlane3 & aP3, const SboPoint3 & aO3)
{

  //return the TRAFFO from CPT_FRAME to NORMAL_FRAME

  //NORMAL_FRAME is oriented like the DICOM FRAME or the STD_FRAME
  //LINK [[hdoch:capture-hproj-implants.org::STEM_NORMAL_FR]]

  //NOTE: NORMAL_TRAFFO is used to position the first stem
  //In NORMAL_FRAME, the neck origin is then mapped directly into the FemurFrame origin.

  HPROJ_UNUSED(aStemLabel);
  HPROJ_UNUSED(aP3);
  HPROJ_UNUSED(aO3);

  using namespace XXXStem;

  //from Y normal frame to NORMAL_FRAME
  return SboML::rotMatX3(SboML::deg2Rad<float>(90.0f));

}

SboVector3 SboOptimys::offsetFF(SboShape3Label aStemLabel)
{

  // independently of the side (left or right)
  // x > 0 cpt moves medially
  // y > 0 cpt moves posteriorly
  // z > 0 cpt moves superiorly

  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;

  return {0.f,0.f,0.f};
}


SboFemImplantConfig SboOptimys::defaultFemIC(QString aPartName,SboAnatomLocation aRequestedSide)
{
  using namespace XXXStem;

  SboFemImplantConfig myFemIC(aRequestedSide,s3(defaultS3StemUID),s3(defaultS3HeadUID));
  myFemIC.setCutPlaneLabel(s3(S3UID::CUTPLANE));
  myFemIC.setStemProductName(productName());
  myFemIC.setDistalShaftProductName(productName());
  myFemIC.setHeadProductName(productName());
  myFemIC.setNeckProductName({});
  myFemIC.setImplantSide(SboAnatomLocation::None); //::None for straight stem
  myFemIC.setValidAssembly(false);

  myFemIC=fillAndValidAssembly(myFemIC);
  HPROJ_DCHECK2(myFemIC.isValidAssembly(),"");

  return myFemIC;
}

SboFemImplantConfig SboOptimys::fillAndValidAssembly(const SboFemImplantConfig& aFemIC)
{
  using namespace XXXStem;

  auto myFemIC=aFemIC;
  myFemIC.setValidAssembly(false);

  if( myFemIC.requestedSide() != SboAnatomLocation::None){
    const bool bs=isStem(myFemIC.stemLabel());
    const bool bh=isHead(myFemIC.headLabel());
    const bool bn=!myFemIC.neckLabel().isSet();

    if(!myFemIC.cutPlaneLabel().isSet()) myFemIC.setCutPlaneLabel(s3(S3UID::CUTPLANE));

    const bool b=bs && bh && bn;

    if(b){
      myFemIC.setStemProductName(productName());
      myFemIC.setDistalShaftProductName({});
      myFemIC.setHeadProductName(productName());
      myFemIC.setNeckProductName({});
      myFemIC.setImplantSide(SboAnatomLocation::None); //::None for straight stem
      myFemIC.setValidAssembly(true);
    }
  }

  return myFemIC;


}

SboFemImplantConfig SboOptimys::nextPrev(const SboFemImplantConfig& aFemIC,bool aNext)
{
  using namespace XXXStem;

  auto fc=aFemIC;
  fc.setStemLabel(nextPrevStem(fc.stemLabel(),aNext));

  return fc;
}

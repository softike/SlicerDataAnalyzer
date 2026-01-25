/*=========================================================================
  HPROJECT
  Copyright (c) Ernesto Durante, Julien de Siebenthal
  All rights reserved.
  See Copyrights.txt for details
  =========================================================================*/

#include "SboEcofitStem.h"

#include "SboTPCatalogElement.h"
#include "SboTPCatalogList.h"
#include "SboMathLibBase.h"
#include "SboPluginDefs.h"

#include <QDir>
#include <QIcon>

#define ICONSET_STR(s) QIcon(":/TPCatalogIcons/" s)

namespace XXXStem {
  constexpr auto ProductRangeStartsAt = hproj::ICAST::productRangeStartsAt(hproj::ICAST::Product::ECOFITSTEMLESS);

  constexpr auto CompanyName = hproj::ICAST::companyName;
  constexpr auto ProductName = hproj::ICAST::productName(hproj::ICAST::Product::ECOFITSTEMLESS);

  constexpr auto RCCIdName   = hproj::ICAST::RCCIdName(hproj::ICAST::Product::ECOFITSTEMLESS);
  constexpr auto RCCFileName = hproj::ICAST::RCCFileName(hproj::ICAST::Product::ECOFITSTEMLESS);
  constexpr auto RCCPath     = hproj::ICAST::RCCPath(hproj::ICAST::Product::ECOFITSTEMLESS);

  const QIcon   PartIcon=ICONSET_STR("generic_stem.png");
  const QString PartMenuText("");
  const QString PartTooltipText("");
  const QString ItemName=hproj::ICAST::itemName(hproj::ICAST::Product::ECOFITSTEMLESS);

  const QIcon   PartHeadIcon=ICONSET_STR("spcl_head.png");
  const QString PartHeadMenuText("");
  const QString PartHeadTooltipText("");

  enum class S3UID: SboShape3UID{
    STEM_STD_133_0 = ProductRangeStartsAt + 90L,
    STEM_STD_133_1,
    STEM_STD_133_2,
    STEM_STD_133_3,
    STEM_STD_133_4,
    STEM_STD_133_5,
    STEM_STD_133_6,
    STEM_STD_133_7,
    STEM_STD_133_8,
    STEM_STD_133_9,
    STEM_STD_133_10,
    STEM_STD_133_11,

    STEM_LAT_133_0,
    STEM_LAT_133_1,
    STEM_LAT_133_2,
    STEM_LAT_133_3,
    STEM_LAT_133_4,
    STEM_LAT_133_5,
    STEM_LAT_133_6,
    STEM_LAT_133_7,
    STEM_LAT_133_8,
    STEM_LAT_133_9,
    STEM_LAT_133_10,
    STEM_LAT_133_11,

    STEM_STD_138_0,
    STEM_STD_138_1,
    STEM_STD_138_2,
    STEM_STD_138_3,
    STEM_STD_138_4,
    STEM_STD_138_5,
    STEM_STD_138_6,
    STEM_STD_138_7,
    STEM_STD_138_8,
    STEM_STD_138_9,

    STEM_LAT_138_0,
    STEM_LAT_138_1,
    STEM_LAT_138_2,
    STEM_LAT_138_3,
    STEM_LAT_138_4,
    STEM_LAT_138_5,
    STEM_LAT_138_6,
    STEM_LAT_138_7,
    STEM_LAT_138_8,
    STEM_LAT_138_9,

    STEM_CV_0,
    STEM_CV_1,
    STEM_CV_2,
    STEM_CV_3,
    STEM_CV_4,
    STEM_CV_5,
    STEM_CV_6,
    STEM_CV_7,
    STEM_CV_8,
    STEM_CV_9,

    CUTPLANE,
    HEAD_M4,
    HEAD_P0,
    HEAD_P4,
    HEAD_P8,
    RANGE_CCD_STD_133,
    RANGE_CCD_LAT_133,
    RANGE_CCD_STD_138,
    RANGE_CCD_LAT_138,
    RANGE_CCD_CV

  };

  const S3UID lowerS3UID=S3UID::STEM_STD_133_0;
  const S3UID upperS3UID=S3UID::RANGE_CCD_CV;

  const S3UID defaultS3StemUID=S3UID::STEM_STD_133_5;
  const S3UID defaultS3HeadUID=S3UID::HEAD_P0;

  SboShape3Label s3( S3UID e) { return SboShape3Label(SboShape3Label::utype(e));}

  bool isCCD_STD_133(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_STD_133_0),s3(S3UID::STEM_STD_133_11));
  }

  bool isCCD_LAT_133(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_LAT_133_0),s3(S3UID::STEM_LAT_133_11));
  }

  bool isCCD_STD_138(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_STD_138_0),s3(S3UID::STEM_STD_138_9));
  }

  bool isCCD_LAT_138(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_LAT_138_0),s3(S3UID::STEM_LAT_138_9));
  }

  bool isCCD_CV(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_CV_0),s3(S3UID::STEM_CV_9));
  }

  bool isCCD_133(SboShape3Label l) {
    return isCCD_STD_133(l) || isCCD_LAT_133(l);
  }

  bool isStem(SboShape3Label l) {
    return isCCD_STD_133(l) || isCCD_LAT_133(l) || isCCD_STD_138(l) || isCCD_LAT_138(l) || isCCD_CV(l);
  }

  bool isHead(SboShape3Label l){
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::HEAD_M4),s3(S3UID::HEAD_P8));
  }

  bool isSubRange(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::RANGE_CCD_STD_133),s3(S3UID::RANGE_CCD_CV));
  }

  bool isSubRange133(SboShape3Label l) {
    return l==s3(S3UID::RANGE_CCD_STD_133) || l==s3(S3UID::RANGE_CCD_LAT_133);
  }

  struct R {
    int r0=0; int r1=0;
    SboShape3Label label0;
    SboShape3Label subRange;

    SboShape3Label next(SboShape3Label aL,int aStep) const {
      auto l=aL.next(aStep);
      return inSubRange(l) ? l: aL;
    }

    int size(SboShape3Label aL) const {
      return inSubRange(aL) ? idx(aL): 0;
    }

    int clampSize(int sz) const {
      return SboML::clamp<int>(sz,r0,r1);
    }

  protected:
    int idx(SboShape3Label aL) const { return aL - label0; }

    bool inSubRange(SboShape3Label aL) const {
      const auto sz=idx(aL);
      return (sz >= r0 && sz<=r1);
    }

  };


  auto getRangeStats(SboShape3Label aL) {
    HPROJ_DCHECK2(isStem(aL) || isSubRange(aL),"must be stem or range");

    auto myRL=aL;

    if(isStem(aL)){
      if(isCCD_STD_133(aL))   myRL=s3(S3UID::RANGE_CCD_STD_133);
      if(isCCD_LAT_133(aL))   myRL=s3(S3UID::RANGE_CCD_LAT_133);
      if(isCCD_STD_138(aL))   myRL=s3(S3UID::RANGE_CCD_STD_138);
      if(isCCD_LAT_138(aL))   myRL=s3(S3UID::RANGE_CCD_LAT_138);
      if(isCCD_CV(aL))   myRL=s3(S3UID::RANGE_CCD_CV);
    }


    if(isSubRange(myRL)){
      if(myRL==s3(S3UID::RANGE_CCD_STD_133)) return R{0,11, s3(S3UID::STEM_STD_133_0),myRL};
      if(myRL==s3(S3UID::RANGE_CCD_LAT_133)) return R{0,11, s3(S3UID::STEM_LAT_133_0),myRL};
      if(myRL==s3(S3UID::RANGE_CCD_STD_138)) return R{0,9, s3(S3UID::STEM_STD_138_0),myRL};
      if(myRL==s3(S3UID::RANGE_CCD_LAT_138)) return R{0,9, s3(S3UID::STEM_LAT_138_0),myRL};
      if(myRL==s3(S3UID::RANGE_CCD_CV))      return R{0,9, s3(S3UID::STEM_CV_0),myRL};
    }

    return R{};
  }


  SboShape3Label nextPrevStem(SboShape3Label aL,bool aNext){
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    return getRangeStats(aL).next(aL,aNext? 1: -1);
  }


  SboShape3Label getSimilarLabel(SboShape3Label aLabel, SboShape3Label aTargetR){

    HPROJ_DCHECK2(isStem(aLabel) || isSubRange(aLabel),"must be stem & range");

    const auto S=getRangeStats(aLabel);
    const auto sourceR=S.subRange;
    const auto sz=S.size(aLabel);
    const auto T=getRangeStats(aTargetR);
    auto tsz=sz;

    if(!isSubRange133(sourceR) && isSubRange133(aTargetR)){

      if(sz==8) tsz=9;
      else if(sz==9) tsz=11;

    }
    else if(isSubRange133(sourceR) && !isSubRange133(aTargetR)){

      if(sz==9) tsz=8;
      else if(sz==11) tsz=9;

    }

    tsz=T.clampSize(tsz);
    return T.label0.next(tsz);
  }

  SboPoint3 getRES_01(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto S=getRangeStats(aLabel);
    const auto sourceR=S.subRange;
    const auto sz=S.size(aLabel);

    float x=0.f,y=0.f,z=0.f;

    return SboPoint3{x,y,z};
  }

  SboPoint3 getRES_02(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");
    // (x,y,z)	133° Std	138° Std	coxa vara	133° Lat	138° Lat
    // RES01	(0,0,0)	(0,0,0)	(0,0,0)	(0,0,0)	(0,0,0)
    // RES02	(10.69,-9.21,0)	(10.5,-9.45,0)	(10.27,-9.93,0)	(6.55,-5.9,0)	6.54,-5.89,0)
    // TPR01	(25.09,23.39,0)	(23.02,25.56,0)	(27.12,17.61,0)	(29.25,27.28,0)	(26.77,29.74,0)

    const auto S=getRangeStats(aLabel);
    const auto sourceR=S.subRange;
    const auto sz=S.size(aLabel);

    float x=0.f,y=0.f,z=0.f;

    if(isCCD_STD_133(aLabel)){
      x=10.69f;
      y=-9.21f;
    }
    else if(isCCD_STD_138(aLabel)){
      x=10.5f;
      y=-9.45f;
    }
    else if(isCCD_CV(aLabel)){
      x=10.27f;
      y=-9.93f;
    }
    else if(isCCD_LAT_133(aLabel)){
      x=6.55f;
      y=-5.9f;
    }
    else if(isCCD_LAT_138(aLabel)){
      x=6.54f;
      y=-5.89f;
    }


    return SboPoint3{x,y,z};
  }

  SboPoint3 getTPR_01(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto S=getRangeStats(aLabel);
    const auto sourceR=S.subRange;
    const auto sz=S.size(aLabel);

    float x=0.f,y=0.f,z=0.f;

    if(isCCD_STD_133(aLabel)){
      x=25.09f;
      y=23.39f;
    }
    else if(isCCD_STD_138(aLabel)){
      x=23.02f;
      y=25.56f;
    }
    else if(isCCD_CV(aLabel)){
      x=27.12f;
      y=17.61f;
    }
    else if(isCCD_LAT_133(aLabel)){
      x=29.25f;
      y=27.28f;
    }
    else if(isCCD_LAT_138(aLabel)){
      x=26.77f;
      y=29.74f;
    }


    return SboPoint3{x,y,z};
  }



}

int SboEcofitStem::rev() const
{
  return 1;
}

QString SboEcofitStem::productName() const
{
  return XXXStem::ProductName;
}

QString SboEcofitStem::companyName() const
{
  return XXXStem::CompanyName;
}

QString SboEcofitStem::message(int,const SboFemImplantConfig&) const
{
  return "Insert a meaningful message";
}

QString SboEcofitStem::setMeshInfoSearchPath(QString aPath)
{
  using namespace XXXStem;

  //http://doc.qt.io/qt-5/qdir.html#setSearchPaths
  //Load resource from the system file
  QString myRcc;
  if(meshInfoResourceFromRcc(myRcc))
    QDir::setSearchPaths(RCCIdName, QStringList(QString(":") + RCCPath));
  else {
    //meshes are loaded from the disk
    //qDebug() << aPath + RCCPath + "/STD";
    //See also MeshInfoCollection::addCRef()
    QDir::setSearchPaths(RCCIdName, {aPath + RCCPath + "/STD_133",
                                     aPath + RCCPath + "/LAT_133",
                                     aPath + RCCPath + "/STD_138",
                                     aPath + RCCPath + "/LAT_138",
                                     aPath + RCCPath + "/CV"});
  }

  return {};
}

bool SboEcofitStem::meshInfoResourceFromRcc(QString& aRcc)
{
  aRcc=XXXStem::RCCFileName;
  return false;
}

bool SboEcofitStem::meshInfoResourceFromFileSystem()
{
  return true;
}


void SboEcofitStem::meshInfoRCList(SboMeshInfoRCList& rcList)
{
  using namespace XXXStem;
  auto next=[&](S3UID e,QString s,QString aRCCId) { rcList.push_back({s3(e),aRCCId + QString(":") + s + ".wrl"});};

  next(S3UID::STEM_STD_133_0, "30363062_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_1, "30363075_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_2, "30363087_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_3, "30363100_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_4, "30363112_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_5, "30363125_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_6, "30363137_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_7, "30363150_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_8, "30363162_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_9, "30363175_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_10,"30363187_133" ,RCCIdName);
  next(S3UID::STEM_STD_133_11,"30363200_133" ,RCCIdName);


  next(S3UID::STEM_LAT_133_0, "30364062_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_1, "30364075_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_2, "30364087_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_3, "30364100_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_4, "30364112_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_5, "30364125_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_6, "30364137_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_7, "30364150_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_8, "30364162_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_9, "30364175_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_10,"30364187_133Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_133_11,"30364200_133Lat" ,RCCIdName);


  next(S3UID::STEM_STD_138_0, "30383062_138" ,RCCIdName);
  next(S3UID::STEM_STD_138_1, "30383075_138" ,RCCIdName);
  next(S3UID::STEM_STD_138_2, "30383087_138" ,RCCIdName);
  next(S3UID::STEM_STD_138_3, "30383100_138" ,RCCIdName);
  next(S3UID::STEM_STD_138_4, "30383112_138" ,RCCIdName);
  next(S3UID::STEM_STD_138_5, "30383125_138" ,RCCIdName);
  next(S3UID::STEM_STD_138_6, "30383137_138" ,RCCIdName);
  next(S3UID::STEM_STD_138_7, "30383150_138" ,RCCIdName);
  next(S3UID::STEM_STD_138_8, "30383175_138" ,RCCIdName);
  next(S3UID::STEM_STD_138_9, "30383200_138" ,RCCIdName);

  next(S3UID::STEM_LAT_138_0, "30384062_138Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_138_1, "30384075_138Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_138_2, "30384087_138Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_138_3, "30384100_138Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_138_4, "30384112_138Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_138_5, "30384125_138Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_138_6, "30384137_138Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_138_7, "30384150_138Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_138_8, "30384175_138Lat" ,RCCIdName);
  next(S3UID::STEM_LAT_138_9, "30384200_138Lat" ,RCCIdName);

  next(S3UID::STEM_CV_0, "30382062_CV" ,RCCIdName);
  next(S3UID::STEM_CV_1, "30382075_CV" ,RCCIdName);
  next(S3UID::STEM_CV_2, "30382087_CV" ,RCCIdName);
  next(S3UID::STEM_CV_3, "30382100_CV" ,RCCIdName);
  next(S3UID::STEM_CV_4, "30382112_CV" ,RCCIdName);
  next(S3UID::STEM_CV_5, "30382125_CV" ,RCCIdName);
  next(S3UID::STEM_CV_6, "30382137_CV" ,RCCIdName);
  next(S3UID::STEM_CV_7, "30382150_CV" ,RCCIdName);
  next(S3UID::STEM_CV_8, "30382175_CV" ,RCCIdName);
  next(S3UID::STEM_CV_9, "30382200_CV" ,RCCIdName);

}

void SboEcofitStem::parts(SboTPCatalogList& prodList)
{
  using namespace XXXStem;

  auto stemRange= new SboTPCPartMonoStem(productName(),SboAnatomLocation::None);
  stemRange->_iconSet=PartIcon;
  stemRange->_menuText=PartMenuText;
  stemRange->_tooltipText=PartTooltipText;
  stemRange->setDefaultLabel(s3(defaultS3StemUID));


  struct CCD_SUPER : public SboTPCPartMonoStem::CCD {

    RT range(SboShape3Label l) const override {
      if(isCCD_STD_133(l)) return _rSTD_133;
      if(isCCD_LAT_133(l)) return _rLAT_133;
      if(isCCD_STD_138(l)) return _rSTD_138;
      if(isCCD_LAT_138(l)) return _rLAT_138;
      if(isCCD_CV(l)) return _rCV;

      return {};
    }

    SboShape3Label similarLabel(SboShape3Label aL, SboShape3Label aNextCCDRange) const override{

      return getSimilarLabel(aL,aNextCCDRange);
    }

    int strategy(SboShape3Label /*nextLabel*/, SboShape3Label /*currLabel*/) const override{
      HPROJ_DCHECK(!"strategy should never be called in rev 1");
      //0 follow neck origin
      //1 keep transform
      return 0;
    }


    std::vector<RT> ranges() const override { return {_rSTD_138,_rLAT_138,_rCV,_rSTD_133,_rLAT_133};}

    const RT _rSTD_133={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_STD_133),"133 STD"};
    const RT _rLAT_133={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_LAT_133),"133 LAT"};
    const RT _rSTD_138={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_STD_138),"138 STD"};
    const RT _rLAT_138={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_LAT_138),"138 LAT"};
    const RT _rCV={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_CV),"123 STD"};

  };

  stemRange->_CCDPart = std::make_unique<CCD_SUPER>();


  auto next=[&](S3UID e,QString s) { stemRange->push_back(new SboTPCatalogItem(stemRange,s3(e), ItemName,s));};

  next(S3UID::STEM_STD_133_0, "133 STD 6,25");
  next(S3UID::STEM_STD_133_1, "133 STD 7,5");
  next(S3UID::STEM_STD_133_2, "133 STD 8,75");
  next(S3UID::STEM_STD_133_3, "133 STD 10");
  next(S3UID::STEM_STD_133_4, "133 STD 11,25");
  next(S3UID::STEM_STD_133_5, "133 STD 12,5");
  next(S3UID::STEM_STD_133_6, "133 STD 13,75");
  next(S3UID::STEM_STD_133_7, "133 STD 15");
  next(S3UID::STEM_STD_133_8, "133 STD 16,25");
  next(S3UID::STEM_STD_133_9, "133 STD 17,5");
  next(S3UID::STEM_STD_133_10,"133 STD 18,75");
  next(S3UID::STEM_STD_133_11,"133 STD 20");

  next(S3UID::STEM_LAT_133_0, "133 LAT 6,25");
  next(S3UID::STEM_LAT_133_1, "133 LAT 7,5");
  next(S3UID::STEM_LAT_133_2, "133 LAT 8,75");
  next(S3UID::STEM_LAT_133_3, "133 LAT 10");
  next(S3UID::STEM_LAT_133_4, "133 LAT 11,25");
  next(S3UID::STEM_LAT_133_5, "133 LAT 12,5");
  next(S3UID::STEM_LAT_133_6, "133 LAT 13,75");
  next(S3UID::STEM_LAT_133_7, "133 LAT 15");
  next(S3UID::STEM_LAT_133_8, "133 LAT 16,25");
  next(S3UID::STEM_LAT_133_9, "133 LAT 17.5");
  next(S3UID::STEM_LAT_133_10,"133 LAT 18,75");
  next(S3UID::STEM_LAT_133_11,"133 LAT 20");

  next(S3UID::STEM_STD_138_0, "138 STD 6,25");
  next(S3UID::STEM_STD_138_1, "138 STD 7,5");
  next(S3UID::STEM_STD_138_2, "138 STD 8,75");
  next(S3UID::STEM_STD_138_3, "138 STD 10");
  next(S3UID::STEM_STD_138_4, "138 STD 11,25");
  next(S3UID::STEM_STD_138_5, "138 STD 12,5");
  next(S3UID::STEM_STD_138_6, "138 STD 13,75");
  next(S3UID::STEM_STD_138_7, "138 STD 15");
  next(S3UID::STEM_STD_138_8, "138 STD 17,5");
  next(S3UID::STEM_STD_138_9, "138 STD 20");

  next(S3UID::STEM_LAT_138_0, "138 LAT 6,25");
  next(S3UID::STEM_LAT_138_1, "138 LAT 7,5");
  next(S3UID::STEM_LAT_138_2, "138 LAT 8,75");
  next(S3UID::STEM_LAT_138_3, "138 LAT 10");
  next(S3UID::STEM_LAT_138_4, "138 LAT 11,25");
  next(S3UID::STEM_LAT_138_5, "138 LAT 12,5");
  next(S3UID::STEM_LAT_138_6, "138 LAT 13,75");
  next(S3UID::STEM_LAT_138_7, "138 LAT 15");
  next(S3UID::STEM_LAT_138_8, "138 LAT 17,5");
  next(S3UID::STEM_LAT_138_9, "138 LAT 20");

  next(S3UID::STEM_CV_0, "123 STD 6,25");
  next(S3UID::STEM_CV_1, "123 STD 7,5");
  next(S3UID::STEM_CV_2, "123 STD 8,75");
  next(S3UID::STEM_CV_3, "123 STD 10");
  next(S3UID::STEM_CV_4, "123 STD 11,25");
  next(S3UID::STEM_CV_5, "123 STD 12,5");
  next(S3UID::STEM_CV_6, "123 STD 13,75");
  next(S3UID::STEM_CV_7, "123 STD 15");
  next(S3UID::STEM_CV_8, "123 STD 17,5");
  next(S3UID::STEM_CV_9, "123 STD 20");

  prodList.push_back(stemRange);


  //NOTE: Last argument S3UID::HEAD_P4 locates the CONE Lateral tip.
  //NOTE: The default label must be different from HEAD_P4 to be able to compute the cone axis.
  auto headRange= new SboTPCPartHead(productName(),s3(S3UID::HEAD_P4));
  headRange->_iconSet=PartHeadIcon;
  headRange->_menuText=PartHeadMenuText;
  headRange->_tooltipText=PartHeadTooltipText;
  headRange->setDefaultLabel(s3(defaultS3HeadUID));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_M4),"Head","K(-4)"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P0),"Head","M(+0)"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P4),"Head","L(+4)"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P8),"Head","XL(+8)"));

  prodList.push_back(headRange);

  auto cutPlaneRange= new SboTPCPartCutPlane(productName());
  cutPlaneRange->setDefaultLabel(s3(S3UID::CUTPLANE));
  cutPlaneRange->push_back(new SboTPCatalogItem(cutPlaneRange,s3(S3UID::CUTPLANE),"Cutplane"));

  prodList.push_back(cutPlaneRange);

}


bool SboEcofitStem::inRange(SboShape3Label aL)
{
  using namespace XXXStem;
  return SboML::in_closed_range<SboShape3Label>(aL,s3(lowerS3UID),s3(upperS3UID));
}

SboMatrix3 SboEcofitStem::headToNeckMatrix(SboShape3Label aHeadLabel, SboShape3Label aNeckLabel)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aHeadLabel);
  HPROJ_UNUSED(aNeckLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboEcofitStem::neckToStemMatrix(SboShape3Label aNeckLabel, SboShape3Label aStemLabel, SboAnatomLocation aSide)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aNeckLabel);
  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboEcofitStem::headToStemMatrix(SboShape3Label aHeadLabel, SboShape3Label aStemLabel)
{
  //NOTE: Requested for mono-block stem

  //NOTE: CS & scenegraph programming [[hdoch:capture-hproj-dev.org::EZCS]]

  //The HEAD point item has a default position at (0,0,0)
  //The HEAD point in CPT_FRAME is specified by the manufacturer

  //return the traffo that maps (0,0,0) to HEAD (including offset) in CPT_FRAME

  //Reference is diameter 36 (NB: 32 is the most common !?)

  using namespace XXXStem;

  const auto neckO=getRES_01(aStemLabel);
  const auto headO=getTPR_01(aStemLabel);
  const auto neckAxis = SboML::unit3(headO - neckO);

  float l=0;//SboML::norm3(headO-neckO);

  if(aHeadLabel == s3(S3UID::HEAD_M4))      l-=3.53f;
  else if(aHeadLabel == s3(S3UID::HEAD_P0)) l=0.f;
  else if(aHeadLabel == s3(S3UID::HEAD_P4)) l+=3.53f;
  else if(aHeadLabel == s3(S3UID::HEAD_P8)) l+=7.1f;

  auto m=SboML::transMat3(headO + neckAxis * l);

  return m;
}


SboPlane3 SboEcofitStem::cutPlane(SboShape3Label aStemLabel)
{
  //return the cutplane equation in CPT_FRAME

  //The cutplane is used to position the component in WORD_CS (STD_FRAME)

  //Default plane position and orientation: centered at (0,0,0) with normal (0,1,0)
  //Should return something like Plane3(Point3(0,0,0),Vector3(0,1,0)).transform(m)
  //Compute the TRAFFFO m

  //FIXME: Plane3 origin is supposed to be the neck origin

  using namespace XXXStem;
  const auto neckO=getRES_01(aStemLabel);

  //Y form orientation
  auto rz=SboML::rotMatZ3(SboML::deg2Rad<float>(-42.0f));
  auto t=SboML::transMat3(neckO);
  auto m=t*rz;

  return SboPlane3(SboPoint3(0,0,0), SboVector3(0,1,0)).transform(m);

}

SboBbox3 SboEcofitStem::cutPlaneBbox(SboShape3Label aStemLabel)
{
  //return a bbox in CPT_FRAME that intersects the cutplane

  //NOTE: if the intersection is empty, the trace of the plane is not
  //visible.

  //Consider a bbox of dimensions (50,50,50) centered at (0,0,0)
  //Strategy the bbox center must be translated to the neck origin


  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;

  SboPoint3 pmin(-25.0f,-25.0f,-25.0f);
  SboPoint3 pmax(25.0f,25.0f,25.0f);

  const auto neckO=getRES_01(aStemLabel);
  auto m=SboML::transMat3(neckO);

  pmin=m(pmin);
  pmax=m(pmax);

  return SboML::makeBbox3(pmin,pmax);
}

SboMatrix3 SboEcofitStem::stemToStemMatrix(const SboFemImplantConfig& aOriginFemIC,const SboFemImplantConfig& aTargetFemIC)
{
  //NOTE: return a TRAFFO that transforms from aOriginStemLabel to aTargetStemLabel in CPT_FRAME
  //LINK: [[hdoch:capture-hproj-implants.org::REV_STEMTOSTEM]]

  using namespace XXXStem;
  // auto neckO =getRES_01(aOriginFemIC.stemLabel());
  // auto neckTO=getRES_01(aTargetFemIC.stemLabel());

  //RES_02 is the most medial point on the R plane
  auto neck2 =getRES_02(aOriginFemIC.stemLabel());
  auto neckT2=getRES_02(aTargetFemIC.stemLabel());

  return SboML::transMat3(neck2 - neckT2);
}

SboMatrix3 SboEcofitStem::normalTrf(SboShape3Label aStemLabel, const SboPlane3 & aP3, const SboPoint3 & aO3)
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

  //Y_FRAME frame to NORMAL_FRAME
  return SboML::rotMatX3(SboML::deg2Rad<float>(90.0f));
}

SboVector3 SboEcofitStem::offsetFF(SboShape3Label aStemLabel)
{
  //STD_FRAME is the reference frame
  // independently of the side (left or right)
  // x > 0 cpt moves medially
  // y > 0 cpt moves posteriorly
  // z > 0 cpt moves superiorly

  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;

  return {15.f,0.f,10.f};
}


SboFemImplantConfig SboEcofitStem::defaultFemIC(QString aPartName,SboAnatomLocation aRequestedSide)
{
  using namespace XXXStem;

  //NOTE: for a side free stem, consider the following ctor instead
  //SboFemImplantConfig myFemIC(aRequestedSide,s3(defaultS3StemRUID),s3(defaultS3HeadUID));

  //NOTE: for anatomical stem, consider instead
  SboFemImplantConfig myFemIC(aRequestedSide,s3(defaultS3StemUID),s3(defaultS3HeadUID));
  myFemIC.setCutPlaneLabel(s3(S3UID::CUTPLANE));
  myFemIC.setStemProductName(productName());
  myFemIC.setDistalShaftProductName(productName());
  myFemIC.setHeadProductName(productName());
  myFemIC.setNeckProductName({});
  myFemIC.setImplantSide(aRequestedSide); //NOTE: consider SboAnatomLocation::None for straight stem
  myFemIC.setValidAssembly(false);

  myFemIC=fillAndValidAssembly(myFemIC);
  HPROJ_DCHECK2(myFemIC.isValidAssembly(),"not a valid FemIC assembly");

  return myFemIC;
}

SboFemImplantConfig SboEcofitStem::fillAndValidAssembly(const SboFemImplantConfig& aFemIC)
{
  using namespace XXXStem;

  auto myFemIC=aFemIC;
  myFemIC.setValidAssembly(false);

  if( myFemIC.requestedSide() != SboAnatomLocation::None){
    const bool bs=isStem(myFemIC.stemLabel());
    const bool bh=isHead(myFemIC.headLabel());
    const bool bn=!myFemIC.neckLabel().isSet();

    if(!myFemIC.cutPlaneLabel().isSet()) myFemIC.setCutPlaneLabel(s3(S3UID::CUTPLANE));

    const bool okSide = true;

    const bool b=bs && bh && bn && okSide;

    if(b){
      myFemIC.setStemProductName(productName());
      myFemIC.setDistalShaftProductName({});
      myFemIC.setHeadProductName(productName());
      myFemIC.setNeckProductName({});
      myFemIC.setImplantSide(myFemIC.requestedSide()); //NOTE: consider SboAnatomLocation::None for straight stem
      myFemIC.setValidAssembly(true);
    }
  }

  return myFemIC;


}

SboFemImplantConfig SboEcofitStem::nextPrev(const SboFemImplantConfig& aFemIC,bool aNext)
{
  using namespace XXXStem;

  auto fc=aFemIC;
  fc.setStemLabel(nextPrevStem(fc.stemLabel(),aNext));

  //NOTE: Don't check whether the config is a valid assembly or combination, let the application do it

  return fc;
}

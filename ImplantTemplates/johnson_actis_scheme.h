/*=========================================================================
  HPROJECT
  Copyright (c) Ernesto Durante, Julien de Siebenthal
  All rights reserved.
  See Copyrights.txt for details
  =========================================================================*/

#include "SboActis.h"

#include "SboTPCatalogElement.h"
#include "SboTPCatalogList.h"
#include "SboMathLibBase.h"
#include "SboPluginDefs.h"

#include <QDir>
#include <QIcon>

#define ICONSET_STR(s) QIcon(":/TPCatalogIcons/" s)

namespace XXXStem {
  constexpr auto ProductRangeStartsAt = hproj::JNJ::productRangeStartsAt(hproj::JNJ::Product::ACTIS);

  constexpr auto CompanyName = hproj::JNJ::companyName;
  constexpr auto ProductName = hproj::JNJ::productName(hproj::JNJ::Product::ACTIS);

  constexpr auto RCCIdName   = hproj::JNJ::RCCIdName(hproj::JNJ::Product::ACTIS);
  constexpr auto RCCFileName = hproj::JNJ::RCCFileName(hproj::JNJ::Product::ACTIS);
  constexpr auto RCCPath     = hproj::JNJ::RCCPath(hproj::JNJ::Product::ACTIS);

  const QIcon   PartIcon=ICONSET_STR("generic_stem.png");
  const QString PartMenuText("");
  const QString PartTooltipText("");
  const QString ItemName=hproj::JNJ::itemName(hproj::JNJ::Product::ACTIS);

  const QIcon   PartHeadIcon=ICONSET_STR("spcl_head.png");
  const QString PartHeadMenuText("");
  const QString PartHeadTooltipText("");

  enum class S3UID: SboShape3UID{
    STEM_STD_0 = ProductRangeStartsAt + 90L,
    STEM_STD_1,
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

    STEM_HO_0,
    STEM_HO_1,
    STEM_HO_2,
    STEM_HO_3,
    STEM_HO_4,
    STEM_HO_5,
    STEM_HO_6,
    STEM_HO_7,
    STEM_HO_8,
    STEM_HO_9,
    STEM_HO_10,
    STEM_HO_11,
    STEM_HO_12,

    CUTPLANE,
    HEAD_M4,
    HEAD_P0,
    HEAD_P4,
    HEAD_P8,
    RANGE_CCD_STD,
    RANGE_CCD_HO,
  };

  const S3UID lowerS3UID=S3UID::STEM_STD_0;
  const S3UID upperS3UID=S3UID::RANGE_CCD_HO;

  const S3UID defaultS3StemUID=S3UID::STEM_STD_6;
  const S3UID defaultS3HeadUID=S3UID::HEAD_P0;

  SboShape3Label s3( S3UID e) { return SboShape3Label(SboShape3Label::utype(e));}

  bool isCCD_STD(SboShape3Label l) {
    //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_STD_0),s3(S3UID::STEM_STD_12));
  }

  bool isCCD_HO(SboShape3Label l) {
    //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_HO_0),s3(S3UID::STEM_HO_12));
  }

  bool isStem(SboShape3Label l) {
    return isCCD_STD(l) || isCCD_HO(l);
  }

  bool isHead(SboShape3Label l){
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::HEAD_M4),s3(S3UID::HEAD_P8));
  }

  bool isSubRange(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::RANGE_CCD_STD),s3(S3UID::RANGE_CCD_HO));
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
      if(isCCD_STD(aL))   myRL=s3(S3UID::RANGE_CCD_STD);
      if(isCCD_HO(aL))   myRL=s3(S3UID::RANGE_CCD_HO);
    }


    if(isSubRange(myRL)){
      if(myRL==s3(S3UID::RANGE_CCD_STD)) return R{0,12, s3(S3UID::STEM_STD_0),myRL};
      if(myRL==s3(S3UID::RANGE_CCD_HO))  return R{0,12, s3(S3UID::STEM_HO_0),myRL};
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
    int tsz=sz;

    // if(sourceR == s3(S3UID::RANGE_CCD_STD)){
    //   if(aTargetR == s3(S3UID::RANGE_CCD_LAT))    tsz=T.clampSize(tsz);

    // }
    // else if(sourceR == s3(S3UID::RANGE_CCD_LAT)){

    //   if(aTargetR == s3(S3UID::RANGE_CCD_STD))    tsz=T.clampSize(tsz);
    // }

    return T.label0.next(tsz);
  }

  SboPoint3 getRES_01(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto S=getRangeStats(aLabel);
    const auto sourceR=S.subRange;
    const auto sz=S.size(aLabel);


    if( sourceR == s3(S3UID::RANGE_CCD_STD)){

      if( aLabel == s3(S3UID::STEM_STD_0))  return {11.94,  0,  10.02};
      if( aLabel == s3(S3UID::STEM_STD_1))  return {12.47 , 0 , 10.46};
      if( aLabel == s3(S3UID::STEM_STD_2))  return {13.27 , 0 , 11.14};
      if( aLabel == s3(S3UID::STEM_STD_3))  return {13.05 , 0 , 10.95};
      if( aLabel == s3(S3UID::STEM_STD_4))  return {13.56 , 0 , 11.38};
      if( aLabel == s3(S3UID::STEM_STD_5))  return {13.58 , 0 , 11.4 };
      if( aLabel == s3(S3UID::STEM_STD_6))  return {14.12 , 0 , 11.85};
      if( aLabel == s3(S3UID::STEM_STD_7))  return {14.14 , 0 , 11.87};
      if( aLabel == s3(S3UID::STEM_STD_8))  return {14.68 , 0 , 12.32};
      if( aLabel == s3(S3UID::STEM_STD_9))  return {14.7 ,  0 , 12.34};
      if( aLabel == s3(S3UID::STEM_STD_10)) return {15.29 , 0 , 12.83};
      if( aLabel == s3(S3UID::STEM_STD_11)) return {15.64 , 0 , 13.12};
      if( aLabel == s3(S3UID::STEM_STD_12)) return {16.04 , 0 , 13.46};

    }
    else {

      if( aLabel == s3(S3UID::STEM_HO_0))  return {15.1, 0, 12.67   };
      if( aLabel == s3(S3UID::STEM_HO_1))  return {15.47 , 0 , 12.98};
      if( aLabel == s3(S3UID::STEM_HO_2))  return {16.27 , 0 , 13.65};
      if( aLabel == s3(S3UID::STEM_HO_3))  return {16.05 , 0 , 13.46};
      if( aLabel == s3(S3UID::STEM_HO_4))  return {17.57 , 0 , 14.74};
      if( aLabel == s3(S3UID::STEM_HO_5))  return {17.58 , 0 , 14.76};
      if( aLabel == s3(S3UID::STEM_HO_6))  return {18.12 , 0 , 15.21};
      if( aLabel == s3(S3UID::STEM_HO_7))  return {18.14 , 0 , 15.22};
      if( aLabel == s3(S3UID::STEM_HO_8))  return {18.68 , 0 , 15.68};
      if( aLabel == s3(S3UID::STEM_HO_9))  return {18.7 ,  0 , 15.69};
      if( aLabel == s3(S3UID::STEM_HO_10)) return {19.29 , 0 , 16.19};
      if( aLabel == s3(S3UID::STEM_HO_11)) return {19.64 , 0 , 16.48};
      if( aLabel == s3(S3UID::STEM_HO_12)) return {20.04 , 0 , 16.82};
    }

    float x=0.f,y=0.f,z=0.f;
    return SboPoint3{x,y,z};
  }

  SboPoint3 getRES_02(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto S=getRangeStats(aLabel);
    const auto sourceR=S.subRange;
    const auto sz=S.size(aLabel);

    if( sourceR == s3(S3UID::RANGE_CCD_STD)){

      if( aLabel == s3(S3UID::STEM_STD_0))  return {20.01 , 0 ,  3.17};
      if( aLabel == s3(S3UID::STEM_STD_1))  return {21.01 , 0 ,  3.3 };
      if( aLabel == s3(S3UID::STEM_STD_2))  return {21.81 , 0 ,  3.98};
      if( aLabel == s3(S3UID::STEM_STD_3))  return {22.51 , 0 ,  3.01};
      if( aLabel == s3(S3UID::STEM_STD_4))  return {23.3 ,  0 ,  3.21};
      if( aLabel == s3(S3UID::STEM_STD_5))  return {24.1 ,  0 ,  2.57};
      if( aLabel == s3(S3UID::STEM_STD_6))  return {24.81 , 0 ,  2.89};
      if( aLabel == s3(S3UID::STEM_STD_7))  return {25.61 , 0 ,  2.25};
      if( aLabel == s3(S3UID::STEM_STD_8))  return {26.31 , 0 ,  2.57};
      if( aLabel == s3(S3UID::STEM_STD_9))  return {27.11 , 0 , 1.93 };
      if( aLabel == s3(S3UID::STEM_STD_10)) return {27.91 , 0 ,  2.24};
      if( aLabel == s3(S3UID::STEM_STD_11)) return {28.61 , 0 ,  2.24};
      if( aLabel == s3(S3UID::STEM_STD_12)) return {29.41 , 0 ,  2.24};

    }
    else {

      if( aLabel == s3(S3UID::STEM_HO_0))  return {20.21 , 0,   8.39};
      if( aLabel == s3(S3UID::STEM_HO_1))  return {21.01 , 0 ,  8.33};
      if( aLabel == s3(S3UID::STEM_HO_2))  return {21.81 , 0 ,  9.01};
      if( aLabel == s3(S3UID::STEM_HO_3))  return {22.51 , 0 ,  8.04};
      if( aLabel == s3(S3UID::STEM_HO_4))  return {23.31 , 0 ,  9.92};
      if( aLabel == s3(S3UID::STEM_HO_5))  return {24.11 , 0 ,  9.28};
      if( aLabel == s3(S3UID::STEM_HO_6))  return {24.82 , 0 ,  9.59};
      if( aLabel == s3(S3UID::STEM_HO_7))  return {25.61 , 0 ,  8.96};
      if( aLabel == s3(S3UID::STEM_HO_8))  return {26.31 , 0 ,  9.28};
      if( aLabel == s3(S3UID::STEM_HO_9))  return {27.11 , 0 , 8.64 };
      if( aLabel == s3(S3UID::STEM_HO_10)) return {27.91 , 0 ,  8.96};
      if( aLabel == s3(S3UID::STEM_HO_11)) return {28.61 , 0 ,  8.96};
      if( aLabel == s3(S3UID::STEM_HO_12)) return {29.41 , 0 ,  8.96};
    }


    float x=0.f,y=0.f,z=0.f;
    return SboPoint3{x,y,z};
  }

  SboPoint3 getTPR_01(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto S=getRangeStats(aLabel);
    const auto sourceR=S.subRange;
    const auto sz=S.size(aLabel);

    if( sourceR == s3(S3UID::RANGE_CCD_STD)){

      if( aLabel == s3(S3UID::STEM_STD_0))  return {36.29 ,  0 , 30.45};
      if( aLabel == s3(S3UID::STEM_STD_1))  return {36.44 ,  0 , 30.58};
      if( aLabel == s3(S3UID::STEM_STD_2))  return {38.44 ,  0 , 32.26};
      if( aLabel == s3(S3UID::STEM_STD_3))  return {38.24 ,  0 , 32.09};
      if( aLabel == s3(S3UID::STEM_STD_4))  return {39.85 ,  0 , 33.44};
      if( aLabel == s3(S3UID::STEM_STD_5))  return {39.66 ,  0 , 33.28};
      if( aLabel == s3(S3UID::STEM_STD_6))  return {41.66 ,  0 , 34.96};
      if( aLabel == s3(S3UID::STEM_STD_7))  return {41.66 ,  0 , 34.96};
      if( aLabel == s3(S3UID::STEM_STD_8))  return {43.66 ,  0 , 36.64};
      if( aLabel == s3(S3UID::STEM_STD_9))  return {43.66 ,  0 , 36.64};
      if( aLabel == s3(S3UID::STEM_STD_10)) return {45.66 ,  0 , 38.32};
      if( aLabel == s3(S3UID::STEM_STD_11)) return {45.66 ,  0 , 38.32};
      if( aLabel == s3(S3UID::STEM_STD_12)) return {45.66 ,  0 , 38.32};

    }
    else {

      if( aLabel == s3(S3UID::STEM_HO_0))  return {42.44,   0, 35.61 };
      if( aLabel == s3(S3UID::STEM_HO_1))  return {42.44 ,  0 , 35.61};
      if( aLabel == s3(S3UID::STEM_HO_2))  return {44.44 ,  0 , 37.29};
      if( aLabel == s3(S3UID::STEM_HO_3))  return {44.24 ,  0 , 37.12};
      if( aLabel == s3(S3UID::STEM_HO_4))  return {47.85 ,  0 , 40.15};
      if( aLabel == s3(S3UID::STEM_HO_5))  return {47.66 ,  0 , 39.99};
      if( aLabel == s3(S3UID::STEM_HO_6))  return {49.66 ,  0 , 41.67};
      if( aLabel == s3(S3UID::STEM_HO_7))  return {49.66 ,  0 , 41.67};
      if( aLabel == s3(S3UID::STEM_HO_8))  return {51.66 ,  0 , 43.35};
      if( aLabel == s3(S3UID::STEM_HO_9))  return {51.66 , 0 , 43.35 };
      if( aLabel == s3(S3UID::STEM_HO_10)) return {53.66 ,  0 , 45.03};
      if( aLabel == s3(S3UID::STEM_HO_11)) return {53.66 ,  0 , 45.03};
      if( aLabel == s3(S3UID::STEM_HO_12)) return {53.66 ,  0 , 45.03};
    }

    float x=0.f,y=0.f,z=0.f;
    return SboPoint3{x,y,z};
  }



}

int SboActis::rev() const
{
  return 1;
}

QString SboActis::productName() const
{
  return XXXStem::ProductName;
}

QString SboActis::companyName() const
{
  return XXXStem::CompanyName;
}

QString SboActis::message(int,const SboFemImplantConfig&) const
{
  return "Insert a meaningful message";
}

QString SboActis::setMeshInfoSearchPath(QString aPath)
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
    QDir::setSearchPaths(RCCIdName, {aPath + RCCPath + "/STD",
                                     aPath + RCCPath + "/HIGH"});
  }

  return {};
}

bool SboActis::meshInfoResourceFromRcc(QString& aRcc)
{
  aRcc=XXXStem::RCCFileName;
  return false;
}

bool SboActis::meshInfoResourceFromFileSystem()
{
  return true;
}


void SboActis::meshInfoRCList(SboMeshInfoRCList& rcList)
{
  using namespace XXXStem;
  auto next=[&](S3UID e,QString s,QString aRCCId) { rcList.push_back({s3(e),aRCCId + QString(":") + s + ".wrl"});};

  next(S3UID::STEM_STD_0,  "103794036 Rev 1",RCCIdName);
  next(S3UID::STEM_STD_1,  "103533729_1",RCCIdName);
  next(S3UID::STEM_STD_2,  "103534115_1",RCCIdName);
  next(S3UID::STEM_STD_3,  "103534118_1",RCCIdName);
  next(S3UID::STEM_STD_4,  "103534120_1",RCCIdName);
  next(S3UID::STEM_STD_5,  "103534121_1",RCCIdName);
  next(S3UID::STEM_STD_6,  "103534123_1",RCCIdName);
  next(S3UID::STEM_STD_7,  "103534124_1",RCCIdName);
  next(S3UID::STEM_STD_8,  "103534125_1",RCCIdName);
  next(S3UID::STEM_STD_9,  "103534127_1",RCCIdName);
  next(S3UID::STEM_STD_10, "103534129_1",RCCIdName);
  next(S3UID::STEM_STD_11, "103534132_1",RCCIdName);
  next(S3UID::STEM_STD_12, "103534133_1",RCCIdName);

  next(S3UID::STEM_HO_0,  "103794037 Rev 1",RCCIdName);
  next(S3UID::STEM_HO_1,  "103534134_1",RCCIdName);
  next(S3UID::STEM_HO_2,  "103534135_1",RCCIdName);
  next(S3UID::STEM_HO_3,  "103534138_1",RCCIdName);
  next(S3UID::STEM_HO_4,  "103534139_1",RCCIdName);
  next(S3UID::STEM_HO_5,  "103534144_1",RCCIdName);
  next(S3UID::STEM_HO_6,  "103534146_1",RCCIdName);
  next(S3UID::STEM_HO_7,  "103534147_1",RCCIdName);
  next(S3UID::STEM_HO_8,  "103534972_1",RCCIdName);
  next(S3UID::STEM_HO_9,  "103534973_1",RCCIdName);
  next(S3UID::STEM_HO_10, "103534974_1",RCCIdName);
  next(S3UID::STEM_HO_11, "103534976_1",RCCIdName);
  next(S3UID::STEM_HO_12, "103534977_1",RCCIdName);

}


void SboActis::parts(SboTPCatalogList& prodList)
{
  using namespace XXXStem;

  auto stemRange= new SboTPCPartMonoStem(productName(),SboAnatomLocation::None);
  stemRange->_iconSet=PartIcon;
  stemRange->_menuText=PartMenuText;
  stemRange->_tooltipText=PartTooltipText;
  stemRange->setDefaultLabel(s3(defaultS3StemUID));


  struct CCD_SUPER : public SboTPCPartMonoStem::CCD {

    RT range(SboShape3Label l) const override {
      if(isCCD_STD(l)) return _rSTD;
      if(isCCD_HO(l)) return _rHO;
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


    std::vector<RT> ranges() const override { return {_rSTD,_rHO};}

    const RT _rSTD={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_STD),"STD"};
    const RT _rHO={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_HO),"HIGH"};
  };

  stemRange->_CCDPart = std::make_unique<CCD_SUPER>();


  auto next=[&](S3UID e,QString s) { stemRange->push_back(new SboTPCatalogItem(stemRange,s3(e), ItemName,s));};

  next(S3UID::STEM_STD_0, "COLLARED STD 0");
  next(S3UID::STEM_STD_1, "COLLARED STD 1");
  next(S3UID::STEM_STD_2, "COLLARED STD 2");
  next(S3UID::STEM_STD_3, "COLLARED STD 3");
  next(S3UID::STEM_STD_4, "COLLARED STD 4");
  next(S3UID::STEM_STD_5, "COLLARED STD 5");
  next(S3UID::STEM_STD_6, "COLLARED STD 6");
  next(S3UID::STEM_STD_7, "COLLARED STD 7");
  next(S3UID::STEM_STD_8, "COLLARED STD 8");
  next(S3UID::STEM_STD_9, "COLLARED STD 9");
  next(S3UID::STEM_STD_10,"COLLARED STD 10");
  next(S3UID::STEM_STD_11,"COLLARED STD 11");
  next(S3UID::STEM_STD_12,"COLLARED STD 12");

  next(S3UID::STEM_HO_0, "COLLARED HIGH 0");
  next(S3UID::STEM_HO_1, "COLLARED HIGH 1");
  next(S3UID::STEM_HO_2, "COLLARED HIGH 2");
  next(S3UID::STEM_HO_3, "COLLARED HIGH 3");
  next(S3UID::STEM_HO_4, "COLLARED HIGH 4");
  next(S3UID::STEM_HO_5, "COLLARED HIGH 5");
  next(S3UID::STEM_HO_6, "COLLARED HIGH 6");
  next(S3UID::STEM_HO_7, "COLLARED HIGH 7");
  next(S3UID::STEM_HO_8, "COLLARED HIGH 8");
  next(S3UID::STEM_HO_9, "COLLARED HIGH 9");
  next(S3UID::STEM_HO_10,"COLLARED HIGH 10");
  next(S3UID::STEM_HO_11,"COLLARED HIGH 11");
  next(S3UID::STEM_HO_12,"COLLARED HIGH 12");


  prodList.push_back(stemRange);


  //NOTE: Last argument S3UID::HEAD_P4 locates the CONE Lateral tip.
  //NOTE: The default label must be different from HEAD_P4 to be able to compute the cone axis.
  auto headRange= new SboTPCPartHead(productName(),s3(S3UID::HEAD_P4));
  headRange->_iconSet=PartHeadIcon;
  headRange->_menuText=PartHeadMenuText;
  headRange->_tooltipText=PartHeadTooltipText;
  headRange->setDefaultLabel(s3(defaultS3HeadUID));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_M4),"Head","+1.5"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P0),"Head","+5  "));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P4),"Head","+8.5"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P8),"Head","+12 "));

  prodList.push_back(headRange);

  auto cutPlaneRange= new SboTPCPartCutPlane(productName());
  cutPlaneRange->setDefaultLabel(s3(S3UID::CUTPLANE));
  cutPlaneRange->push_back(new SboTPCatalogItem(cutPlaneRange,s3(S3UID::CUTPLANE),"Cutplane"));

  prodList.push_back(cutPlaneRange);

}


bool SboActis::inRange(SboShape3Label aL)
{
  using namespace XXXStem;
  return SboML::in_closed_range<SboShape3Label>(aL,s3(lowerS3UID),s3(upperS3UID));
}

SboMatrix3 SboActis::headToNeckMatrix(SboShape3Label aHeadLabel, SboShape3Label aNeckLabel)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aHeadLabel);
  HPROJ_UNUSED(aNeckLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboActis::neckToStemMatrix(SboShape3Label aNeckLabel, SboShape3Label aStemLabel, SboAnatomLocation aSide)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aNeckLabel);
  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboActis::headToStemMatrix(SboShape3Label aHeadLabel, SboShape3Label aStemLabel)
{
  //NOTE: Requested for mono-block stem

  //NOTE: CS & scenegraph programming [[hdoch:capture-hproj-dev.org::EZCS]]

  //The HEAD point item has a default position at (0,0,0)
  //The HEAD point in CPT_FRAME is specified by the manufacturer

  //return the traffo that maps (0,0,0) to HEAD (including offset) in CPT_FRAME

  //Reference is diameter 36 (NB: 32 is the most common !?)
  HPROJ_UNUSED(aHeadLabel);
  using namespace XXXStem;

  const auto neckO=getRES_01(aStemLabel);
  const auto headO=getTPR_01(aStemLabel);
  const auto neckAxis = SboML::unit3(headO - neckO);

  float l=0;//SboML::norm3(headO-neckO);

  if(aHeadLabel == s3(S3UID::HEAD_M4))      l-=3.5f;
  else if(aHeadLabel == s3(S3UID::HEAD_P0)) l+=0.f;
  else if(aHeadLabel == s3(S3UID::HEAD_P4)) l+=3.5f;
  else if(aHeadLabel == s3(S3UID::HEAD_P8)) l+=7.0f;

  auto m=SboML::transMat3(headO + neckAxis * l);

  return m;
}


SboPlane3 SboActis::cutPlane(SboShape3Label aStemLabel)
{
  //return the cutplane equation in CPT_FRAME

  //The cutplane is used to position the component in WORD_CS (STD_FRAME)

  //Default plane position and orientation: centered at (0,0,0) with normal (0,1,0)
  //Should return something like Plane3(Point3(0,0,0),Vector3(0,1,0)).transform(m)
  //Compute the TRAFFFO m

  //FIXME: Plane3 origin is supposed to be the neck origin

  using namespace XXXStem;
  const auto neckO=getRES_01(aStemLabel);

  //NOTE: Y_FRAME
  // auto rz=SboML::rotMatZ3(SboML::deg2Rad<float>(-42.0f));
  // auto t=SboML::transMat3(neckO);
  // auto m=t*rz;

  //NOTE: Z_FRAME is the normal frame
  auto rx=SboML::rotMatX3(SboML::deg2Rad<float>(90.0f));
  auto ry=SboML::rotMatY3(SboML::deg2Rad<float>(40.0f));
  auto t=SboML::transMat3(neckO);
  auto m=t*ry*rx;

  return SboPlane3(SboPoint3(0,0,0), SboVector3(0,1,0)).transform(m);

}

SboBbox3 SboActis::cutPlaneBbox(SboShape3Label aStemLabel)
{
  //return a bbox in CPT_FRAME that intersects the cutplane

  //NOTE: if the intersection is empty, the trace of the plane is not
  //visible.

  //Consider a bbox of dimensions (50,50,50) centered at (0,0,0)
  //Strategy the bbox center must be translated to the neck origin


  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;

  SboPoint3 pmin(-50.0f,-25.0f,-25.0f);
  SboPoint3 pmax(50.0f,25.0f,25.0f);

  const auto neckO=getRES_01(aStemLabel);
  auto m=SboML::transMat3(neckO);

  pmin=m(pmin);
  pmax=m(pmax);

  return SboML::makeBbox3(pmin,pmax);
}

SboMatrix3 SboActis::stemToStemMatrix(const SboFemImplantConfig& aOriginFemIC,const SboFemImplantConfig& aTargetFemIC)
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

SboMatrix3 SboActis::normalTrf(SboShape3Label aStemLabel, const SboPlane3 & aP3, const SboPoint3 & aO3)
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

  //from Z_FRAME is NORMAL_FRAME
  return SboML::idMat3();

  //from Y_FRAME to NORMAL_FRAME
  // return SboML::rotMatX3(SboML::deg2Rad<float>(90.0f));
}

SboVector3 SboActis::offsetFF(SboShape3Label aStemLabel)
{

  // independently of the side (left or right)
  // x > 0 cpt moves medially
  // y > 0 cpt moves posteriorly
  // z > 0 cpt moves superiorly

  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;

  return {15.f,0.f,5.f};
}


SboFemImplantConfig SboActis::defaultFemIC(QString aPartName,SboAnatomLocation aRequestedSide)
{
  using namespace XXXStem;

  //NOTE: straight stem
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

SboFemImplantConfig SboActis::fillAndValidAssembly(const SboFemImplantConfig& aFemIC)
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
      myFemIC.setImplantSide(myFemIC.requestedSide()); //NOTE: consider SboAnatomLocation::None for straight stem
      myFemIC.setValidAssembly(true);
    }
  }

  return myFemIC;


}

SboFemImplantConfig SboActis::nextPrev(const SboFemImplantConfig& aFemIC,bool aNext)
{
  using namespace XXXStem;

  auto fc=aFemIC;
  fc.setStemLabel(nextPrevStem(fc.stemLabel(),aNext));

  //NOTE: Don't check whether the config is a valid assembly or combination, let the application do it

  return fc;
}

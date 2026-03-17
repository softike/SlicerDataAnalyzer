/*=========================================================================
  HPROJECT
  Copyright (c) Ernesto Durante, Julien de Siebenthal
  All rights reserved.
  See Copyrights.txt for details
  =========================================================================*/

#include "SboFitmore.h"

#include "SboTPCatalogElement.h"
#include "SboTPCatalogList.h"
#include "SboMathLibBase.h"
#include "SboPluginDefs.h"

#include <QDir>
#include <QIcon>

#define ICONSET_STR(s) QIcon(":/TPCatalogIcons/" s)

namespace XXXStem {
  constexpr auto ProductRangeStartsAt = hproj::ZB::productRangeStartsAt(hproj::ZB::Product::FITMORE);

  constexpr auto CompanyName = hproj::ZB::companyName;
  constexpr auto ProductName = hproj::ZB::productName(hproj::ZB::Product::FITMORE);

  constexpr auto RCCIdName   = hproj::ZB::RCCIdName(hproj::ZB::Product::FITMORE);
  constexpr auto RCCFileName = hproj::ZB::RCCFileName(hproj::ZB::Product::FITMORE);
  constexpr auto RCCPath     = hproj::ZB::RCCPath(hproj::ZB::Product::FITMORE);

  const QIcon   PartIcon=ICONSET_STR("generic_stem.png");
  const QString PartMenuText("");
  const QString PartTooltipText("");
  const QString ItemName=hproj::ZB::itemName(hproj::ZB::Product::FITMORE);

  const QIcon   PartHeadIcon=ICONSET_STR("spcl_head.png");
  const QString PartHeadMenuText("");
  const QString PartHeadTooltipText("");

  enum class S3UID: SboShape3UID{
    STEM_A_0 = ProductRangeStartsAt + 90L,
    STEM_A_1,
    STEM_A_2,
    STEM_A_3,
    STEM_A_4,
    STEM_A_5,
    STEM_A_6,
    STEM_A_7,
    STEM_A_8,
    STEM_A_9,
    STEM_A_10,
    STEM_A_11,
    STEM_A_12,
    STEM_A_13,

    STEM_B_0,
    STEM_B_1,
    STEM_B_2,
    STEM_B_3,
    STEM_B_4,
    STEM_B_5,
    STEM_B_6,
    STEM_B_7,
    STEM_B_8,
    STEM_B_9,
    STEM_B_10,
    STEM_B_11,
    STEM_B_12,
    STEM_B_13,

    STEM_BEX_0,
    STEM_BEX_1,
    STEM_BEX_2,
    STEM_BEX_3,
    STEM_BEX_4,
    STEM_BEX_5,
    STEM_BEX_6,
    STEM_BEX_7,
    STEM_BEX_8,
    STEM_BEX_9,
    STEM_BEX_10,
    STEM_BEX_11,
    STEM_BEX_12,
    STEM_BEX_13,

    STEM_C_0,
    STEM_C_1,
    STEM_C_2,
    STEM_C_3,
    STEM_C_4,
    STEM_C_5,
    STEM_C_6,
    STEM_C_7,
    STEM_C_8,
    STEM_C_9,
    STEM_C_10,
    STEM_C_11,
    STEM_C_12,
    STEM_C_13,

    CUTPLANE,
    HEAD_M4,
    HEAD_P0,
    HEAD_P4,
    HEAD_P8,
    HEAD_P10,
    RANGE_CCD_A,
    RANGE_CCD_B,
    RANGE_CCD_BEX,
    RANGE_CCD_C
  };

  const S3UID lowerS3UID=S3UID::STEM_A_0;
  const S3UID upperS3UID=S3UID::RANGE_CCD_C;

  const S3UID defaultS3StemUID=S3UID::STEM_B_7;
  const S3UID defaultS3HeadUID=S3UID::HEAD_P0;

  // PLANE_ORIGIN
  const float cRes01_A[14][3]={
    {16.053f, 0, 19.132f},
    {16.553f, 0, 19.728f},
    {17.053f, 0, 20.323f},
    {17.553f, 0, 20.919f},
    {18.053f, 0, 21.515f},
    {18.678f, 0, 22.260f},
    {19.303f, 0, 23.005f},
    {19.928f, 0, 23.750f},
    {20.553f, 0, 24.495f},
    {21.303f, 0, 25.388f},
    {22.053f, 0, 26.282f},
    {22.803f, 0, 27.176f},
    {23.553f, 0, 28.070f},
    {24.303f, 0, 28.964f}};

  // HEAD_ROTATION_POINT_0
  const float cTpr01_A[14][3]={
    {31.000f, 0, 36.944f},
    {31.500f, 0, 37.540f},
    {32.000f, 0, 38.136f},
    {32.500f, 0, 38.732f},
    {33.000f, 0, 39.328f},
    {33.625f, 0, 40.073f},
    {34.250f, 0, 40.818f},
    {34.875f, 0, 41.562f},
    {35.500f, 0, 42.307f},
    {36.250f, 0, 43.201f},
    {37.000f, 0, 44.095f},
    {37.750f, 0, 44.989f},
    {38.500f, 0, 45.883f},
    {39.250f, 0, 46.776f}};

  // STEM_DISTAL_END_POINT
  const float cDistalEndPt_A[14][3]={
    {1.759f, 0.575f, -61.056f},
    {1.939f, 0.571f, -63.460f},
    {2.129f, 0.566f, -65.864f},
    {2.330f, 0.480f, -68.268f},
    {2.542f, 0.475f, -70.672f},
    {2.749f, 0.470f, -72.927f},
    {2.967f, 0.466f, -75.182f},
    {3.195f, 0.461f, -77.438f},
    {3.434f, 0.457f, -79.693f},
    {3.667f, 0.453f, -81.799f},
    {3.909f, 0.449f, -83.905f},
    {4.161f, 0.445f, -86.011f},
    {4.425f, 0.441f, -88.117f},
    {4.699f, 0.437f, -90.224f}};

  // B
  const float cRes01_B[14][3]={
    {18.297f, 0.000f, 19.621f},
    {18.797f, 0.000f, 20.157f},
    {19.297f, 0.000f, 20.694f},
    {19.797f, 0.000f, 21.230f},
    {20.297f, 0.000f, 21.766f},
    {20.922f, 0.000f, 22.436f},
    {21.547f, 0.000f, 23.106f},
    {22.172f, 0.000f, 23.777f},
    {22.797f, 0.000f, 24.447f},
    {23.547f, 0.000f, 25.251f},
    {24.297f, 0.000f, 26.055f},
    {25.047f, 0.000f, 26.860f},
    {25.797f, 0.000f, 27.664f},
    {26.547f, 0.000f, 28.468f}};

  const float cTpr01_B[14][3]={
    {37.000f, 0.000f, 39.678f},
    {37.500f, 0.000f, 40.214f},
    {38.000f, 0.000f, 40.750f},
    {38.500f, 0.000f, 41.286f},
    {39.000f, 0.000f, 41.822f},
    {39.625f, 0.000f, 42.493f},
    {40.250f, 0.000f, 43.163f},
    {40.875f, 0.000f, 43.833f},
    {41.500f, 0.000f, 44.503f},
    {42.250f, 0.000f, 45.308f},
    {43.000f, 0.000f, 46.112f},
    {43.750f, 0.000f, 46.916f},
    {44.500f, 0.000f, 47.720f},
    {45.250f, 0.000f, 48.525f}};

  const float cDistalEndPt_B[14][3]={
    {1.759f, 0.714f, -64.322f },
    {1.939f, 0.710f, -66.786f },
    {2.129f, -0.706f, -69.250f},
    {2.330f, 0.480f, -71.714f },
    {2.542f, -0.475f, -74.178f},
    {2.749f, 0.470f, -76.507f },
    {2.967f, 0.466f, -78.837f },
    {3.195f, 0.461f, -81.167f },
    {3.434f, 0.457f, -83.497f },
    {3.667f, -0.453f, -85.692f},
    {3.909f, 0.449f, -87.888f },
    {4.161f, 0.445f, -90.084f },
    {4.425f, 0.441f, -92.280f },
    {4.699f, 0.437f, -94.475f }};

  //BEX
  const float cRes01_BEX[14][3]={
    {18.716f, 0.000f, 15.156f},
    {19.216f, 0.000f, 15.560f},
    {19.716f, 0.000f, 15.965f},
    {20.216f, 0.000f, 16.370f},
    {20.716f, 0.000f, 16.775f},
    {21.341f, 0.000f, 17.281f},
    {21.966f, 0.000f, 17.787f},
    {22.591f, 0.000f, 18.293f},
    {23.216f, 0.000f, 18.800f},
    {23.966f, 0.000f, 19.407f},
    {24.716f, 0.000f, 20.014f},
    {25.466f, 0.000f, 20.622f},
    {26.216f, 0.000f, 21.229f},
    {26.966f, 0.000f, 21.836f}};

  const float cTpr01_BEX[14][3]={
    {44.000f, 0.000f, 35.630f},
    {44.500f, 0.000f, 36.035f},
    {45.000f, 0.000f, 36.440f},
    {45.500f, 0.000f, 36.845f},
    {46.000f, 0.000f, 37.250f},
    {46.625f, 0.000f, 37.756f},
    {47.250f, 0.000f, 38.262f},
    {47.875f, 0.000f, 38.768f},
    {48.500f, 0.000f, 39.275f},
    {49.250f, 0.000f, 39.882f},
    {50.000f, 0.000f, 40.489f},
    {50.750f, 0.000f, 41.097f},
    {51.500f, 0.000f, 41.704f},
    {52.250f, 0.000f, 42.311f}};

  const float cDistalEndPt_BEX[14][3]={
    {1.759f, 0.714f, -68.370f},
    {1.939f, 0.710f, -70.965f},
    {2.129f, 0.706f, -73.560f},
    {2.330f, 0.480f, -76.155f},
    {2.542f, 0.475f, -78.750f},
    {2.749f, 0.470f, -81.244f},
    {2.967f, 0.466f, -83.738f},
    {3.195f, 0.461f, -86.232f},
    {3.434f, 0.457f, -88.725f},
    {3.667f, 0.453f, -91.118f},
    {3.909f, -0.449f, -93.511f},
    {4.161f, 0.445f, -95.903f},
    {4.425f, 0.441f, -98.296f},
    {4.699f, 0.437f, -100.689f}};

  //C
  const float cRes01_C[14][3]={
    {20.913f, 0.000f, 15.759f},
    {21.413f, 0.000f, 16.136f},
    {21.913f, 0.000f, 16.513f},
    {22.413f, 0.000f, 16.889f},
    {22.913f, 0.000f, 17.266f},
    {23.538f, 0.000f, 17.737f},
    {24.163f, 0.000f, 18.208f},
    {24.788f, 0.000f, 18.679f},
    {25.413f, 0.000f, 19.150f},
    {26.163f, 0.000f, 19.715f},
    {26.913f, 0.000f, 20.280f},
    {27.663f, 0.000f, 20.845f},
    {28.413f, 0.000f, 21.411f},
    {29.163f, 0.000f, 21.976f}};

  const float cTpr01_C[14][3]={
    {51.000f, 0.000f, 38.431f},
    {51.500f, 0.000f, 38.808f},
    {52.000f, 0.000f, 39.185f},
    {52.500f, 0.000f, 39.562f},
    {53.000f, 0.000f, 39.938f},
    {53.625f, 0.000f, 40.409f},
    {54.250f, 0.000f, 40.880f},
    {54.875f, 0.000f, 41.351f},
    {55.500f, 0.000f, 41.822f},
    {56.250f, 0.000f, 42.387f},
    {57.000f, 0.000f, 42.953f},
    {57.750f, 0.000f, 43.518f},
    {58.500f, 0.000f, 44.083f},
    {59.250f, 0.000f, 44.648f}};

  const float cDistalEndPt_C[14][3]={
    {1.759f, 0.853f, -71.569f},
    {1.939f, 0.849f, -74.192f},
    {2.129f, 0.845f, -76.815f},
    {2.330f, 0.480f, -79.438f},
    {2.542f, 0.475f, -82.062f},
    {2.749f, 0.470f, -84.591f},
    {2.967f, -0.466f, -87.120f},
    {3.195f, 0.461f, -89.649f},
    {3.434f, 0.457f, -92.178f},
    {3.667f, 0.453f, -94.613f},
    {3.909f, 0.449f, -97.047f},
    {4.161f, 0.445f, -99.482f},
    {4.425f, 0.441f, -101.917f},
    {4.699f, 0.437f, -104.352f}};


  SboShape3Label s3( S3UID e) { return SboShape3Label(SboShape3Label::utype(e));}

  bool isCCD_A(SboShape3Label l) {
    //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_A_0),s3(S3UID::STEM_A_13));
  }

  bool isCCD_B(SboShape3Label l) {
    //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_B_0),s3(S3UID::STEM_B_13));
  }

  bool isCCD_BEX(SboShape3Label l) {
    //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_BEX_0),s3(S3UID::STEM_BEX_13));
  }

  bool isCCD_C(SboShape3Label l) {
    //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_C_0),s3(S3UID::STEM_C_13));
  }

  bool isStem(SboShape3Label l) {
    return isCCD_A(l) || isCCD_B(l) || isCCD_BEX(l) || isCCD_C(l);
  }

  bool isHead(SboShape3Label l){
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::HEAD_M4),s3(S3UID::HEAD_P10));
  }

  bool isSubRange(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::RANGE_CCD_A),s3(S3UID::RANGE_CCD_C));
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
      if(isCCD_A(aL))   myRL=s3(S3UID::RANGE_CCD_A);
      if(isCCD_B(aL))   myRL=s3(S3UID::RANGE_CCD_B);
      if(isCCD_BEX(aL)) myRL=s3(S3UID::RANGE_CCD_BEX);
      if(isCCD_C(aL))   myRL=s3(S3UID::RANGE_CCD_C);

    }


    if(isSubRange(myRL)){
      if(myRL==s3(S3UID::RANGE_CCD_A))   return R{0,13, s3(S3UID::STEM_A_0),myRL};
      if(myRL==s3(S3UID::RANGE_CCD_B))   return R{0,13, s3(S3UID::STEM_B_0),myRL};
      if(myRL==s3(S3UID::RANGE_CCD_BEX)) return R{0,13, s3(S3UID::STEM_BEX_0),myRL};
      if(myRL==s3(S3UID::RANGE_CCD_C))   return R{0,13, s3(S3UID::STEM_C_0),myRL};
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

    float x=0.f,y=0.f,z=0.f;

    if(sourceR == s3(S3UID::RANGE_CCD_A)){

      x=cRes01_A[sz][0];
      y=cRes01_A[sz][1];
      z=cRes01_A[sz][2];
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_B)){

      x=cRes01_B[sz][0];
      y=cRes01_B[sz][1];
      z=cRes01_B[sz][2];

    }
    else if(sourceR == s3(S3UID::RANGE_CCD_BEX)){

      x=cRes01_BEX[sz][0];
      y=cRes01_BEX[sz][1];
      z=cRes01_BEX[sz][2];

    }
    else if(sourceR == s3(S3UID::RANGE_CCD_C)){

      x=cRes01_C[sz][0];
      y=cRes01_C[sz][1];
      z=cRes01_C[sz][2];

    }

    return SboPoint3{x,y,z};
  }

  SboPoint3 getRES_02(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto S=getRangeStats(aLabel);
    const auto sourceR=S.subRange;
    const auto sz=S.size(aLabel);

    float x=0.f,y=0.f,z=0.f;
    if(sourceR == s3(S3UID::RANGE_CCD_A)){
      x=cRes01_A[sz][0]+6.55f;
      y=cRes01_A[sz][1];
      z=cRes01_A[sz][2]-6.55f;
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_B)){
      x=cRes01_B[sz][0]+6.9;
      y=cRes01_B[sz][1];
      z=cRes01_B[sz][2]-6.9;
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_BEX)){

      x=cRes01_BEX[sz][0]+6.5f;
      y=cRes01_BEX[sz][1];
      z=cRes01_BEX[sz][2]-6.5f;

    }
    else if(sourceR == s3(S3UID::RANGE_CCD_C)){

      x=cRes01_C[sz][0]+6.95f;
      y=cRes01_C[sz][1];
      z=cRes01_C[sz][2]-6.95f;

    }

    return SboPoint3{x,y,z};
  }

  SboPoint3 getTPR_01(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto S=getRangeStats(aLabel);
    const auto sourceR=S.subRange;
    const auto sz=S.size(aLabel);

    float x=0.f,y=0.f,z=0.f;

    if(sourceR == s3(S3UID::RANGE_CCD_A)){

      x=cTpr01_A[sz][0];
      y=cTpr01_A[sz][1];
      z=cTpr01_A[sz][2];
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_B)){

      x=cTpr01_B[sz][0];
      y=cTpr01_B[sz][1];
      z=cTpr01_B[sz][2];

    }
    else if(sourceR == s3(S3UID::RANGE_CCD_BEX)){

      x=cTpr01_BEX[sz][0];
      y=cTpr01_BEX[sz][1];
      z=cTpr01_BEX[sz][2];

    }
    else if(sourceR == s3(S3UID::RANGE_CCD_C)){

      x=cTpr01_C[sz][0];
      y=cTpr01_C[sz][1];
      z=cTpr01_C[sz][2];

    }

    return SboPoint3{x,y,z};
  }



}

int SboFitmore::rev() const
{
  return 1;
}

QString SboFitmore::productName() const
{
  return XXXStem::ProductName;
}

QString SboFitmore::companyName() const
{
  return XXXStem::CompanyName;
}

QString SboFitmore::message(int,const SboFemImplantConfig&) const
{
  return "Insert a meaningful message";
}

QString SboFitmore::setMeshInfoSearchPath(QString aPath)
{
  using namespace XXXStem;

  //http://doc.qt.io/qt-5/qdir.html#setSearchPaths
  //Load resource from the system file
  QString myRcc;
  if(meshInfoResourceFromRcc(myRcc))
    QDir::setSearchPaths(RCCIdName, QStringList(QString(":") + RCCPath));
  else {
    QStringList myList{aPath + RCCPath + "/A",
                       aPath + RCCPath + "/B",
                       aPath + RCCPath + "/BEX",
                       aPath + RCCPath + "/C" };

    HPROJ_DCHECK2(QDir(myList[0]).exists(),"dir doesn't exist");

    QDir::setSearchPaths(RCCIdName, myList);
  }

  return {};
}

bool SboFitmore::meshInfoResourceFromRcc(QString& aRcc)
{
  aRcc=XXXStem::RCCFileName;
  return false;
}

bool SboFitmore::meshInfoResourceFromFileSystem()
{
  return true;
}


void SboFitmore::meshInfoRCList(SboMeshInfoRCList& rcList)
{
  using namespace XXXStem;
  auto next=[&](S3UID e,QString s,QString aRCCId) { rcList.push_back({s3(e),aRCCId + QString(":") + s + ".wrl"});};

  next(S3UID::STEM_A_0,  "063.287.411_C_M01_R00",RCCIdName);
  next(S3UID::STEM_A_1,  "063.287.411_C_M02_R00",RCCIdName);
  next(S3UID::STEM_A_2,  "063.287.411_C_M03_R00",RCCIdName);
  next(S3UID::STEM_A_3,  "063.287.411_C_M04_R00",RCCIdName);
  next(S3UID::STEM_A_4,  "063.287.411_C_M05_R00",RCCIdName);
  next(S3UID::STEM_A_5,  "063.287.411_C_M06_R00",RCCIdName);
  next(S3UID::STEM_A_6,  "063.287.411_C_M07_R00",RCCIdName);
  next(S3UID::STEM_A_7,  "063.287.411_C_M08_R00",RCCIdName);
  next(S3UID::STEM_A_8,  "063.287.411_C_M09_R00",RCCIdName);
  next(S3UID::STEM_A_9,  "063.287.411_C_M10_R00",RCCIdName);
  next(S3UID::STEM_A_10, "063.287.411_C_M11_R00",RCCIdName);
  next(S3UID::STEM_A_11, "063.287.411_C_M12_R00",RCCIdName);
  next(S3UID::STEM_A_12, "063.287.411_C_M13_R00",RCCIdName);
  next(S3UID::STEM_A_13, "063.287.411_C_M14_R00",RCCIdName);

  next(S3UID::STEM_B_0,  "063.287.411_C_M15_R00",RCCIdName);
  next(S3UID::STEM_B_1,  "063.287.411_C_M16_R00",RCCIdName);
  next(S3UID::STEM_B_2,  "063.287.411_C_M17_R00",RCCIdName);
  next(S3UID::STEM_B_3,  "063.287.411_C_M18_R00",RCCIdName);
  next(S3UID::STEM_B_4,  "063.287.411_C_M19_R00",RCCIdName);
  next(S3UID::STEM_B_5,  "063.287.411_C_M20_R00",RCCIdName);
  next(S3UID::STEM_B_6,  "063.287.411_C_M21_R00",RCCIdName);
  next(S3UID::STEM_B_7,  "063.287.411_C_M22_R00",RCCIdName);
  next(S3UID::STEM_B_8,  "063.287.411_C_M23_R00",RCCIdName);
  next(S3UID::STEM_B_9,  "063.287.411_C_M24_R00",RCCIdName);
  next(S3UID::STEM_B_10, "063.287.411_C_M25_R00",RCCIdName);
  next(S3UID::STEM_B_11, "063.287.411_C_M26_R00",RCCIdName);
  next(S3UID::STEM_B_12, "063.287.411_C_M27_R00",RCCIdName);
  next(S3UID::STEM_B_13, "063.287.411_C_M28_R00",RCCIdName);

  next(S3UID::STEM_BEX_0,  "063.287.411_C_M29_R00",RCCIdName);
  next(S3UID::STEM_BEX_1,  "063.287.411_C_M30_R00",RCCIdName);
  next(S3UID::STEM_BEX_2,  "063.287.411_C_M31_R00",RCCIdName);
  next(S3UID::STEM_BEX_3,  "063.287.411_C_M32_R00",RCCIdName);
  next(S3UID::STEM_BEX_4,  "063.287.411_C_M33_R00",RCCIdName);
  next(S3UID::STEM_BEX_5,  "063.287.411_C_M34_R00",RCCIdName);
  next(S3UID::STEM_BEX_6,  "063.287.411_C_M35_R00",RCCIdName);
  next(S3UID::STEM_BEX_7,  "063.287.411_C_M36_R00",RCCIdName);
  next(S3UID::STEM_BEX_8,  "063.287.411_C_M37_R00",RCCIdName);
  next(S3UID::STEM_BEX_9,  "063.287.411_C_M38_R00",RCCIdName);
  next(S3UID::STEM_BEX_10, "063.287.411_C_M39_R00",RCCIdName);
  next(S3UID::STEM_BEX_11, "063.287.411_C_M40_R00",RCCIdName);
  next(S3UID::STEM_BEX_12, "063.287.411_C_M41_R00",RCCIdName);
  next(S3UID::STEM_BEX_13, "063.287.411_C_M42_R00",RCCIdName);

  next(S3UID::STEM_C_0,  "063.287.411_C_M43_R00",RCCIdName);
  next(S3UID::STEM_C_1,  "063.287.411_C_M44_R00",RCCIdName);
  next(S3UID::STEM_C_2,  "063.287.411_C_M45_R00",RCCIdName);
  next(S3UID::STEM_C_3,  "063.287.411_C_M46_R00",RCCIdName);
  next(S3UID::STEM_C_4,  "063.287.411_C_M47_R00",RCCIdName);
  next(S3UID::STEM_C_5,  "063.287.411_C_M48_R00",RCCIdName);
  next(S3UID::STEM_C_6,  "063.287.411_C_M49_R00",RCCIdName);
  next(S3UID::STEM_C_7,  "063.287.411_C_M50_R00",RCCIdName);
  next(S3UID::STEM_C_8,  "063.287.411_C_M51_R00",RCCIdName);
  next(S3UID::STEM_C_9,  "063.287.411_C_M52_R00",RCCIdName);
  next(S3UID::STEM_C_10, "063.287.411_C_M53_R00",RCCIdName);
  next(S3UID::STEM_C_11, "063.287.411_C_M54_R00",RCCIdName);
  next(S3UID::STEM_C_12, "063.287.411_C_M55_R00",RCCIdName);
  next(S3UID::STEM_C_13, "063.287.411_C_M56_R00",RCCIdName);

}


void SboFitmore::parts(SboTPCatalogList& prodList)
{
  using namespace XXXStem;

  auto stemRange= new SboTPCPartMonoStem(productName(),SboAnatomLocation::None);
  stemRange->_iconSet=PartIcon;
  stemRange->_menuText=PartMenuText;
  stemRange->_tooltipText=PartTooltipText;
  stemRange->setDefaultLabel(s3(defaultS3StemUID));


  struct CCD_SUPER : public SboTPCPartMonoStem::CCD {

    RT range(SboShape3Label l) const override {
      if(isCCD_A(l)) return _rA;
      if(isCCD_B(l)) return _rB;
      if(isCCD_BEX(l)) return _rBEX;
      if(isCCD_C(l)) return _rC;
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


    std::vector<RT> ranges() const override { return {_rA,_rB,_rBEX,_rC}; }

    const RT _rA  ={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_A),  "A"};
    const RT _rB  ={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_B),  "B"};
    const RT _rBEX={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_BEX),"BEX"};
    const RT _rC  ={-1, -1, s3(XXXStem::S3UID::RANGE_CCD_C),  "C"};

  };

  stemRange->_CCDPart = std::make_unique<CCD_SUPER>();


  auto next=[&](S3UID e,QString s) { stemRange->push_back(new SboTPCatalogItem(stemRange,s3(e), ItemName,s));};

  next(S3UID::STEM_A_0,  "A1");
  next(S3UID::STEM_A_1,  "A2");
  next(S3UID::STEM_A_2,  "A3");
  next(S3UID::STEM_A_3,  "A4");
  next(S3UID::STEM_A_4,  "A5");
  next(S3UID::STEM_A_5,  "A6");
  next(S3UID::STEM_A_6,  "A7");
  next(S3UID::STEM_A_7,  "A8");
  next(S3UID::STEM_A_8,  "A9");
  next(S3UID::STEM_A_9,  "A10");
  next(S3UID::STEM_A_10, "A11");
  next(S3UID::STEM_A_11, "A12");
  next(S3UID::STEM_A_12, "A13");
  next(S3UID::STEM_A_13, "A14");

  next(S3UID::STEM_B_0,  "B1");
  next(S3UID::STEM_B_1,  "B2");
  next(S3UID::STEM_B_2,  "B3");
  next(S3UID::STEM_B_3,  "B4");
  next(S3UID::STEM_B_4,  "B5");
  next(S3UID::STEM_B_5,  "B6");
  next(S3UID::STEM_B_6,  "B7");
  next(S3UID::STEM_B_7,  "B8");
  next(S3UID::STEM_B_8,  "B9");
  next(S3UID::STEM_B_9,  "B10");
  next(S3UID::STEM_B_10, "B11");
  next(S3UID::STEM_B_11, "B12");
  next(S3UID::STEM_B_12, "B13");
  next(S3UID::STEM_B_13, "B14");

  next(S3UID::STEM_BEX_0,  "Bext1");
  next(S3UID::STEM_BEX_1,  "Bext2");
  next(S3UID::STEM_BEX_2,  "Bext3");
  next(S3UID::STEM_BEX_3,  "Bext4");
  next(S3UID::STEM_BEX_4,  "Bext5");
  next(S3UID::STEM_BEX_5,  "Bext6");
  next(S3UID::STEM_BEX_6,  "Bext7");
  next(S3UID::STEM_BEX_7,  "Bext8");
  next(S3UID::STEM_BEX_8,  "Bext9");
  next(S3UID::STEM_BEX_9,  "Bext10");
  next(S3UID::STEM_BEX_10, "Bext11");
  next(S3UID::STEM_BEX_11, "Bext12");
  next(S3UID::STEM_BEX_12, "Bext13");
  next(S3UID::STEM_BEX_13, "Bext14");

  next(S3UID::STEM_C_0,  "C1");
  next(S3UID::STEM_C_1,  "C2");
  next(S3UID::STEM_C_2,  "C3");
  next(S3UID::STEM_C_3,  "C4");
  next(S3UID::STEM_C_4,  "C5");
  next(S3UID::STEM_C_5,  "C6");
  next(S3UID::STEM_C_6,  "C7");
  next(S3UID::STEM_C_7,  "C8");
  next(S3UID::STEM_C_8,  "C9");
  next(S3UID::STEM_C_9,  "C10");
  next(S3UID::STEM_C_10, "C11");
  next(S3UID::STEM_C_11, "C12");
  next(S3UID::STEM_C_12, "C13");
  next(S3UID::STEM_C_13, "C14");

  prodList.push_back(stemRange);


  //NOTE: Last argument S3UID::HEAD_P4 locates the CONE Lateral tip.
  //NOTE: The default label must be different from HEAD_P4 to be able to compute the cone axis.
  auto headRange= new SboTPCPartHead(productName(),s3(S3UID::HEAD_P4));
  headRange->_iconSet=PartHeadIcon;
  headRange->_menuText=PartHeadMenuText;
  headRange->_tooltipText=PartHeadTooltipText;
  headRange->setDefaultLabel(s3(defaultS3HeadUID));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_M4),"Head","-3.5"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P0),"Head","0"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P4),"Head","+3.5"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P8),"Head","+7"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P10),"Head","+10.5"));

  prodList.push_back(headRange);

  auto cutPlaneRange= new SboTPCPartCutPlane(productName());
  cutPlaneRange->setDefaultLabel(s3(S3UID::CUTPLANE));
  cutPlaneRange->push_back(new SboTPCatalogItem(cutPlaneRange,s3(S3UID::CUTPLANE),"Cutplane"));

  prodList.push_back(cutPlaneRange);

}


bool SboFitmore::inRange(SboShape3Label aL)
{
  using namespace XXXStem;
  return SboML::in_closed_range<SboShape3Label>(aL,s3(lowerS3UID),s3(upperS3UID));
}

SboMatrix3 SboFitmore::headToNeckMatrix(SboShape3Label aHeadLabel, SboShape3Label aNeckLabel)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aHeadLabel);
  HPROJ_UNUSED(aNeckLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboFitmore::neckToStemMatrix(SboShape3Label aNeckLabel, SboShape3Label aStemLabel, SboAnatomLocation aSide)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aNeckLabel);
  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboFitmore::headToStemMatrix(SboShape3Label aHeadLabel, SboShape3Label aStemLabel)
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
  else if(aHeadLabel == s3(S3UID::HEAD_P0)) l=0;
  else if(aHeadLabel == s3(S3UID::HEAD_P4)) l=3.5f;
  else if(aHeadLabel == s3(S3UID::HEAD_P8)) l=7;
  else if(aHeadLabel == s3(S3UID::HEAD_P10)) l=10.5;

  auto m=SboML::transMat3(headO + neckAxis * l);

  return m;
}


SboPlane3 SboFitmore::cutPlane(SboShape3Label aStemLabel)
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
  auto ry=SboML::rotMatY3(SboML::deg2Rad<float>(45.0f));
  auto t=SboML::transMat3(neckO);
  auto m=t*ry*rx;

  return SboPlane3(SboPoint3(0,0,0), SboVector3(0,1,0)).transform(m);

}

SboBbox3 SboFitmore::cutPlaneBbox(SboShape3Label aStemLabel)
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

SboMatrix3 SboFitmore::stemToStemMatrix(const SboFemImplantConfig& aOriginFemIC,const SboFemImplantConfig& aTargetFemIC)
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

SboMatrix3 SboFitmore::normalTrf(SboShape3Label aStemLabel, const SboPlane3 & aP3, const SboPoint3 & aO3)
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

SboVector3 SboFitmore::offsetFF(SboShape3Label aStemLabel)
{
  //NOTE: getRES_01(aStemLabel) is located at FF origin

  // Z_FRAME independently of the side (left or right)
  // x > 0 cpt moves medially
  // y > 0 cpt moves posteriorly
  // z > 0 cpt moves superiorly

  using namespace XXXStem;

  const auto S=getRangeStats(aStemLabel);
  const auto sourceR=S.subRange;
  const auto sz=S.size(aStemLabel);

  float x=0,y=0,z=0;
  if(sourceR == s3(S3UID::RANGE_CCD_A)){
    x=cDistalEndPt_A[sz][0];
    y=cDistalEndPt_A[sz][1];
    z=cDistalEndPt_A[sz][2];
  }
  else if(sourceR == s3(S3UID::RANGE_CCD_B)){
    x=cDistalEndPt_B[sz][0];
    y=cDistalEndPt_B[sz][1];
    z=cDistalEndPt_B[sz][2];
  }
  else if(sourceR == s3(S3UID::RANGE_CCD_BEX)){
    x=cDistalEndPt_BEX[sz][0];
    y=cDistalEndPt_BEX[sz][1];
    z=cDistalEndPt_BEX[sz][2];
  }
  else if(sourceR == s3(S3UID::RANGE_CCD_C)){
    x=cDistalEndPt_C[sz][0];
    y=cDistalEndPt_C[sz][1];
    z=cDistalEndPt_C[sz][2];
  }

  auto p1=getRES_01(aStemLabel);
  //align with the femoral axis
  return {p1[0]-x,0,15};
}


SboFemImplantConfig SboFitmore::defaultFemIC(QString aPartName,SboAnatomLocation aRequestedSide)
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

SboFemImplantConfig SboFitmore::fillAndValidAssembly(const SboFemImplantConfig& aFemIC)
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

SboFemImplantConfig SboFitmore::nextPrev(const SboFemImplantConfig& aFemIC,bool aNext)
{
  using namespace XXXStem;

  auto fc=aFemIC;
  fc.setStemLabel(nextPrevStem(fc.stemLabel(),aNext));

  //NOTE: Don't check whether the config is a valid assembly or combination, let the application do it

  return fc;
}

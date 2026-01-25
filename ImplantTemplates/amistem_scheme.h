/*=========================================================================
  HPROJECT
  Copyright (c) Ernesto Durante, Julien de Siebenthal
  All rights reserved.
  See Copyrights.txt for details
  =========================================================================*/

#include "SboAmistem.h"

#include "SboTPCatalogElement.h"
#include "SboTPCatalogList.h"
#include "SboMathLibBase.h"
#include "SboPluginDefs.h"

#include <QDir>
#include <QIcon>

#define ICONSET_STR(s) QIcon(":/TPCatalogIcons/" s)

namespace XXXStem {

  constexpr auto ProductRangeStartsAt = hproj::MDCA::productRangeStartsAt(hproj::MDCA::Product::AMISTEM);

  constexpr auto CompanyName = hproj::MDCA::companyName;
  constexpr auto ProductName = hproj::MDCA::productName(hproj::MDCA::Product::AMISTEM);

  constexpr auto RCCIdName   = hproj::MDCA::RCCIdName(hproj::MDCA::Product::AMISTEM);
  constexpr auto RCCFileName = hproj::MDCA::RCCFileName(hproj::MDCA::Product::AMISTEM);
  constexpr auto RCCPath     = hproj::MDCA::RCCPath(hproj::MDCA::Product::AMISTEM);

  const QIcon   PartIcon=ICONSET_STR("generic_stem.png");
  const QString PartMenuText("");
  const QString PartTooltipText("");
  const QString ItemName("AMISTEM-P");

  const QIcon   PartHeadIcon=ICONSET_STR("spcl_head.png");
  const QString PartHeadMenuText("");
  const QString PartHeadTooltipText("");

  enum class S3UID: SboShape3UID{
				 STEM_STD_0 = ProductRangeStartsAt + 50L,
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

                                 STEM_LAT_0, //offset 11
				 STEM_LAT_1,
                                 STEM_LAT_2,
                                 STEM_LAT_3,
                                 STEM_LAT_4,
                                 STEM_LAT_5,
                                 STEM_LAT_6,
                                 STEM_LAT_7,
                                 STEM_LAT_8,

				 STEM_STD_SN_0, //offset 20
				 STEM_STD_SN_1,
                                 STEM_STD_SN_2,
                                 STEM_STD_SN_3,
                                 STEM_STD_SN_4,
                                 STEM_STD_SN_5,
                                 STEM_STD_SN_6,
                                 STEM_STD_SN_7,
                                 STEM_STD_SN_8,
                                 STEM_STD_SN_9,
                                 STEM_STD_SN_10,

                                 STEM_LAT_SN_0, //offset 31
				 STEM_LAT_SN_1,
                                 STEM_LAT_SN_2,
                                 STEM_LAT_SN_3,
                                 STEM_LAT_SN_4,
                                 STEM_LAT_SN_5,
                                 STEM_LAT_SN_6,
                                 STEM_LAT_SN_7,
                                 STEM_LAT_SN_8,

				 CUTPLANE,
				 HEAD_M4,
				 HEAD_P0,
				 HEAD_P4,
				 HEAD_P8,
				 HEAD_P12,
                                 RANGE_CCD_STD,
                                 RANGE_CCD_LAT,
                                 RANGE_CCD_STD_SN,
                                 RANGE_CCD_LAT_SN,

  };

  const S3UID lowerS3UID=S3UID::STEM_STD_0;
  const S3UID upperS3UID=S3UID::RANGE_CCD_LAT_SN;

  const S3UID defaultS3StemRUID=S3UID::STEM_STD_5;
  const S3UID defaultS3HeadUID=S3UID::HEAD_P0;

  SboShape3Label s3( S3UID e) { return SboShape3Label(SboShape3Label::utype(e));}

  bool isCCD_STD(SboShape3Label l) {
   //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_STD_0),s3(S3UID::STEM_STD_10));
  }

  bool isCCD_LAT(SboShape3Label l) {
    //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_LAT_0),s3(S3UID::STEM_LAT_8));
  }

  bool isCCD_STD_SN(SboShape3Label l) {
   //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_STD_SN_0),s3(S3UID::STEM_STD_SN_10));
  }

  bool isCCD_LAT_SN(SboShape3Label l) {
    //add left side
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_LAT_SN_0),s3(S3UID::STEM_LAT_SN_8));
  }

  bool isSTD(SboShape3Label l) {
    return isCCD_STD(l) || isCCD_STD_SN(l);
  }

  bool isLAT(SboShape3Label l) {
    return isCCD_LAT(l) || isCCD_LAT_SN(l);
  }


  bool isStem(SboShape3Label l) {
    return isCCD_STD(l) || isCCD_LAT(l) || isCCD_STD_SN(l) || isCCD_LAT_SN(l);
  }

  bool isHead(SboShape3Label l){
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::HEAD_M4),s3(S3UID::HEAD_P12));
  }

  bool isRange(SboShape3Label l){
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::RANGE_CCD_STD),s3(S3UID::RANGE_CCD_LAT_SN));
  }


  inline SboShape3Label nextPrevStem(SboShape3Label aL,bool aNext){
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    const auto nL= aL.next(aNext ? 1: -1);

    if(isCCD_STD_SN(aL))
      return isCCD_STD_SN(nL) ? nL: aL;

    if(isCCD_LAT_SN(aL))
      return isCCD_LAT_SN(nL) ? nL: aL;

    if(isCCD_LAT(aL))
        return isCCD_LAT(nL) ? nL: aL;

    return isCCD_STD(nL) ? nL: aL;
  }

  inline SboShape3Label getCCDRange(SboShape3Label aL){

    if(isCCD_STD(aL)) return s3(S3UID::RANGE_CCD_STD);
    if(isCCD_LAT(aL)) return s3(S3UID::RANGE_CCD_LAT);

    if(isCCD_STD_SN(aL)) return s3(S3UID::RANGE_CCD_STD_SN);
    if(isCCD_LAT_SN(aL)) return s3(S3UID::RANGE_CCD_LAT_SN);

    return {};
  }

  auto getRangeStats(SboShape3Label aL) {
    HPROJ_DCHECK2(isStem(aL) || isRange(aL),"must be stem or eange");

    struct R { int r0=0; int r1=0; int l=0; int s=0; SboShape3Label label0; };

    if(isStem(aL)){
      if(isCCD_STD(aL))      return R{0,10,0 ,10,  s3(S3UID::STEM_STD_0)};
      if(isCCD_LAT(aL))      return R{0,8 ,11,19,  s3(S3UID::STEM_LAT_0)};
      if(isCCD_STD_SN(aL))   return R{0,10,20,30,  s3(S3UID::STEM_STD_SN_0)};
      if(isCCD_LAT_SN(aL))   return R{0,8 ,31,39,  s3(S3UID::STEM_LAT_SN_0)};
    }

    if(aL==s3(S3UID::RANGE_CCD_STD))      return R{0,10,0 ,10,  s3(S3UID::STEM_STD_0)};
    if(aL==s3(S3UID::RANGE_CCD_LAT))      return R{0,8 ,11,19,  s3(S3UID::STEM_LAT_0)};
    if(aL==s3(S3UID::RANGE_CCD_STD_SN))   return R{0,10,20,30,  s3(S3UID::STEM_STD_SN_0)};
    if(aL==s3(S3UID::RANGE_CCD_LAT_SN))   return R{0,8 ,31,39,  s3(S3UID::STEM_LAT_SN_0)};

    return R{};
  }

  int getStemSize(SboShape3Label aL){
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    if (aL == s3(S3UID::STEM_STD_0) ) return 0;
    if (aL == s3(S3UID::STEM_STD_1) ) return 1;
    if (aL == s3(S3UID::STEM_STD_2) ) return 2;
    if (aL == s3(S3UID::STEM_STD_3) ) return 3;
    if (aL == s3(S3UID::STEM_STD_4) ) return 4;
    if (aL == s3(S3UID::STEM_STD_5) ) return 5;
    if (aL == s3(S3UID::STEM_STD_6) ) return 6;
    if (aL == s3(S3UID::STEM_STD_7) ) return 7;
    if (aL == s3(S3UID::STEM_STD_8) ) return 8;
    if (aL == s3(S3UID::STEM_STD_9) ) return 9;
    if (aL == s3(S3UID::STEM_STD_10)) return 10;

    if(aL == s3(S3UID::STEM_LAT_0)) return 0;
    if(aL == s3(S3UID::STEM_LAT_1)) return 1;
    if(aL == s3(S3UID::STEM_LAT_2)) return 2;
    if(aL == s3(S3UID::STEM_LAT_3)) return 3;
    if(aL == s3(S3UID::STEM_LAT_4)) return 4;
    if(aL == s3(S3UID::STEM_LAT_5)) return 5;
    if(aL == s3(S3UID::STEM_LAT_6)) return 6;
    if(aL == s3(S3UID::STEM_LAT_7)) return 7;
    if(aL == s3(S3UID::STEM_LAT_8)) return 8;

    if(aL == s3(S3UID::STEM_STD_SN_0) ) return 0;
    if(aL == s3(S3UID::STEM_STD_SN_1) ) return 1;
    if(aL == s3(S3UID::STEM_STD_SN_2) ) return 2;
    if(aL == s3(S3UID::STEM_STD_SN_3) ) return 3;
    if(aL == s3(S3UID::STEM_STD_SN_4) ) return 4;
    if(aL == s3(S3UID::STEM_STD_SN_5) ) return 5;
    if(aL == s3(S3UID::STEM_STD_SN_6) ) return 6;
    if(aL == s3(S3UID::STEM_STD_SN_7) ) return 7;
    if(aL == s3(S3UID::STEM_STD_SN_8) ) return 8;
    if(aL == s3(S3UID::STEM_STD_SN_9) ) return 9;
    if(aL == s3(S3UID::STEM_STD_SN_10)) return 10;

    if(aL == s3(S3UID::STEM_LAT_SN_0)) return 0;
    if(aL == s3(S3UID::STEM_LAT_SN_1)) return 1;
    if(aL == s3(S3UID::STEM_LAT_SN_2)) return 2;
    if(aL == s3(S3UID::STEM_LAT_SN_3)) return 3;
    if(aL == s3(S3UID::STEM_LAT_SN_4)) return 4;
    if(aL == s3(S3UID::STEM_LAT_SN_5)) return 5;
    if(aL == s3(S3UID::STEM_LAT_SN_6)) return 6;
    if(aL == s3(S3UID::STEM_LAT_SN_7)) return 7;
    if(aL == s3(S3UID::STEM_LAT_SN_8)) return 8;

    return 0;
  }


  SboShape3Label getSimilarLabel(SboShape3Label aLabel, SboShape3Label aTargetR){

    HPROJ_DCHECK2(isStem(aLabel) || isRange(aLabel),"must be stem & range");

    const auto sourceR=getCCDRange(aLabel);
    const auto sz=getStemSize(aLabel);
    const auto S=getRangeStats(sourceR);
    const auto T=getRangeStats(aTargetR);
    int tsz=sz;

    if(sourceR == s3(S3UID::RANGE_CCD_STD)){

      if(aTargetR == s3(S3UID::RANGE_CCD_STD_SN))    tsz=SboML::clamp<int>(sz,T.r0,T.r1);
      else if(sz==0 || sz==10) return aLabel; //NOTE: return the same label because no similar size exists for LAT

      if(aTargetR == s3(S3UID::RANGE_CCD_LAT))    tsz=SboML::clamp<int>(sz-1,T.r0,T.r1);
      if(aTargetR == s3(S3UID::RANGE_CCD_LAT_SN)) tsz=SboML::clamp<int>(sz-1,T.r0,T.r1);
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_LAT)){

      if(aTargetR == s3(S3UID::RANGE_CCD_STD))    tsz=SboML::clamp<int>(sz+1,T.r0,T.r1);
      if(aTargetR == s3(S3UID::RANGE_CCD_STD_SN)) tsz=SboML::clamp<int>(sz+1,T.r0,T.r1);
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_STD_SN)){

      if(aTargetR == s3(S3UID::RANGE_CCD_STD))    tsz=SboML::clamp<int>(sz,T.r0,T.r1);
      else if(sz==0 || sz==10) return aLabel; //NOTE: return the same label because no similar size exists for LAT

      if(aTargetR == s3(S3UID::RANGE_CCD_LAT))    tsz=SboML::clamp<int>(sz-1,T.r0,T.r1);
      if(aTargetR == s3(S3UID::RANGE_CCD_LAT_SN)) tsz=SboML::clamp<int>(sz-1,T.r0,T.r1);

    }
    else if(sourceR == s3(S3UID::RANGE_CCD_LAT_SN)){

      if(aTargetR == s3(S3UID::RANGE_CCD_STD))    tsz=SboML::clamp<int>(sz+1,T.r0,T.r1);
      if(aTargetR == s3(S3UID::RANGE_CCD_STD_SN)) tsz=SboML::clamp<int>(sz+1,T.r0,T.r1);
    }

    return T.label0.next(tsz);
  }


  SboPoint3 getRES_01(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto sourceR=getCCDRange(aLabel);
    const auto sz=getStemSize(aLabel);

    float y=0.f,z=0.f;

    //NOTE: DATA come from the xls file
    if(sourceR == s3(S3UID::RANGE_CCD_STD)){

      if(sz==0)       { y=14.52f; z=14.52f;  }
      else if(sz==1)  { y=14.78f; z=14.78f;  }
      else if(sz==2)  { y=15.49f; z=15.49f;  }
      else if(sz==3)  { y=16.19f; z=16.19f;  }
      else if(sz==4)  { y=16.90f; z=16.90f;  }
      else if(sz==5)  { y=17.54f; z=17.54f;  }
      else if(sz==6)  { y=18.17f; z=18.17f;  }
      else if(sz==7)  { y=18.80f; z=18.80f;  }
      else if(sz==8)  { y=19.37f; z=19.37f;  }
      else if(sz==9)  { y=20.07f; z=20.07f;  }
      else if(sz==10) { y=20.78f; z=20.78f;  }
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_LAT)){

      if(sz==0)       { y=13.99f; z=10.54f;  }
      else if(sz==1)  { y=14.70f; z=11.08f;  }
      else if(sz==2)  { y=15.40f; z=11.61f;  }
      else if(sz==3)  { y=16.35f; z=12.32f;  }
      else if(sz==4)  { y=16.76f; z=12.63f;  }
      else if(sz==5)  { y=17.38f; z=13.1f;  }
      else if(sz==6)  { y=17.88f; z=13.55f;  }
      else if(sz==7)  { y=18.59f; z=14.01f;  }
      else if(sz==8)  { y=19.2f;  z=14.47f;  }
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_STD_SN)){

      if(sz==0)       { y=14.51f; z=14.51f;  }
      else if(sz==1)  { y=14.77f; z=14.77f;  }
      else if(sz==2)  { y=15.48f; z=15.48f;  }
      else if(sz==3)  { y=16.19f; z=16.19f;  }
      else if(sz==4)  { y=16.9f;  z=16.9f;  }
      else if(sz==5)  { y=17.53f; z=17.53f;  }
      else if(sz==6)  { y=18.17f; z=18.17f;  }
      else if(sz==7)  { y=18.8f;  z=18.8f;  }
      else if(sz==8)  { y=19.36f; z=19.36f;  }
      else if(sz==9)  { y=20.07f; z=20.07f;  }
      else if(sz==10) { y=20.78f; z=20.78f;  }
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_LAT_SN)){

      if(sz==0)       { y=13.99f; z=10.54f;  }
      else if(sz==1)  { y=14.7f;  z=11.08f;  }
      else if(sz==2)  { y=15.4f;  z=11.61f;  }
      else if(sz==3)  { y=16.35f; z=12.32f;  }
      else if(sz==4)  { y=16.76f; z=12.63f;  }
      else if(sz==5)  { y=17.38f; z=13.1f;  }
      else if(sz==6)  { y=17.98f; z=13.55f;  }
      else if(sz==7)  { y=18.59f; z=14.01f;  }
      else if(sz==8)  { y=19.2f;  z=14.47f;  }
    }

    return SboPoint3(0,y,z);
  }

  SboPoint3 getRES_02(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto sourceR=getCCDRange(aLabel);
    const auto sz=getStemSize(aLabel);

    return SboPoint3(0,0,0);
  }

  SboPoint3 getTPR_01(SboShape3Label aLabel) {
    HPROJ_DCHECK2(isStem(aLabel),"must be stem");

    const auto sourceR=getCCDRange(aLabel);
    const auto sz=getStemSize(aLabel);

    float y=0.f,z=0.f;

    //NOTE: DATA come from the xls file
    if(sourceR == s3(S3UID::RANGE_CCD_STD)){

      if(sz==0)       { y=41.50f; z=41.50f;  }
      else if(sz==1)  { y=41.95f; z=41.95f;  }
      else if(sz==2)  { y=43.19f; z=43.19f;  }
      else if(sz==3)  { y=44.44f; z=44.44f;  }
      else if(sz==4)  { y=45.70f; z=45.70f;  }
      else if(sz==5)  { y=46.84f; z=46.84f;  }
      else if(sz==6)  { y=48.00f; z=48.00f;  }
      else if(sz==7)  { y=49.18f; z=49.18f;  }
      else if(sz==8)  { y=50.25f; z=50.25f;  }
      else if(sz==9)  { y=51.48f; z=51.48f;  }
      else if(sz==10) { y=52.87f; z=52.87f;  }
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_LAT)){

      if(sz==0)       { y=43.73f; z=32.96f;  }
      else if(sz==1)  { y=45.13f; z=34.01f;  }
      else if(sz==2)  { y=46.54f; z=35.07f;  }
      else if(sz==3)  { y=47.94f; z=36.13f;  }
      else if(sz==4)  { y=49.3f;  z=37.15f;  }
      else if(sz==5)  { y=50.61f; z=38.14f;  }
      else if(sz==6)  { y=51.91f; z=39.12f;  }
      else if(sz==7)  { y=53.26f; z=40.13f;  }
      else if(sz==8)  { y=54.41f; z=41.00f;  }
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_STD_SN)){

      if(sz==0)       { y=37.96f; z=37.96f;  }
      else if(sz==1)  { y=38.42f; z=38.42f;  }
      else if(sz==2)  { y=39.65f; z=39.65f;  }
      else if(sz==3)  { y=40.91f; z=40.91f;  }
      else if(sz==4)  { y=42.16f; z=42.16f;  }
      else if(sz==5)  { y=43.30f; z=43.30f;  }
      else if(sz==6)  { y=44.46f; z=44.46f;  }
      else if(sz==7)  { y=45.64f; z=45.64f;  }
      else if(sz==8)  { y=46.72f; z=46.72f;  }
      else if(sz==9)  { y=47.94f; z=47.94f;  }
      else if(sz==10) { y=49.33f; z=49.33f;  }
    }
    else if(sourceR == s3(S3UID::RANGE_CCD_LAT_SN)){

      if(sz==0)       { y=43.73f; z=32.96f;  }
      else if(sz==1)  { y=45.13f; z=34.01f;  }
      else if(sz==2)  { y=45.64f; z=35.07f;  }
      else if(sz==3)  { y=47.94f; z=36.13f;  }
      else if(sz==4)  { y=49.3f;  z=37.15f;  }
      else if(sz==5)  { y=50.61f; z=38.14f;  }
      else if(sz==6)  { y=51.91f; z=39.12f;  }
      else if(sz==7)  { y=53.26f; z=40.13f;  }
      else if(sz==8)  { y=54.41f; z=41.00f;  }
    }

    return SboPoint3(0,y,z);
  }

  SboMatrix3 getShift(SboShape3Label aSourceL, SboShape3Label aTargetL){

    auto neckOS =getRES_01(aSourceL);
    auto neckOT =getRES_01(aTargetL);
    const  auto sz=getStemSize(aSourceL);

    if(isSTD(aSourceL) && isSTD(aTargetL)){
      return SboML::transMat3(neckOS - neckOT);
    }

    if(isCCD_LAT(aSourceL) && isCCD_LAT(aTargetL)){
      return SboML::transMat3(neckOS - neckOT);
    }

    if(isCCD_LAT_SN(aSourceL) && isCCD_LAT_SN(aTargetL)){
      return SboML::transMat3(neckOS - neckOT);
    }

    //NOTE: Z shift column in the xls file
    if(isCCD_STD(aSourceL)  && isCCD_LAT(aTargetL)){

      float t=0.f;
      if(sz == 1)      t=5.89f;
      else if(sz == 2) t=6.03f;
      else if(sz == 3) t=6.22f;
      else if(sz == 4) t=6.39f;
      else if(sz == 5) t=6.55f;
      else if(sz == 6) t=6.71f;
      else if(sz == 7) t=6.85f;
      else if(sz == 8) t=7.0f;
      else if(sz == 9) t=7.26f;

      return SboML::transMat3(0,0,t);
    }

    if(isCCD_LAT(aSourceL) && isCCD_STD(aTargetL)){

      float t=0.f;
      if(sz == 0)      t=5.89f;
      else if(sz == 1) t=6.03f;
      else if(sz == 2) t=6.22f;
      else if(sz == 3) t=6.39f;
      else if(sz == 4) t=6.55f;
      else if(sz == 5) t=6.71f;
      else if(sz == 6) t=6.85f;
      else if(sz == 7) t=7.0f;
      else if(sz == 8) t=7.26f;

      return SboML::transMat3(0,0,-t);
    }

    if(isCCD_STD_SN(aSourceL) && isCCD_LAT_SN(aTargetL)){

      float t=0.f;
      if(sz == 1)      t=5.01f;
      else if(sz == 2) t=5.19f;
      else if(sz == 3) t=5.38f;
      else if(sz == 4) t=5.58f;
      else if(sz == 5) t=5.69f;
      else if(sz == 6) t=5.87f;
      else if(sz == 7) t=6.07f;
      else if(sz == 8) t=6.13f;
      else if(sz == 9) t=6.48f;

      return SboML::transMat3(0,0,t);
    }

    if(isCCD_LAT_SN(aSourceL) && isCCD_STD_SN(aTargetL)){

      float t=0.f;
      if(sz == 0)      t=5.01f;
      else if(sz == 1) t=5.19f;
      else if(sz == 2) t=5.38f;
      else if(sz == 3) t=5.58f;
      else if(sz == 4) t=5.69f;
      else if(sz == 5) t=5.87f;
      else if(sz == 6) t=6.07f;
      else if(sz == 7) t=6.13f;
      else if(sz == 8) t=6.48f;

      return SboML::transMat3(0,0,-t);
    }


    return SboML::idMat3();
  }


}

int SboAmistem::rev() const
{
  return 1;
}

QString SboAmistem::productName() const
{
  return XXXStem::ProductName;
}

QString SboAmistem::companyName() const
{
  return XXXStem::CompanyName;
}

QString SboAmistem::message(int,const SboFemImplantConfig&) const
{
  return "Insert a meaningful message";
}

QString SboAmistem::setMeshInfoSearchPath(QString aPath)
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
    QDir::setSearchPaths(RCCIdName, {aPath + RCCPath + "/P_STD",
                                     aPath + RCCPath + "/P_LAT",
                                     aPath + RCCPath + "/PSN_STD",
                                     aPath + RCCPath + "/PSN_LAT"});
  }

  return {};
}

bool SboAmistem::meshInfoResourceFromRcc(QString& aRcc)
{
  aRcc=XXXStem::RCCFileName;
  return false;
}

bool SboAmistem::meshInfoResourceFromFileSystem()
{
  return true;
}


void SboAmistem::meshInfoRCList(SboMeshInfoRCList& rcList)
{
  using namespace XXXStem;
  auto next=[&](S3UID e,QString s,QString aRCCId) { rcList.push_back({s3(e),aRCCId + QString(":") + s + ".wrl"});};

  next(S3UID::STEM_STD_0, "01_18_399",RCCIdName);
  next(S3UID::STEM_STD_1, "01_18_400",RCCIdName);
  next(S3UID::STEM_STD_2, "01_18_401",RCCIdName);
  next(S3UID::STEM_STD_3, "01_18_402",RCCIdName);
  next(S3UID::STEM_STD_4, "01_18_403",RCCIdName);
  next(S3UID::STEM_STD_5, "01_18_404",RCCIdName);
  next(S3UID::STEM_STD_6, "01_18_405",RCCIdName);
  next(S3UID::STEM_STD_7, "01_18_406",RCCIdName);
  next(S3UID::STEM_STD_8, "01_18_407",RCCIdName);
  next(S3UID::STEM_STD_9, "01_18_408",RCCIdName);
  next(S3UID::STEM_STD_10,"01_18_409",RCCIdName);

  next(S3UID::STEM_LAT_0,"01_18_410",RCCIdName);
  next(S3UID::STEM_LAT_1,"01_18_411",RCCIdName);
  next(S3UID::STEM_LAT_2,"01_18_412",RCCIdName);
  next(S3UID::STEM_LAT_3,"01_18_413",RCCIdName);
  next(S3UID::STEM_LAT_4,"01_18_414",RCCIdName);
  next(S3UID::STEM_LAT_5,"01_18_415",RCCIdName);
  next(S3UID::STEM_LAT_6,"01_18_416",RCCIdName);
  next(S3UID::STEM_LAT_7,"01_18_417",RCCIdName);
  next(S3UID::STEM_LAT_8,"01_18_418",RCCIdName);

  next(S3UID::STEM_STD_SN_0, "01_18_459",RCCIdName);
  next(S3UID::STEM_STD_SN_1, "01_18_460",RCCIdName);
  next(S3UID::STEM_STD_SN_2, "01_18_461",RCCIdName);
  next(S3UID::STEM_STD_SN_3, "01_18_462",RCCIdName);
  next(S3UID::STEM_STD_SN_4, "01_18_463",RCCIdName);
  next(S3UID::STEM_STD_SN_5, "01_18_464",RCCIdName);
  next(S3UID::STEM_STD_SN_6, "01_18_465",RCCIdName);
  next(S3UID::STEM_STD_SN_7, "01_18_466",RCCIdName);
  next(S3UID::STEM_STD_SN_8, "01_18_467",RCCIdName);
  next(S3UID::STEM_STD_SN_9, "01_18_468",RCCIdName);
  next(S3UID::STEM_STD_SN_10,"01_18_469",RCCIdName);

  next(S3UID::STEM_LAT_SN_0,"01_18_470",RCCIdName);
  next(S3UID::STEM_LAT_SN_1,"01_18_471",RCCIdName);
  next(S3UID::STEM_LAT_SN_2,"01_18_472",RCCIdName);
  next(S3UID::STEM_LAT_SN_3,"01_18_473",RCCIdName);
  next(S3UID::STEM_LAT_SN_4,"01_18_474",RCCIdName);
  next(S3UID::STEM_LAT_SN_5,"01_18_475",RCCIdName);
  next(S3UID::STEM_LAT_SN_6,"01_18_476",RCCIdName);
  next(S3UID::STEM_LAT_SN_7,"01_18_477",RCCIdName);
  next(S3UID::STEM_LAT_SN_8,"01_18_478",RCCIdName);

}


void SboAmistem::parts(SboTPCatalogList& prodList)
{
  using namespace XXXStem;

  auto stemRange= new SboTPCPartMonoStem(productName(),SboAnatomLocation::None);
  stemRange->_iconSet=PartIcon;
  stemRange->_menuText=PartMenuText;
  stemRange->_tooltipText=PartTooltipText;
  stemRange->setDefaultLabel(s3(defaultS3StemRUID));


  struct CCD_Amistem : public SboTPCPartMonoStem::CCD {

    virtual RT range(SboShape3Label l) const override {
      if(isCCD_STD(l)) return _rSTD;
      if(isCCD_LAT(l)) return _rLAT;
      if(isCCD_STD_SN(l)) return _rSTD_SN;
      if(isCCD_LAT_SN(l)) return _rLAT_SN;
      return {};
    }

    virtual SboShape3Label similarLabel(SboShape3Label aL, SboShape3Label aNextCCDRange) const{
      return getSimilarLabel(aL,aNextCCDRange);
    }

    //0 follow neck origin
    //1 keep transform
    virtual int strategy(SboShape3Label /*nextLabel*/, SboShape3Label /*currLabel*/) const {
      HPROJ_DCHECK(!"strategy should never be called in rev 1");
      return 0;
    }


    virtual std::vector<RT> ranges() const override { return {_rSTD,_rLAT,_rSTD_SN,_rLAT_SN};}

    const RT _rSTD={0,  10,  s3(XXXStem::S3UID::RANGE_CCD_STD),"STD(135°)"};
    const RT _rLAT={11, 19,  s3(XXXStem::S3UID::RANGE_CCD_LAT),"LAT(127°)"};
    const RT _rSTD_SN={20, 30,  s3(XXXStem::S3UID::RANGE_CCD_STD_SN),"SN STD(135°)"};
    const RT _rLAT_SN={31, 39,  s3(XXXStem::S3UID::RANGE_CCD_LAT_SN),"SN LAT(127°)"};
  };

  stemRange->_CCDPart = std::make_unique<CCD_Amistem>();


  auto next=[&](S3UID e,QString s) { stemRange->push_back(new SboTPCatalogItem(stemRange,s3(e), ItemName,s));};

  next(S3UID::STEM_STD_0, "STD 00");
  next(S3UID::STEM_STD_1, "STD 0");
  next(S3UID::STEM_STD_2, "STD 1");
  next(S3UID::STEM_STD_3, "STD 2");
  next(S3UID::STEM_STD_4, "STD 3");
  next(S3UID::STEM_STD_5, "STD 4");
  next(S3UID::STEM_STD_6, "STD 5");
  next(S3UID::STEM_STD_7, "STD 6");
  next(S3UID::STEM_STD_8, "STD 7");
  next(S3UID::STEM_STD_9, "STD 8");
  next(S3UID::STEM_STD_10,"STD 9");

  next(S3UID::STEM_LAT_0,"LAT 0");
  next(S3UID::STEM_LAT_1,"LAT 1");
  next(S3UID::STEM_LAT_2,"LAT 2");
  next(S3UID::STEM_LAT_3,"LAT 3");
  next(S3UID::STEM_LAT_4,"LAT 4");
  next(S3UID::STEM_LAT_5,"LAT 5");
  next(S3UID::STEM_LAT_6,"LAT 6");
  next(S3UID::STEM_LAT_7,"LAT 7");
  next(S3UID::STEM_LAT_8,"LAT 8");

  next(S3UID::STEM_STD_SN_0, "SN STD 00");
  next(S3UID::STEM_STD_SN_1, "SN STD 0");
  next(S3UID::STEM_STD_SN_2, "SN STD 1");
  next(S3UID::STEM_STD_SN_3, "SN STD 2");
  next(S3UID::STEM_STD_SN_4, "SN STD 3");
  next(S3UID::STEM_STD_SN_5, "SN STD 4");
  next(S3UID::STEM_STD_SN_6, "SN STD 5");
  next(S3UID::STEM_STD_SN_7, "SN STD 6");
  next(S3UID::STEM_STD_SN_8, "SN STD 7");
  next(S3UID::STEM_STD_SN_9, "SN STD 8");
  next(S3UID::STEM_STD_SN_10,"SN STD 9");

  next(S3UID::STEM_LAT_SN_0,"SN LAT 0");
  next(S3UID::STEM_LAT_SN_1,"SN LAT 1");
  next(S3UID::STEM_LAT_SN_2,"SN LAT 2");
  next(S3UID::STEM_LAT_SN_3,"SN LAT 3");
  next(S3UID::STEM_LAT_SN_4,"SN LAT 4");
  next(S3UID::STEM_LAT_SN_5,"SN LAT 5");
  next(S3UID::STEM_LAT_SN_6,"SN LAT 6");
  next(S3UID::STEM_LAT_SN_7,"SN LAT 7");
  next(S3UID::STEM_LAT_SN_8,"SN LAT 8");

  prodList.push_back(stemRange);


  //NOTE: Last argument S3UID::HEAD_P4 locates the CONE Lateral tip.
  //NOTE: The default label must be different from HEAD_P4 to be able to compute the cone axis.
  auto headRange= new SboTPCPartHead(productName(),s3(S3UID::HEAD_P4));
  headRange->_iconSet=PartHeadIcon;
  headRange->_menuText=PartHeadMenuText;
  headRange->_tooltipText=PartHeadTooltipText;
  headRange->setDefaultLabel(s3(defaultS3HeadUID));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_M4),"Head","S"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P0),"Head","M"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P4),"Head","L"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P8),"Head","XL"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P12),"Head","XXL"));

  prodList.push_back(headRange);

  auto cutPlaneRange= new SboTPCPartCutPlane(productName());
  cutPlaneRange->setDefaultLabel(s3(S3UID::CUTPLANE));
  cutPlaneRange->push_back(new SboTPCatalogItem(cutPlaneRange,s3(S3UID::CUTPLANE),"Cutplane"));

  prodList.push_back(cutPlaneRange);
}


bool SboAmistem::inRange(SboShape3Label aL)
{
  using namespace XXXStem;
  return SboML::in_closed_range<SboShape3Label>(aL,s3(lowerS3UID),s3(upperS3UID));
}

SboMatrix3 SboAmistem::headToNeckMatrix(SboShape3Label aHeadLabel, SboShape3Label aNeckLabel)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aHeadLabel);
  HPROJ_UNUSED(aNeckLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboAmistem::neckToStemMatrix(SboShape3Label aNeckLabel, SboShape3Label aStemLabel, SboAnatomLocation aSide)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aNeckLabel);
  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboAmistem::headToStemMatrix(SboShape3Label aHeadLabel, SboShape3Label aStemLabel)
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

  //NOTE: the neck offset 3.5355f is computed using the neck points from the xls file

  float l=3.5355f;

  if(aHeadLabel == s3(S3UID::HEAD_M4))      l*=-2;
  else if(aHeadLabel == s3(S3UID::HEAD_P0)) l*=-1;
  else if(aHeadLabel == s3(S3UID::HEAD_P4)) l=0.f;
  //else if(aHeadLabel == s3(S3UID::HEAD_P8)) l*=1;
  else if(aHeadLabel == s3(S3UID::HEAD_P12)) l*=2;

  if(isCCD_LAT(aStemLabel)){
    //NOTE: wrong coords provided by the xls file. So we add a ha-doc correction
    l+=0.9f + 3.5355f;
  }

  auto m=SboML::transMat3(headO + neckAxis * l);

  return m;


}


SboPlane3 SboAmistem::cutPlane(SboShape3Label aStemLabel)
{
  //return the cutplane equation in CPT_FRAME

  //The cutplane is used to position the component in WORD_CS (STD_FRAME)

  //Default plane position and orientation: centered at (0,0,0) with normal (0,1,0)
  //Should return something like Plane3(Point3(0,0,0),Vector3(0,1,0)).transform(m)
  //Compute the TRAFFFO m

  //FIXME: Plane3 origin is supposed to be the neck origin

  using namespace XXXStem;
  const auto neckO=getRES_01(aStemLabel);

  auto r=SboML::rotMatX3(SboML::deg2Rad<float>(45.0f));
  auto t=SboML::transMat3(neckO);
  auto m=t*r;

  return SboPlane3(SboPoint3(0,0,0), SboVector3(0,1,0)).transform(m);
}

SboBbox3 SboAmistem::cutPlaneBbox(SboShape3Label aStemLabel)
{
  //return a bbox in CPT_FRAME that intersects the cutplane

  //NOTE: if the intersection is empty, the trace of the plane is not
  //visible.

  //Consider a bbox of dimensions (50,50,50) centered at (0,0,0)
  //Strategy the bbox center must be translated to the neck origin

  using namespace XXXStem;

  SboPoint3 pmin(-40.0f,-80.0f,-40.0f);
  SboPoint3 pmax(40.0f,80.0f,40.0f);

  const auto neckO=getRES_01(aStemLabel);
  auto m=SboML::transMat3(neckO);

  pmin=m(pmin);
  pmax=m(pmax);

  return SboML::makeBbox3(pmin,pmax);
}

SboMatrix3 SboAmistem::stemToStemMatrix(const SboFemImplantConfig& aOriginFemIC,const SboFemImplantConfig& aTargetFemIC)
{
  //NOTE: return a TRAFFO that transforms from aOriginStemLabel to aTargetStemLabel in CPT_FRAME
  //LINK: [[hdoch:capture-hproj-implants.org::REV_STEMTOSTEM]]

  using namespace XXXStem;

  //NOTE: From the xls file we don't know how to go from LAT to LAT SN and vice-versa.
  //However we are lucky enough because jumping form STD to STD SN (and vice-versa) can be performed
  //by matching the neck origin.
  //The missing paths can be now deduced from the known jumps.

  if(isCCD_STD(aOriginFemIC.stemLabel()) && isCCD_LAT_SN(aTargetFemIC.stemLabel())){

    //Get STD SN from source
    auto sno=getSimilarLabel(aOriginFemIC.stemLabel(),s3(S3UID::RANGE_CCD_STD_SN));

    //STD to STD SN to LAT SN
    return getShift(sno,aTargetFemIC.stemLabel()) * getShift(aOriginFemIC.stemLabel(),sno);
  }

  if(isCCD_LAT_SN(aOriginFemIC.stemLabel()) && isCCD_STD(aTargetFemIC.stemLabel())){

    //Get STD SN from target
    auto snt=getSimilarLabel(aTargetFemIC.stemLabel(),s3(S3UID::RANGE_CCD_STD_SN));

    //LAT_SN to STD SN to STD
    return getShift(snt,aTargetFemIC.stemLabel()) * getShift(aOriginFemIC.stemLabel(),snt);
  }

  if(isCCD_LAT_SN(aOriginFemIC.stemLabel()) && isCCD_LAT(aTargetFemIC.stemLabel())){

    auto sno=getSimilarLabel(aOriginFemIC.stemLabel(),s3(S3UID::RANGE_CCD_STD_SN));

    auto stdt=getSimilarLabel(aTargetFemIC.stemLabel(),s3(S3UID::RANGE_CCD_STD));

    //LAT_SN to STD_SN to STD to LAT
    return getShift(stdt,aTargetFemIC.stemLabel()) * getShift(sno,stdt) * getShift(aOriginFemIC.stemLabel(),sno);
  }

  if(isCCD_STD_SN(aOriginFemIC.stemLabel()) && isCCD_LAT(aTargetFemIC.stemLabel())){

    //Get STD from source
    auto stdo=getSimilarLabel(aOriginFemIC.stemLabel(),s3(S3UID::RANGE_CCD_STD));

    //STD SN to STD to LAT
    return getShift(stdo,aTargetFemIC.stemLabel()) * getShift(aOriginFemIC.stemLabel(),stdo);
  }

  if(isCCD_LAT(aOriginFemIC.stemLabel()) && isCCD_STD_SN(aTargetFemIC.stemLabel())){

    //Get STD from source
    auto stdo=getSimilarLabel(aOriginFemIC.stemLabel(),s3(S3UID::RANGE_CCD_STD));

    //LAT to STD to STD SN
    return getShift(stdo,aTargetFemIC.stemLabel()) * getShift(aOriginFemIC.stemLabel(),stdo);
  }

  if(isCCD_LAT(aOriginFemIC.stemLabel()) && isCCD_LAT_SN(aTargetFemIC.stemLabel())){

    auto stdo=getSimilarLabel(aOriginFemIC.stemLabel(),s3(S3UID::RANGE_CCD_STD));

    auto snt=getSimilarLabel(aTargetFemIC.stemLabel(),s3(S3UID::RANGE_CCD_STD_SN));

    //LAT_SN to STD_SN to STD to LAT
    return getShift(snt,aTargetFemIC.stemLabel()) * getShift(stdo,snt) * getShift(aOriginFemIC.stemLabel(),stdo);
  }


  return getShift(aOriginFemIC.stemLabel(),aTargetFemIC.stemLabel());
}

SboMatrix3 SboAmistem::normalTrf(SboShape3Label aStemLabel, const SboPlane3 & aP3, const SboPoint3 & aO3)
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

  //to NORMAL_FRAME
  return SboML::rotMatZ3(SboML::deg2Rad<float>(-90.0f));
}

SboVector3 SboAmistem::offsetFF(SboShape3Label aStemLabel)
{

  // independently of the side (left or right)
  // x > 0 cpt moves medially
  // y > 0 cpt moves posteriorly
  // z > 0 cpt moves superiorly

  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;

  return {12.f,0.f,0.f};
}


SboFemImplantConfig SboAmistem::defaultFemIC(QString aPartName,SboAnatomLocation aRequestedSide)
{
  using namespace XXXStem;

  SboFemImplantConfig myFemIC(aRequestedSide,s3(defaultS3StemRUID),s3(defaultS3HeadUID));
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

SboFemImplantConfig SboAmistem::fillAndValidAssembly(const SboFemImplantConfig& aFemIC)
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

SboFemImplantConfig SboAmistem::nextPrev(const SboFemImplantConfig& aFemIC,bool aNext)
{
  using namespace XXXStem;

  auto fc=aFemIC;
  fc.setStemLabel(nextPrevStem(fc.stemLabel(),aNext));

  //NOTE: Don't check whether the config is a valid assembly or combination, let the application do it

  return fc;
}

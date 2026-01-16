/*=========================================================================
  HPROJECT
  Copyright (c) Ernesto Durante, Julien de Siebenthal
  All rights reserved.
  See Copyrights.txt for details
  =========================================================================*/

#include "SboCorail.h"

#include "SboTPCatalogElement.h"
#include "SboTPCatalogList.h"
#include "SboMathLibBase.h"
#include "SboPluginDefs.h"

#include <QDir>
#include <QIcon>

#define ICONSET_STR(s) QIcon(":/TPCatalogIcons/" s)

namespace XXXStem {
  constexpr auto ProductRangeStartsAt = hproj::JNJ::productRangeStartsAt(hproj::JNJ::Product::CORAIL);

  constexpr auto CompanyName = hproj::JNJ::companyName;
  constexpr auto ProductName = hproj::JNJ::productName(hproj::JNJ::Product::CORAIL);

  constexpr auto RCCIdName   = hproj::JNJ::RCCIdName(hproj::JNJ::Product::CORAIL);
  constexpr auto RCCFileName = hproj::JNJ::RCCFileName(hproj::JNJ::Product::CORAIL);
  constexpr auto RCCPath     = hproj::JNJ::RCCPath(hproj::JNJ::Product::CORAIL);

  const QIcon   PartIcon=ICONSET_STR("generic_stem.png");
  const QString PartMenuText("");
  const QString PartTooltipText("");
  const QString ItemName=hproj::JNJ::itemName(hproj::JNJ::Product::CORAIL);

  const QIcon   PartHeadIcon=ICONSET_STR("spcl_head.png");
  const QString PartHeadMenuText("");
  const QString PartHeadTooltipText("");

  //NOTE: Let 100 slots free in case further implants must be added
  enum class S3UID: SboShape3UID{
                                 STEM_KHO_A_135_0= ProductRangeStartsAt + 90L,
				 STEM_KHO_A_135_1,
				 STEM_KHO_A_135_2,
				 STEM_KHO_A_135_3,
				 STEM_KHO_A_135_4,
				 STEM_KHO_A_135_5,
				 STEM_KHO_A_135_6,
				 STEM_KHO_A_135_7,
				 STEM_KHO_A_135_8,
				 STEM_KHO_A_135_9,

				 STEM_KS_STD135_0, //offset 10
				 STEM_KS_STD135_1,
				 STEM_KS_STD135_2,
				 STEM_KS_STD135_3,
				 STEM_KS_STD135_4,
				 STEM_KS_STD135_5,
				 STEM_KS_STD135_6,
				 STEM_KS_STD135_7,
				 STEM_KS_STD135_8,
				 STEM_KS_STD135_9,
				 STEM_KS_STD135_10,

                                 STEM_KA_STD135_0, //offset 21
				 STEM_KA_STD135_1,
				 STEM_KA_STD135_2,
				 STEM_KA_STD135_3,
				 STEM_KA_STD135_4,
				 STEM_KA_STD135_5,
				 STEM_KA_STD135_6,
				 STEM_KA_STD135_7,
				 STEM_KA_STD135_8,
				 STEM_KA_STD135_9,
				 STEM_KA_STD135_10,

                                 STEM_KHO_S_135_0, //offset 32
				 STEM_KHO_S_135_1,
				 STEM_KHO_S_135_2,
				 STEM_KHO_S_135_3,
				 STEM_KHO_S_135_4,
				 STEM_KHO_S_135_5,
				 STEM_KHO_S_135_6,
				 STEM_KHO_S_135_7,
				 STEM_KHO_S_135_8,
				 STEM_KHO_S_135_9,

                                 STEM_KLA_125_0, //offset 42
				 STEM_KLA_125_1,
				 STEM_KLA_125_2,
				 STEM_KLA_125_3,
				 STEM_KLA_125_4,
				 STEM_KLA_125_5,
				 STEM_KLA_125_6,
				 STEM_KLA_125_7,
				 STEM_KLA_125_8,
				 STEM_KLA_125_9,

                                 STEM_STD125_S_0, //offset 52
                                 STEM_STD125_S_1,
                                 STEM_STD125_S_2,
                                 STEM_STD125_S_3,

                                 STEM_STD125_A_0, //offset 56
                                 STEM_STD125_A_1,
                                 STEM_STD125_A_2,
                                 STEM_STD125_A_3,
                                 STEM_STD125_A_4,
                                 STEM_STD125_A_5,
                                 STEM_STD125_A_6,
                                 STEM_STD125_A_7,

                                 STEM_SN_S_0,//offset 64
                                 STEM_SN_S_1,
                                 STEM_SN_S_2,
                                 STEM_SN_S_3,

                                 STEM_SN_A_0,//offset 68
                                 STEM_SN_A_1,
                                 STEM_SN_A_2,
                                 STEM_SN_A_3,
                                 STEM_SN_A_4,
                                 STEM_SN_A_5,
                                 STEM_SN_A_6,
                                 STEM_SN_A_7,

				 CUTPLANE,
				 HEAD_M4,
				 HEAD_P0,
				 HEAD_P4,
				 HEAD_P8,

                                 RANGE_CCD_KS_STD135, //range labels are not save on disk
                                 RANGE_CCD_KA_STD135,
                                 RANGE_CCD_KHO_S_135,
                                 RANGE_CCD_KHO_A_135,
                                 RANGE_CCD_KLA_125,
                                 RANGE_CCD_STD125_S,
                                 RANGE_CCD_STD125_A,
                                 RANGE_CCD_SN_S,
                                 RANGE_CCD_SN_A

  };

  const S3UID lowerS3UID=S3UID::STEM_KHO_A_135_0;
  const S3UID upperS3UID=S3UID::RANGE_CCD_SN_A;

  const S3UID defaultS3StemRUID=S3UID::STEM_KA_STD135_5;
  const S3UID defaultS3HeadUID=S3UID::HEAD_P0;

  inline SboShape3Label s3( S3UID e) { return SboShape3Label(SboShape3Label::utype(e));}

  inline bool isCCD_KS_STD135(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_KS_STD135_0),s3(S3UID::STEM_KS_STD135_10));
  }

  inline bool isCCD_KA_STD135(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_KA_STD135_0),s3(S3UID::STEM_KA_STD135_10));
  }

  inline bool isCCD_KHO_S_135(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_KHO_S_135_0),s3(S3UID::STEM_KHO_S_135_9));
  }

  inline bool isCCD_KHO_A_135(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_KHO_A_135_0),s3(S3UID::STEM_KHO_A_135_9));
  }

  inline bool isCCD_KLA_125(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_KLA_125_0),s3(S3UID::STEM_KLA_125_9));
  }


  inline bool isCCD_STD125_S(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_STD125_S_0),s3(S3UID::STEM_STD125_S_3));
  }

  inline bool isCCD_STD125_A(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_STD125_A_0),s3(S3UID::STEM_STD125_A_7));
  }

  inline bool isCCD_SN_S(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_SN_S_0),s3(S3UID::STEM_SN_S_3));
  }

  inline bool isCCD_SN_A(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_SN_A_0),s3(S3UID::STEM_SN_A_7));
  }


  inline bool isStem(SboShape3Label l) {
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::STEM_KHO_A_135_0),s3(S3UID::STEM_SN_A_7));
  }

  inline bool isHead(SboShape3Label l){
    return SboML::in_closed_range<SboShape3Label>(l,s3(S3UID::HEAD_M4),s3(S3UID::HEAD_P8));
  }

  inline bool hasCollar(SboShape3Label l){
    return isCCD_KHO_A_135(l) || isCCD_KA_STD135(l) || isCCD_KLA_125(l) || isCCD_STD125_A(l) || isCCD_SN_A(l);
  }


  inline SboShape3Label nextPrevStem(SboShape3Label aL,bool aNext){
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    const auto nL= aL.next(aNext ? 1: -1);

    if(isCCD_KS_STD135(aL)) return isCCD_KS_STD135(nL) ? nL: aL;
    if(isCCD_KA_STD135(aL)) return isCCD_KA_STD135(nL) ? nL: aL;

    if(isCCD_KHO_S_135(aL)) return isCCD_KHO_S_135(nL) ? nL: aL;
    if(isCCD_KHO_A_135(aL)) return isCCD_KHO_A_135(nL) ? nL: aL;

    if(isCCD_STD125_S(aL)) return isCCD_STD125_S(nL) ? nL: aL;
    if(isCCD_STD125_A(aL)) return isCCD_STD125_A(nL) ? nL: aL;

    if(isCCD_SN_S(aL)) return isCCD_SN_S(nL) ? nL: aL;
    if(isCCD_SN_A(aL)) return isCCD_SN_A(nL) ? nL: aL;

    return isCCD_KLA_125(nL) ? nL: aL;
  }

  inline SboShape3Label getCCDRange(SboShape3Label aL){
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    if(isCCD_KS_STD135(aL)) return s3(S3UID::RANGE_CCD_KS_STD135);
    if(isCCD_KA_STD135(aL)) return s3(S3UID::RANGE_CCD_KA_STD135);

    if(isCCD_KHO_S_135(aL)) return s3(S3UID::RANGE_CCD_KHO_S_135);
    if(isCCD_KHO_A_135(aL)) return s3(S3UID::RANGE_CCD_KHO_A_135);

    if(isCCD_KLA_125(aL)) return s3(S3UID::RANGE_CCD_KLA_125);

    if(isCCD_STD125_S(aL)) return s3(S3UID::RANGE_CCD_STD125_S);
    if(isCCD_STD125_A(aL)) return s3(S3UID::RANGE_CCD_STD125_A);

    if(isCCD_SN_S(aL)) return s3(S3UID::RANGE_CCD_SN_S);
    if(isCCD_SN_A(aL)) return s3(S3UID::RANGE_CCD_SN_A);

    return {};
  }


  inline int getCCDStartIdx(SboShape3Label aL){
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    if(isCCD_KHO_A_135(aL)) return 0;

    if(isCCD_KS_STD135(aL)) return 10;
    if(isCCD_KA_STD135(aL)) return 21;

    if(isCCD_KHO_S_135(aL)) return 32;

    if(isCCD_KLA_125(aL))   return 42;

    if(isCCD_STD125_S(aL)) return 52;
    if(isCCD_STD125_A(aL)) return 56;

    if(isCCD_SN_S(aL)) return 64;
    if(isCCD_SN_A(aL)) return 68;

    return 0;
  }


  inline int getSimilarOffset(int aOffset, SboShape3Label aSourceR, SboShape3Label aTargetR){

    //NOTE: see ProductInfo to get the relation between sizes
    //[[hdoc:hproject/capture-hproj-implants.org::twinsys]]

    //same nbr of sizes for KHO_A,KHO_S,KLA

    if(aSourceR == s3(S3UID::RANGE_CCD_KS_STD135)){

      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_S_135))  aOffset=SboML::clamp<int>(aOffset-1,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_A_135))  aOffset=SboML::clamp<int>(aOffset-1,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KLA_125))    aOffset=SboML::clamp<int>(aOffset-1,0,9);

      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_S))   aOffset=SboML::clamp<int>(aOffset+1,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_A))   aOffset=SboML::clamp<int>(aOffset+1,0,7);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_S))       aOffset=SboML::clamp<int>(aOffset+1,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_A))       aOffset=SboML::clamp<int>(aOffset+1,0,7);

    }
    else if(aSourceR == s3(S3UID::RANGE_CCD_KA_STD135)){

      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_S_135))  aOffset=SboML::clamp<int>(aOffset-1,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_A_135))  aOffset=SboML::clamp<int>(aOffset-1,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KLA_125))    aOffset=SboML::clamp<int>(aOffset-1,0,9);

      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_S))   aOffset=SboML::clamp<int>(aOffset+1,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_A))   aOffset=SboML::clamp<int>(aOffset+1,0,7);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_S))       aOffset=SboML::clamp<int>(aOffset+1,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_A))       aOffset=SboML::clamp<int>(aOffset+1,0,7);

    }
    else if(aSourceR == s3(S3UID::RANGE_CCD_KHO_S_135) ||
            aSourceR == s3(S3UID::RANGE_CCD_KHO_A_135) ||
            aSourceR == s3(S3UID::RANGE_CCD_KLA_125)){

      if(aTargetR == s3(S3UID::RANGE_CCD_KS_STD135))    aOffset=SboML::clamp<int>(aOffset+1,0,10);
      if(aTargetR == s3(S3UID::RANGE_CCD_KA_STD135))    aOffset=SboML::clamp<int>(aOffset+1,0,10);

      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_S))   aOffset=SboML::clamp<int>(aOffset+2,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_A))   aOffset=SboML::clamp<int>(aOffset+2,0,7);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_S))       aOffset=SboML::clamp<int>(aOffset+2,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_A))       aOffset=SboML::clamp<int>(aOffset+2,0,7);

    }
    else if(aSourceR == s3(S3UID::RANGE_CCD_STD125_S)){

      if(aTargetR == s3(S3UID::RANGE_CCD_KS_STD135))  aOffset=SboML::clamp<int>(aOffset-1,0,10);
      if(aTargetR == s3(S3UID::RANGE_CCD_KA_STD135))  aOffset=SboML::clamp<int>(aOffset-1,0,10);

      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_S_135))  aOffset=SboML::clamp<int>(aOffset-2,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_A_135))  aOffset=SboML::clamp<int>(aOffset-2,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KLA_125))    aOffset=SboML::clamp<int>(aOffset-2,0,9);

      //if(aTargetR == s3(S3UID::RANGE_CCD_STD125_S))   aOffset=SboML::clamp<int>(aOffset,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_A))   aOffset=SboML::clamp<int>(aOffset,0,7);
      //if(aTargetR == s3(S3UID::RANGE_CCD_SN_S))       aOffset=SboML::clamp<int>(aOffset,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_A))       aOffset=SboML::clamp<int>(aOffset,0,7);

    }
    else if(aSourceR == s3(S3UID::RANGE_CCD_STD125_A)){

      if(aTargetR == s3(S3UID::RANGE_CCD_KS_STD135))  aOffset=SboML::clamp<int>(aOffset-1,0,10);
      if(aTargetR == s3(S3UID::RANGE_CCD_KA_STD135))  aOffset=SboML::clamp<int>(aOffset-1,0,10);

      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_S_135))  aOffset=SboML::clamp<int>(aOffset-2,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_A_135))  aOffset=SboML::clamp<int>(aOffset-2,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KLA_125))    aOffset=SboML::clamp<int>(aOffset-2,0,9);

      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_S))   aOffset=SboML::clamp<int>(aOffset,0,3);
      //if(aTargetR == s3(S3UID::RANGE_CCD_STD125_A))   aOffset=SboML::clamp<int>(aOffset,0,7);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_S))       aOffset=SboML::clamp<int>(aOffset,0,3);
      //if(aTargetR == s3(S3UID::RANGE_CCD_SN_A))       aOffset=SboML::clamp<int>(aOffset,0,7);

    }
    else if(aSourceR == s3(S3UID::RANGE_CCD_SN_S)){

      if(aTargetR == s3(S3UID::RANGE_CCD_KS_STD135))  aOffset=SboML::clamp<int>(aOffset-1,0,10);
      if(aTargetR == s3(S3UID::RANGE_CCD_KA_STD135))  aOffset=SboML::clamp<int>(aOffset-1,0,10);

      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_S_135))  aOffset=SboML::clamp<int>(aOffset-2,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_A_135))  aOffset=SboML::clamp<int>(aOffset-2,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KLA_125))    aOffset=SboML::clamp<int>(aOffset-2,0,9);

      //if(aTargetR == s3(S3UID::RANGE_CCD_STD125_S))   aOffset=SboML::clamp<int>(aOffset,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_A))   aOffset=SboML::clamp<int>(aOffset,0,7);
      //if(aTargetR == s3(S3UID::RANGE_CCD_SN_S))       aOffset=SboML::clamp<int>(aOffset,0,3);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_A))       aOffset=SboML::clamp<int>(aOffset,0,7);

    }
    else if(aSourceR == s3(S3UID::RANGE_CCD_SN_A)){

      if(aTargetR == s3(S3UID::RANGE_CCD_KS_STD135))  aOffset=SboML::clamp<int>(aOffset-1,0,10);
      if(aTargetR == s3(S3UID::RANGE_CCD_KA_STD135))  aOffset=SboML::clamp<int>(aOffset-1,0,10);

      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_S_135))  aOffset=SboML::clamp<int>(aOffset-2,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KHO_A_135))  aOffset=SboML::clamp<int>(aOffset-2,0,9);
      if(aTargetR == s3(S3UID::RANGE_CCD_KLA_125))    aOffset=SboML::clamp<int>(aOffset-2,0,9);

      if(aTargetR == s3(S3UID::RANGE_CCD_STD125_S))   aOffset=SboML::clamp<int>(aOffset,0,3);
      //if(aTargetR == s3(S3UID::RANGE_CCD_STD125_A))   aOffset=SboML::clamp<int>(aOffset,0,7);
      if(aTargetR == s3(S3UID::RANGE_CCD_SN_S))       aOffset=SboML::clamp<int>(aOffset,0,3);
      //if(aTargetR == s3(S3UID::RANGE_CCD_SN_A))       aOffset=SboML::clamp<int>(aOffset,0,7);
    }



    return aOffset;
  }

  inline int getOffset(SboShape3Label aL){
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    const auto lower=s3(lowerS3UID);
    const auto rIdx = getCCDStartIdx(aL);

    return aL.uid() - rIdx - lower.uid();
  }


  inline SboPoint3 getRES_01(SboShape3Label aL) {
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    const auto offset=getOffset(aL);

    if(isCCD_KS_STD135(aL) || isCCD_KA_STD135(aL)){
      if(offset==0) return  SboPoint3(-11.07,0,11.07);
      if(offset==1) return  SboPoint3(-11.57,0,11.57);
      if(offset==2) return  SboPoint3(-12.32,0,12.32);
      if(offset==3) return  SboPoint3(-13.07,0,13.07);
      if(offset==4) return  SboPoint3(-13.8 ,0,13.8 );
      if(offset==5) return  SboPoint3(-14.44,0,14.44);
      if(offset==6) return  SboPoint3(-15.07,0,15.07);
      if(offset==7) return  SboPoint3(-15.82,0,15.82);
      if(offset==8) return  SboPoint3(-16.57,0,16.57);
      if(offset==9) return  SboPoint3(-17.57,0,17.57);
      if(offset==10) return SboPoint3(-18.57,0,18.57);
    }
    else if(isCCD_KHO_S_135(aL) || isCCD_KHO_A_135(aL)){
      if(offset==0) return  SboPoint3(  -15.1,  0,  15.1);
      if(offset==1) return  SboPoint3( -15.85,  0, 15.85);
      if(offset==2) return  SboPoint3(  -16.6,  0,  16.6);
      if(offset==3) return  SboPoint3( -17.35,  0, 17.35);
      if(offset==4) return  SboPoint3( -17.98,  0, 17.98);
      if(offset==5) return  SboPoint3(  -18.6,  0,  18.6);
      if(offset==6) return  SboPoint3( -19.35,  0, 19.35);
      if(offset==7) return  SboPoint3(  -20.1,  0,  20.1);
      if(offset==8) return  SboPoint3(  -21.1,  0,  21.1);
      if(offset==9) return  SboPoint3(  -22.1,  0,  22.1);
    }
    else if(isCCD_KLA_125(aL)){
      if(offset==0) return  SboPoint3( -12.62  ,0,  8.84);
      if(offset==1) return  SboPoint3( -13.37  ,0,  9.36);
      if(offset==2) return  SboPoint3( -14.12  ,0,  9.89);
      if(offset==3) return  SboPoint3( -14.86  ,0,  10.4);
      if(offset==4) return  SboPoint3(  -15.5  ,0, 10.85);
      if(offset==5) return  SboPoint3( -16.12  ,0, 11.29);
      if(offset==6) return  SboPoint3( -16.87  ,0, 11.81);
      if(offset==7) return  SboPoint3( -17.62  ,0, 12.34);
      if(offset==8) return  SboPoint3( -18.58  ,0, 13.01);
      if(offset==9) return  SboPoint3( -19.59  ,0, 13.72);
    }
    else if(isCCD_STD125_S(aL)){
      if(offset==0) return  SboPoint3(  -8.76,  0 , 6.13 );
      if(offset==1) return  SboPoint3(  -9.26 , 0 , 6.48 );
      if(offset==2) return  SboPoint3(  -9.76 , 0 , 6.83 );
      if(offset==3) return  SboPoint3( -10.51 , 0 , 7.36 );
    }
    else if(isCCD_STD125_A(aL)){
      if(offset==0) return  SboPoint3(    -8.76 , 0 , 6.13);
      if(offset==1) return  SboPoint3(    -9.26 , 0 , 6.48);
      if(offset==2) return  SboPoint3(    -9.76 , 0 , 6.83);
      if(offset==3) return  SboPoint3(   -10.51 , 0 , 7.36);
      if(offset==4) return  SboPoint3(   -11.26 , 0 , 7.88);
      if(offset==5) return  SboPoint3(   -12.01 , 0 , 8.41);
      if(offset==6) return  SboPoint3(   -12.63 , 0 , 8.84);
      if(offset==7) return  SboPoint3(   -13.26 , 0 , 9.28);
    }
    else if(isCCD_SN_S(aL)){
      if(offset==0) return  SboPoint3( -10.22 , 0 , 10.22 );
      if(offset==1) return  SboPoint3( -10.71 , 0 , 10.71 );
      if(offset==2) return  SboPoint3( -11.21 , 0 , 11.21 );
      if(offset==3) return  SboPoint3( -11.96 , 0 , 11.96 );
    }
    else if(isCCD_SN_A(aL)){
      if(offset==0) return  SboPoint3(  -10.21 , 0 , 10.21);
      if(offset==1) return  SboPoint3(  -10.71 , 0 , 10.71);
      if(offset==2) return  SboPoint3(  -11.21 , 0 , 11.21);
      if(offset==3) return  SboPoint3(  -11.96 , 0 , 11.96);
      if(offset==4) return  SboPoint3(  -12.71 , 0 , 12.71);
      if(offset==5) return  SboPoint3(  -13.46 , 0 , 13.46);
      if(offset==6) return  SboPoint3(  -14.09 , 0 , 14.09);
      if(offset==7) return  SboPoint3(  -14.71 , 0 , 14.71);
    }



    return SboPoint3(0,0,0);
  }


  inline SboPoint3 getRES_02(SboShape3Label aL) {
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    const auto offset=getOffset(aL);

    if(isCCD_KS_STD135(aL) || isCCD_KA_STD135(aL)){
      if(offset==0) return  SboPoint3( -19.5, 0,  2.64);
      if(offset==1) return  SboPoint3(   -20, 0,  3.14);
      if(offset==2) return  SboPoint3(-20.75, 0,  3.89);
      if(offset==3) return  SboPoint3( -21.5, 0,  4.64);
      if(offset==4) return  SboPoint3(-22.25, 0,  5.36);
      if(offset==5) return  SboPoint3(-22.87, 0,  6.01);
      if(offset==6) return  SboPoint3( -23.5, 0,  6.64);
      if(offset==7) return  SboPoint3(-24.25, 0,  7.39);
      if(offset==8) return  SboPoint3(   -25, 0,  8.14);
      if(offset==9) return  SboPoint3(   -26, 0,  9.14);
      if(offset==10) return SboPoint3(   -27, 0, 10.14);
    }
    else if(isCCD_KHO_S_135(aL) || isCCD_KHO_A_135(aL)){
      if(offset==0) return  SboPoint3(   -20 ,0, 10.21 );
      if(offset==1) return  SboPoint3(-20.75 ,0, 10.96 );
      if(offset==2) return  SboPoint3( -21.5 ,0, 11.71 );
      if(offset==3) return  SboPoint3(-22.25 ,0, 12.46 );
      if(offset==4) return  SboPoint3(-22.87 ,0, 13.08 );
      if(offset==5) return  SboPoint3( -23.5 ,0, 13.71 );
      if(offset==6) return  SboPoint3(-24.25 ,0, 14.46 );
      if(offset==7) return  SboPoint3(   -25 ,0, 15.21 );
      if(offset==8) return  SboPoint3(   -26 ,0, 16.21 );
      if(offset==9) return  SboPoint3(   -27 ,0, 17.21 );
    }
    else if(isCCD_KLA_125(aL)){
      if(offset==0) return  SboPoint3(-19.99, 0, 1.46 );
      if(offset==1) return  SboPoint3(-20.74, 0, 1.99 );
      if(offset==2) return  SboPoint3( -21.5, 0, 2.51 );
      if(offset==3) return  SboPoint3(-22.26, 0,    3 );
      if(offset==4) return  SboPoint3(-22.88, 0, 3.47 );
      if(offset==5) return  SboPoint3(-23.49, 0, 3.92 );
      if(offset==6) return  SboPoint3(-24.21, 0, 4.47 );
      if(offset==7) return  SboPoint3(-24.96, 0, 5.01 );
      if(offset==8) return  SboPoint3(-25.85, 0, 5.74 );
      if(offset==9) return  SboPoint3(-26.78, 0, 6.53 );
    }
    else if(isCCD_STD125_S(aL)){
      if(offset==0) return  SboPoint3(    -19,  0 , -4.11 );
      if(offset==1) return  SboPoint3(  -19.5 , 0 , -3.76 );
      if(offset==2) return  SboPoint3(    -20 , 0 , -3.41 );
      if(offset==3) return  SboPoint3( -20.75 , 0 , -2.89 );
    }
    else if(isCCD_STD125_A(aL)){
      if(offset==0) return  SboPoint3(     -19 , 0 , -4.11);
      if(offset==1) return  SboPoint3(   -19.5 , 0 , -3.76);
      if(offset==2) return  SboPoint3(     -20 , 0 , -3.41);
      if(offset==3) return  SboPoint3(  -20.75 , 0 , -2.89);
      if(offset==4) return  SboPoint3(   -21.5 , 0 , -2.36);
      if(offset==5) return  SboPoint3(  -22.25 , 0 , -1.84);
      if(offset==6) return  SboPoint3(  -22.87 , 0 ,  -1.4);
      if(offset==7) return  SboPoint3(   -23.5 , 0 , -0.96);
    }
    else if(isCCD_SN_S(aL)){
      if(offset==0) return  SboPoint3(     -19 , 0 , 1.43);
      if(offset==1) return  SboPoint3(   -19.5 , 0 , 1.93);
      if(offset==2) return  SboPoint3(     -20 , 0 , 2.43);
      if(offset==3) return  SboPoint3(  -20.75 , 0 , 3.18);
    }
    else if(isCCD_SN_A(aL)){
      if(offset==0) return  SboPoint3(      -19 , 0 , 1.43);
      if(offset==1) return  SboPoint3(    -19.5 , 0 , 1.93);
      if(offset==2) return  SboPoint3(      -20 , 0 , 2.43);
      if(offset==3) return  SboPoint3(   -20.75 , 0 , 3.18);
      if(offset==4) return  SboPoint3(    -21.5 , 0 , 3.93);
      if(offset==5) return  SboPoint3(   -22.25 , 0 , 4.68);
      if(offset==6) return  SboPoint3(   -22.87 , 0 ,  5.3);
      if(offset==7) return  SboPoint3(    -23.5 , 0 , 5.93);
    }

    return SboPoint3(0,0,0);
  }


  inline SboPoint3 getTPR_01(SboShape3Label aL) {
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    const auto offset=getOffset(aL);

    if(isCCD_KS_STD135(aL) || isCCD_KA_STD135(aL)){
      if(offset==0) return  SboPoint3(-38.29,  0, 38.29);
      if(offset==1) return  SboPoint3(-38.79,  0, 38.79);
      if(offset==2) return  SboPoint3(-39.54,  0, 39.54);
      if(offset==3) return  SboPoint3(-40.29,  0, 40.29);
      if(offset==4) return  SboPoint3(-41.03,  0, 41.03);
      if(offset==5) return  SboPoint3(-41.67,  0, 41.67);
      if(offset==6) return  SboPoint3(-42.29,  0, 42.29);
      if(offset==7) return  SboPoint3(-43.04,  0, 43.04);
      if(offset==8) return  SboPoint3(-43.79,  0, 43.79);
      if(offset==9) return  SboPoint3(-44.78,  0, 44.78);
      if(offset==10) return SboPoint3(-45.79,  0, 45.79);
    }
    else if(isCCD_KHO_S_135(aL) || isCCD_KHO_A_135(aL)){
      if(offset==0) return  SboPoint3(-45.65, 0, 45.65);
      if(offset==1) return  SboPoint3( -46.4, 0,  46.4);
      if(offset==2) return  SboPoint3(-47.15, 0, 47.15);
      if(offset==3) return  SboPoint3( -47.9, 0,  47.9);
      if(offset==4) return  SboPoint3(-48.53, 0, 48.53);
      if(offset==5) return  SboPoint3(-49.15, 0, 49.15);
      if(offset==6) return  SboPoint3( -49.9, 0,  49.9);
      if(offset==7) return  SboPoint3(-50.65, 0, 50.65);
      if(offset==8) return  SboPoint3(-51.83, 0, 51.83);
      if(offset==9) return  SboPoint3(-52.86, 0, 52.86);
    }
    else if(isCCD_KLA_125(aL)){
      if(offset==0) return  SboPoint3(-45.59 ,0, 31.92);
      if(offset==1) return  SboPoint3(-46.35 ,0, 32.45);
      if(offset==2) return  SboPoint3(-47.09 ,0, 32.98);
      if(offset==3) return  SboPoint3(-47.83 ,0, 33.49);
      if(offset==4) return  SboPoint3(-48.46 ,0, 33.93);
      if(offset==5) return  SboPoint3(-49.08 ,0, 34.37);
      if(offset==6) return  SboPoint3(-49.83 ,0, 34.89);
      if(offset==7) return  SboPoint3(-50.58 ,0, 35.41);
      if(offset==8) return  SboPoint3(-51.78 ,0, 36.26);
      if(offset==9) return  SboPoint3(-52.79 ,0, 36.97);
    }
    else if(isCCD_STD125_S(aL)){
      if(offset==0) return  SboPoint3(  -37.87,  0 , 26.52);
      if(offset==1) return  SboPoint3(  -38.37 , 0 , 26.87);
      if(offset==2) return  SboPoint3(  -38.87 , 0 , 27.22);
      if(offset==3) return  SboPoint3(  -39.62 , 0 , 27.74);
    }
    else if(isCCD_STD125_A(aL)){
      if(offset==0) return  SboPoint3(  -37.87 , 0 , 26.52);
      if(offset==1) return  SboPoint3(  -38.37 , 0 , 26.87);
      if(offset==2) return  SboPoint3(  -38.87 , 0 , 27.22);
      if(offset==3) return  SboPoint3(  -39.62 , 0 , 27.74);
      if(offset==4) return  SboPoint3(  -40.37 , 0 , 28.27);
      if(offset==5) return  SboPoint3(  -41.12 , 0 , 28.79);
      if(offset==6) return  SboPoint3(  -41.74 , 0 , 29.23);
      if(offset==7) return  SboPoint3(  -42.37 , 0 , 29.67);
    }
    else if(isCCD_SN_S(aL)){
      if(offset==0) return  SboPoint3(  -32.49 , 0 , 32.49);
      if(offset==1) return  SboPoint3(  -32.99 , 0 , 32.99);
      if(offset==2) return  SboPoint3(  -33.49 , 0 , 33.49);
      if(offset==3) return  SboPoint3(  -34.24 , 0 , 34.24);
    }
    else if(isCCD_SN_A(aL)){
      if(offset==0) return  SboPoint3(  -32.49 , 0 , 32.49);
      if(offset==1) return  SboPoint3(  -32.99 , 0 , 32.99);
      if(offset==2) return  SboPoint3(  -33.49 , 0 , 33.49);
      if(offset==3) return  SboPoint3(  -34.24 , 0 , 34.24);
      if(offset==4) return  SboPoint3(  -34.99 , 0 , 34.99);
      if(offset==5) return  SboPoint3(  -35.74 , 0 , 35.74);
      if(offset==6) return  SboPoint3(  -36.36 , 0 , 36.36);
      if(offset==7) return  SboPoint3(  -36.99 , 0 , 36.99);
    }

    return SboPoint3(0,0,0);
  }

  inline float getShaftAngle(SboShape3Label aL){
    HPROJ_DCHECK2(isStem(aL),"must be aStem");

    if(isCCD_KLA_125(aL))   return 55.f;

    return 45.f;
  }



};



int SboCorail::rev() const
{
  return 1;
}

QString SboCorail::productName() const
{
  return XXXStem::ProductName;
}

QString SboCorail::companyName() const
{
  return XXXStem::CompanyName;
}

QString SboCorail::message(int,const SboFemImplantConfig&) const
{
  return "Corail implant system";
}

QString SboCorail::setMeshInfoSearchPath(QString aPath)
{
  using namespace XXXStem;

  //http://doc.qt.io/qt-5/qdir.html#setSearchPaths
  //Load resource from the system file
  QString myRcc;
  if(meshInfoResourceFromRcc(myRcc))
    QDir::setSearchPaths(RCCIdName, QStringList(QString(":") + RCCPath));
  else {
    //meshes are loaded from the disk
    //qDebug() << aPath + RCCPath + "/KS_STD135";
    //See also MeshInfoCollection::addCRef()
    QDir::setSearchPaths(RCCIdName, {aPath + RCCPath + "/KS_STD135",
                                     aPath + RCCPath + "/KA_STD135",
                                     aPath + RCCPath + "/KHOS_135",
                                     aPath + RCCPath + "/KHOA_135",
                                     aPath + RCCPath + "/KLA_125",
                                     aPath + RCCPath + "/STD125_S",
                                     aPath + RCCPath + "/STD125_A",
                                     aPath + RCCPath + "/SNS_135",
                                     aPath + RCCPath + "/SNA_135"
      });
  }

  return {};
}

bool SboCorail::meshInfoResourceFromRcc(QString& aRcc)
{
  aRcc=XXXStem::RCCFileName;
  return false;
}

bool SboCorail::meshInfoResourceFromFileSystem()
{
  return true;
}


void SboCorail::meshInfoRCList(SboMeshInfoRCList& rcList)
{
  using namespace XXXStem;
  auto next=[&](S3UID e,QString s,QString aRCCId) { rcList.push_back({s3(e),aRCCId + QString(":") + s + ".wrl"});};

  next(S3UID::STEM_KS_STD135_0, "103427643_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_1, "103427644_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_2, "103427646_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_3, "103427648_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_4, "103427649_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_5, "103427650_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_6, "103427651_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_7, "103427652_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_8, "103427653_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_9, "103427654_1",RCCIdName);
  next(S3UID::STEM_KS_STD135_10,"103427657_1",RCCIdName);

  next(S3UID::STEM_KA_STD135_0, "103414240_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_1, "103414964_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_2, "103414966_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_3, "103414967_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_4, "103414968_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_5, "103414969_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_6, "103414970_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_7, "103414971_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_8, "103427630_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_9, "103427639_1",RCCIdName);
  next(S3UID::STEM_KA_STD135_10,"103427658_1",RCCIdName);

  next(S3UID::STEM_KHO_S_135_0, "103607083_1",RCCIdName);
  next(S3UID::STEM_KHO_S_135_1, "103607086_1",RCCIdName);
  next(S3UID::STEM_KHO_S_135_2, "103607087_1",RCCIdName);
  next(S3UID::STEM_KHO_S_135_3, "103607088_1",RCCIdName);
  next(S3UID::STEM_KHO_S_135_4, "103607091_1",RCCIdName);
  next(S3UID::STEM_KHO_S_135_5, "103607092_1",RCCIdName);
  next(S3UID::STEM_KHO_S_135_6, "103607093_1",RCCIdName);
  next(S3UID::STEM_KHO_S_135_7, "103607094_1",RCCIdName);
  next(S3UID::STEM_KHO_S_135_8, "103607095_1",RCCIdName);
  next(S3UID::STEM_KHO_S_135_9, "103607099_1",RCCIdName);

  next(S3UID::STEM_KHO_A_135_0, "103550471_1",RCCIdName);
  next(S3UID::STEM_KHO_A_135_1, "103550472_1",RCCIdName);
  next(S3UID::STEM_KHO_A_135_2, "103550473_1",RCCIdName);
  next(S3UID::STEM_KHO_A_135_3, "103550474_1",RCCIdName);
  next(S3UID::STEM_KHO_A_135_4, "103550475_1",RCCIdName);
  next(S3UID::STEM_KHO_A_135_5, "103550476_1",RCCIdName);
  next(S3UID::STEM_KHO_A_135_6, "103550477_1",RCCIdName);
  next(S3UID::STEM_KHO_A_135_7, "103550478_1",RCCIdName);
  next(S3UID::STEM_KHO_A_135_8, "103550481_1",RCCIdName);
  next(S3UID::STEM_KHO_A_135_9, "103550482_1",RCCIdName);


  next(S3UID::STEM_KLA_125_0, "103610427_1",RCCIdName);
  next(S3UID::STEM_KLA_125_1, "103610428_1",RCCIdName);
  next(S3UID::STEM_KLA_125_2, "103610429_1",RCCIdName);
  next(S3UID::STEM_KLA_125_3, "103610430_1",RCCIdName);
  next(S3UID::STEM_KLA_125_4, "103610431_1",RCCIdName);
  next(S3UID::STEM_KLA_125_5, "103610432_1",RCCIdName);
  next(S3UID::STEM_KLA_125_6, "103610433_1",RCCIdName);
  next(S3UID::STEM_KLA_125_7, "103610434_1",RCCIdName);
  next(S3UID::STEM_KLA_125_8, "103610435_1",RCCIdName);
  next(S3UID::STEM_KLA_125_9, "103610436_1",RCCIdName);

  next(S3UID::STEM_STD125_S_0, "103548905_1",RCCIdName);
  next(S3UID::STEM_STD125_S_1, "103550468_1",RCCIdName);
  next(S3UID::STEM_STD125_S_2, "103550469_1",RCCIdName);
  next(S3UID::STEM_STD125_S_3, "103550470_1",RCCIdName);

  next(S3UID::STEM_STD125_A_0, "103548903_1",RCCIdName);
  next(S3UID::STEM_STD125_A_1, "103550462_1",RCCIdName);
  next(S3UID::STEM_STD125_A_2, "103550463_1",RCCIdName);
  next(S3UID::STEM_STD125_A_3, "103550464_1",RCCIdName);
  next(S3UID::STEM_STD125_A_4, "103550908_1",RCCIdName);
  next(S3UID::STEM_STD125_A_5, "103550915_1",RCCIdName);
  next(S3UID::STEM_STD125_A_6, "103550917_1",RCCIdName);
  next(S3UID::STEM_STD125_A_7, "103550918_1",RCCIdName);

  next(S3UID::STEM_SN_S_0, "103548906_1",RCCIdName);
  next(S3UID::STEM_SN_S_1, "103550465_1",RCCIdName);
  next(S3UID::STEM_SN_S_2, "103550466_1",RCCIdName);
  next(S3UID::STEM_SN_S_3, "103550467_1",RCCIdName);

  next(S3UID::STEM_SN_A_0, "103548904_1",RCCIdName);
  next(S3UID::STEM_SN_A_1, "103550459_1",RCCIdName);
  next(S3UID::STEM_SN_A_2, "103550460_1",RCCIdName);
  next(S3UID::STEM_SN_A_3, "103550461_1",RCCIdName);
  next(S3UID::STEM_SN_A_4, "103550919_1",RCCIdName);
  next(S3UID::STEM_SN_A_5, "103550920_1",RCCIdName);
  next(S3UID::STEM_SN_A_6, "103550921_1",RCCIdName);
  next(S3UID::STEM_SN_A_7, "103550922_1",RCCIdName);

}


void SboCorail::parts(SboTPCatalogList& prodList)
{
  using namespace XXXStem;

  auto stemRange= new SboTPCPartMonoStem(productName(),SboAnatomLocation::None);
  stemRange->_iconSet=PartIcon;
  stemRange->_menuText=PartMenuText;
  stemRange->_tooltipText=PartTooltipText;
  stemRange->setDefaultLabel(s3(defaultS3StemRUID));


  struct CCD_CORAIL : public SboTPCPartMonoStem::CCD {

    virtual RT range(SboShape3Label l) const override {
      if(isCCD_KS_STD135(l)) return _rKS_STD135;
      if(isCCD_KA_STD135(l)) return _rKA_STD135;

      if(isCCD_KHO_S_135(l)) return _rKHO_S_135;
      if(isCCD_KHO_A_135(l)) return _rKHO_A_135;

      if(isCCD_KLA_125(l))   return _rKLA_125;

      if(isCCD_STD125_S(l))   return _rSTD125_S;
      if(isCCD_STD125_A(l))   return _rSTD125_A;
      if(isCCD_SN_S(l))   return _rSN_S;
      if(isCCD_SN_A(l))   return _rSN_A;

      HPROJ_DCHECK(!"range returns a null label");
      return {};
    }

    virtual SboShape3Label similarLabel(SboShape3Label aL, SboShape3Label aNextCCDRange) const{
      const auto v=ranges();
      const auto itCurrR=std::find_if(v.cbegin(),v.cend(),[&](const RT& x) { return x.label == getCCDRange(aL); });
      const auto itNextR=std::find_if(v.cbegin(),v.cend(),[&](const RT& x) { return x.label == aNextCCDRange; });

      const auto lower=s3(lowerS3UID);

      auto offset=getOffset(aL);
      offset=getSimilarOffset(offset,itCurrR->label,itNextR->label);
      return lower.next(offset + itNextR->startIdx);
    }

    //0 follow neck origin
    //1 keep transform
    virtual int strategy(SboShape3Label /*nextLabel*/, SboShape3Label /*currLabel*/) const {
      HPROJ_DCHECK(!"strategy should never be called in rev 1");
      return 0;
    }

    //no collar
    // std::vector<RT> ranges() const override {
    //   return {_rKS_STD135,_rKHO_S_135,_rKLA_125,_rSTD125_S,_rSTD125_A,_rSN_S,_rSN_A};
    // }

    //all
    std::vector<RT> ranges() const override {
      return {_rKS_STD135,_rKA_STD135,_rKHO_S_135,_rKHO_A_135,_rKLA_125,_rSTD125_S,_rSTD125_A,_rSN_S,_rSN_A};
    }


    const RT _rKS_STD135={10,  20,  s3(XXXStem::S3UID::RANGE_CCD_KS_STD135),"135 STD"};
    const RT _rKA_STD135={21,  31,  s3(XXXStem::S3UID::RANGE_CCD_KA_STD135),"135 STD COLLAR"};

    const RT _rKHO_S_135={32, 41,  s3(XXXStem::S3UID::RANGE_CCD_KHO_S_135),"135 KHO"};
    const RT _rKHO_A_135={0, 9,  s3(XXXStem::S3UID::RANGE_CCD_KHO_A_135),"135 KHO COLLAR"};

    const RT _rKLA_125=  {42, 51,  s3(XXXStem::S3UID::RANGE_CCD_KLA_125),  "125 KLA"};

    const RT _rSTD125_S= {52, 55,  s3(XXXStem::S3UID::RANGE_CCD_STD125_S), "125 STD"};
    const RT _rSTD125_A= {56, 63,  s3(XXXStem::S3UID::RANGE_CCD_STD125_A), "125 STD COLLAR"};

    const RT _rSN_S= {64, 67,  s3(XXXStem::S3UID::RANGE_CCD_SN_S), "135 SN"};
    const RT _rSN_A= {68, 75,  s3(XXXStem::S3UID::RANGE_CCD_SN_A), "135 SN COLLAR"};


  };

  stemRange->_CCDPart = std::make_unique<CCD_CORAIL>();


  auto next=[&](S3UID e,QString s) { stemRange->push_back(new SboTPCatalogItem(stemRange,s3(e), ItemName,s));};


  //NOTE: see the brochure to get the sizing convention
  next(S3UID::STEM_KS_STD135_0, "KS 135° 8");
  next(S3UID::STEM_KS_STD135_1, "KS 135° 9");
  next(S3UID::STEM_KS_STD135_2, "KS 135° 10");
  next(S3UID::STEM_KS_STD135_3, "KS 135° 11");
  next(S3UID::STEM_KS_STD135_4, "KS 135° 12");
  next(S3UID::STEM_KS_STD135_5, "KS 135° 13");
  next(S3UID::STEM_KS_STD135_6, "KS 135° 14");
  next(S3UID::STEM_KS_STD135_7, "KS 135° 15");
  next(S3UID::STEM_KS_STD135_8, "KS 135° 16");
  next(S3UID::STEM_KS_STD135_9, "KS 135° 18");
  next(S3UID::STEM_KS_STD135_10,"KS 135° 20");

  next(S3UID::STEM_KA_STD135_0, "KA 135° 8");
  next(S3UID::STEM_KA_STD135_1, "KA 135° 9");
  next(S3UID::STEM_KA_STD135_2, "KA 135° 10");
  next(S3UID::STEM_KA_STD135_3, "KA 135° 11");
  next(S3UID::STEM_KA_STD135_4, "KA 135° 12");
  next(S3UID::STEM_KA_STD135_5, "KA 135° 13");
  next(S3UID::STEM_KA_STD135_6, "KA 135° 14");
  next(S3UID::STEM_KA_STD135_7, "KA 135° 15");
  next(S3UID::STEM_KA_STD135_8, "KA 135° 16");
  next(S3UID::STEM_KA_STD135_9, "KA 135° 18");
  next(S3UID::STEM_KA_STD135_10,"KA 135° 20");

  next(S3UID::STEM_KHO_S_135_0, "KHO S 135° 9");
  next(S3UID::STEM_KHO_S_135_1, "KHO S 135° 10");
  next(S3UID::STEM_KHO_S_135_2, "KHO S 135° 11");
  next(S3UID::STEM_KHO_S_135_3, "KHO S 135° 12");
  next(S3UID::STEM_KHO_S_135_4, "KHO S 135° 13");
  next(S3UID::STEM_KHO_S_135_5, "KHO S 135° 14");
  next(S3UID::STEM_KHO_S_135_6, "KHO S 135° 15");
  next(S3UID::STEM_KHO_S_135_7, "KHO S 135° 16");
  next(S3UID::STEM_KHO_S_135_8, "KHO S 135° 18");
  next(S3UID::STEM_KHO_S_135_9, "KHO S 135° 20");

  next(S3UID::STEM_KHO_A_135_0, "KHO A 135° 9");
  next(S3UID::STEM_KHO_A_135_1, "KHO A 135° 10");
  next(S3UID::STEM_KHO_A_135_2, "KHO A 135° 11");
  next(S3UID::STEM_KHO_A_135_3, "KHO A 135° 12");
  next(S3UID::STEM_KHO_A_135_4, "KHO A 135° 13");
  next(S3UID::STEM_KHO_A_135_5, "KHO A 135° 14");
  next(S3UID::STEM_KHO_A_135_6, "KHO A 135° 15");
  next(S3UID::STEM_KHO_A_135_7, "KHO A 135° 16");
  next(S3UID::STEM_KHO_A_135_8, "KHO A 135° 18");
  next(S3UID::STEM_KHO_A_135_9, "KHO A 135° 20");

  next(S3UID::STEM_KLA_125_0, "KLA 125° 9");
  next(S3UID::STEM_KLA_125_1, "KLA 125° 10");
  next(S3UID::STEM_KLA_125_2, "KLA 125° 11");
  next(S3UID::STEM_KLA_125_3, "KLA 125° 12");
  next(S3UID::STEM_KLA_125_4, "KLA 125° 13");
  next(S3UID::STEM_KLA_125_5, "KLA 125° 14");
  next(S3UID::STEM_KLA_125_6, "KLA 125° 15");
  next(S3UID::STEM_KLA_125_7, "KLA 125° 16");
  next(S3UID::STEM_KLA_125_8, "KLA 125° 18");
  next(S3UID::STEM_KLA_125_9, "KLA 125° 20");

  next(S3UID::STEM_STD125_S_0, "STD S 125° 7");
  next(S3UID::STEM_STD125_S_1, "STD S 125° 8");
  next(S3UID::STEM_STD125_S_2, "STD S 125° 9");
  next(S3UID::STEM_STD125_S_3, "STD S 125° 10");

  next(S3UID::STEM_STD125_A_0, "STD A 125° 7");
  next(S3UID::STEM_STD125_A_1, "STD A 125° 8");
  next(S3UID::STEM_STD125_A_2, "STD A 125° 9");
  next(S3UID::STEM_STD125_A_3, "STD A 125° 10");
  next(S3UID::STEM_STD125_A_4, "STD A 125° 11");
  next(S3UID::STEM_STD125_A_5, "STD A 125° 12");
  next(S3UID::STEM_STD125_A_6, "STD A 125° 13");
  next(S3UID::STEM_STD125_A_7, "STD A 125° 14");

  next(S3UID::STEM_SN_S_0, "SN S 135° 7");
  next(S3UID::STEM_SN_S_1, "SN S 135° 8");
  next(S3UID::STEM_SN_S_2, "SN S 135° 9");
  next(S3UID::STEM_SN_S_3, "SN S 135° 10");

  next(S3UID::STEM_SN_A_0, "SN A 135° 7");
  next(S3UID::STEM_SN_A_1, "SN A 135° 8");
  next(S3UID::STEM_SN_A_2, "SN A 135° 9");
  next(S3UID::STEM_SN_A_3, "SN A 135° 10");
  next(S3UID::STEM_SN_A_4, "SN A 135° 11");
  next(S3UID::STEM_SN_A_5, "SN A 135° 12");
  next(S3UID::STEM_SN_A_6, "SN A 135° 13");
  next(S3UID::STEM_SN_A_7, "SN A 135° 14");


  prodList.push_back(stemRange);

  //NOTE: Last argument S3UID::HEAD_P4 locates the CONE Lateral tip.
  //NOTE: The default label must be different from HEAD_P4 to be able to compute the cone axis.
  auto headRange= new SboTPCPartHead(productName(),s3(S3UID::HEAD_P4));
  headRange->_iconSet=PartHeadIcon;
  headRange->_menuText=PartHeadMenuText;
  headRange->_tooltipText=PartHeadTooltipText;
  headRange->setDefaultLabel(s3(defaultS3HeadUID));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_M4),"Head","+1.5"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P0),"Head","+5.0"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P4),"Head","+8.5"));
  headRange->push_back(new SboTPCatalogItem(headRange,s3(S3UID::HEAD_P8),"Head","+12"));

  prodList.push_back(headRange);

  auto cutPlaneRange= new SboTPCPartCutPlane(productName());
  cutPlaneRange->setDefaultLabel(s3(S3UID::CUTPLANE));
  cutPlaneRange->push_back(new SboTPCatalogItem(cutPlaneRange,s3(S3UID::CUTPLANE),"Cutplane"));

  prodList.push_back(cutPlaneRange);

}


bool SboCorail::inRange(SboShape3Label aL)
{
  using namespace XXXStem;
  return SboML::in_closed_range<SboShape3Label>(aL,s3(lowerS3UID),s3(upperS3UID));
}

SboMatrix3 SboCorail::headToNeckMatrix(SboShape3Label aHeadLabel, SboShape3Label aNeckLabel)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aHeadLabel);
  HPROJ_UNUSED(aNeckLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboCorail::neckToStemMatrix(SboShape3Label aNeckLabel, SboShape3Label aStemLabel, SboAnatomLocation aSide)
{
  //NOTE: Only for modular neck stem

  HPROJ_UNUSED(aNeckLabel);
  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;
  return SboML::idMat3();
}

SboMatrix3 SboCorail::headToStemMatrix(SboShape3Label aHeadLabel, SboShape3Label aStemLabel)
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

  float l=0;
  if(aHeadLabel == s3(S3UID::HEAD_M4)) l=-3.5;
  else if(aHeadLabel == s3(S3UID::HEAD_P4)) l=3.5;
  else if(aHeadLabel == s3(S3UID::HEAD_P8)) l=7.0;

  auto m=SboML::transMat3(headO + neckAxis * l);

  return m;

}


SboPlane3 SboCorail::cutPlane(SboShape3Label aStemLabel)
{
  //return the cutplane equation in CPT_FRAME

  //The cutplane is used to position the component in WORD_CS (STD_FRAME)

  //Default plane position and orientation: centered at (0,0,0) with normal (0,1,0)
  //Should return something like Plane3(Point3(0,0,0),Vector3(0,1,0)).transform(m)
  //Compute the TRAFFFO m

  //FIXME: Plane3 origin is supposed to be the neck origin (RES_01)

  using namespace XXXStem;

  const auto neckO=getRES_01(aStemLabel);
  const auto alpha=45.f; //fem axis cutplane angle (not related to angle shaft angle)

  const auto m=
    SboML::transMat3(neckO) * SboML::rotMatY3(SboML::deg2Rad<float>(-alpha)) * SboML::rotMatX3(SboML::deg2Rad<float>(90.0f));

  //transform the plane
  const auto plane=SboPlane3(SboPoint3(0,0,0), SboVector3(0,1,0)).transform(m);

  //in case of collar adjust the cutPlane to be well aligned with the R line
  return hasCollar(aStemLabel) ?  SboML::offset(plane,-0.1f): plane;
}

SboBbox3 SboCorail::cutPlaneBbox(SboShape3Label aStemLabel)
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

  auto neckO=SboPoint3(0,0,0);
  auto m=SboML::transMat3(neckO);

  pmin=m(pmin);
  pmax=m(pmax);

  return SboML::makeBbox3(pmin,pmax);
}

SboMatrix3 SboCorail::stemToStemMatrix(const SboFemImplantConfig& aOriginFemIC,const SboFemImplantConfig& aTargetFemIC)
{
  //NOTE: return the local TRAFFO that transforms from aOriginStemLabel to aTargetStemLabel in CPT_FRAME
  //LINK: [[hdoch:capture-hproj-implants.org::REV_STEMTOSTEM]]

  using namespace XXXStem;

  // auto neckO =getRES_01(aOriginFemIC.stemLabel());
  // auto neckTO=getRES_01(aTargetFemIC.stemLabel());

  //RES_02 is the Rpoint on the stem. Align RES_02
  auto neck2 =getRES_02(aOriginFemIC.stemLabel());
  auto neckT2=getRES_02(aTargetFemIC.stemLabel());

  return SboML::transMat3(neck2 - neckT2);
}

SboMatrix3 SboCorail::normalTrf(SboShape3Label aStemLabel, const SboPlane3 & aP3, const SboPoint3 & aO3)
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

  return SboML::rotMatZ3(SboML::deg2Rad<float>(180.0f));
}

SboVector3 SboCorail::offsetFF(SboShape3Label aStemLabel)
{

  // independently of the side (left or right)
  // x > 0 cpt moves medially
  // y > 0 cpt moves posteriorly
  // z > 0 cpt moves superiorly

  HPROJ_UNUSED(aStemLabel);
  using namespace XXXStem;

  //in COMPONENT frame adjust to aline femAxs with FF
  const auto neckO=getRES_01(aStemLabel);
  const auto femAxs=SboPoint3(0,0,-25.f);

  //go to NORMAL frame
  auto m=SboML::rotMatZ3(SboML::deg2Rad<float>(180.0f));
  auto d=m(neckO-femAxs);
  return {d.x(),0.f,0.f};
}


SboFemImplantConfig SboCorail::defaultFemIC(QString aPartName,SboAnatomLocation aRequestedSide)
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

SboFemImplantConfig SboCorail::fillAndValidAssembly(const SboFemImplantConfig& aFemIC)
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

SboFemImplantConfig SboCorail::nextPrev(const SboFemImplantConfig& aFemIC,bool aNext)
{
  using namespace XXXStem;

  auto fc=aFemIC;
  fc.setStemLabel(nextPrevStem(fc.stemLabel(),aNext));

  //NOTE: Don't check whether the config is a valid assembly or combination, let the application do it

  return fc;
}

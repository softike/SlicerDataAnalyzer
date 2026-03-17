/*=========================================================================
  Program: HPROJECT
  Copyright (c) Ernesto Durante, Julien de Siebenthal
  All rights reserved.
  See Copyright.txt for details.
  =========================================================================*/

#pragma once

#include "SboShape3UID.h"

#ifdef Q_CC_MSVC
//https://docs.microsoft.com/en-us/cpp/error-messages/compiler-warnings/compiler-warning-level-4-c4062?view=msvc-170
//https://brevzin.github.io/c++/2019/08/01/enums-default/
#pragma warning(1 : 4062)
#endif

HPROJ_BEGIN_NAMESPACE

namespace MDCA {

  enum Product { QUADRA,
                 VERSAFITCUPCCTRIO,
                 AMISTEM,
                 MINIMAX };

  const constexpr SboShape3UID companyRangeStartsAt = 100000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 130000L;
  const constexpr char* companyName                 = "MDCA";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch (aP) {
      case Product::QUADRA: return companyRangeStartsAt + 0L;
      case Product::VERSAFITCUPCCTRIO: return companyRangeStartsAt + 500L;
      case Product::AMISTEM: return companyRangeStartsAt + 750L;
      case Product::MINIMAX: return companyRangeStartsAt + 1250L;
    };
    return 0;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch (aP) {
      case Product::QUADRA: return "MDCA QUADRA";
      case Product::VERSAFITCUPCCTRIO: return "MDCA VERSAFITCUP CC TRIO";
      case Product::AMISTEM: return "MDCA AMIStem";
      case Product::MINIMAX: return "MDCA MiniMAX";
    };
    return {};
  }

  //NOTE: From Qt doc, valid names for rcc id can contain only letters & numbers
  //NOTE: Because each RCCId name must be unique, concatenate CompanyName & ProductName
  inline constexpr const char* RCCIdName(MDCA::Product aP)
  {
    switch (aP) {
      case Product::QUADRA: return "MDCAQUADRA";
      case Product::VERSAFITCUPCCTRIO: return "MDCAVERSAFITCUPCCTRIO";
      case Product::AMISTEM: return "MDCAAMISTEM";
      case Product::MINIMAX: return "MDCAMINIMAX";
    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch (aP) {
      case Product::QUADRA: return "Quadra.rcc";
      case Product::VERSAFITCUPCCTRIO: return "Versafitcup.rcc";
      case Product::AMISTEM: return "Amistem.rcc";
      case Product::MINIMAX: return "Minimax.rcc";
    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch (aP) {
      case Product::QUADRA: return "/MDCA/QUADRAMeshes";
      case Product::VERSAFITCUPCCTRIO: return "/MDCA/VERSAFITCUPCCTRIOMeshes";
      case Product::AMISTEM: return "/MDCA/AMISTEMMeshes";
      case Product::MINIMAX: return "/MDCA/MINIMAXMeshes";
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItems(Product aP)
  {
    switch (aP) {
      case Product::QUADRA: return 18;
      case Product::VERSAFITCUPCCTRIO: return 13;
      case Product::AMISTEM: return 40;
      case Product::MINIMAX: return -1;
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItemsLoaded(Product aP)
  {
    switch (aP) {
      case Product::QUADRA: return 18;
      case Product::VERSAFITCUPCCTRIO: return 13;
      case Product::AMISTEM: return 40;
      case Product::MINIMAX: return -1;
    };
    return {};
  }

}  // namespace MDCA

namespace SYK {

  enum Product { EXETER,
                 MODULAR };

  const constexpr SboShape3UID companyRangeStartsAt = 250000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 280000L;
  const constexpr char* companyName                 = "SYK";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch (aP) {
      case Product::MODULAR: return companyRangeStartsAt + 0L;
      case Product::EXETER: return companyRangeStartsAt + 250L;
    };
    return 0;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch (aP) {
      case Product::MODULAR: return "SYK MODULAR";
      case Product::EXETER: return "SYK EXETER";
    };
    return {};
  }

  inline constexpr const char* RCCIdName(Product aP)
  {
    switch (aP) {
      case Product::MODULAR: return "SYKMODULAR";
      case Product::EXETER: return "SYKEXETER";
    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch (aP) {
      case Product::MODULAR: return "Modular.rcc";
      case Product::EXETER: return "Exeter.rcc";
    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch (aP) {
      case Product::MODULAR: return "/SYK/MODULARMeshes";
      case Product::EXETER: return "/SYK/EXETERMeshes";
    };
    return {};
  }

}  // namespace SYK

namespace ZB {

  enum Product { EXCEPTION, SPOTORNO, AVENIRCOMPLETE, FITMORE, G7PPSLTDHOLE, G7OSSEOTILTDHOLE };

  const constexpr SboShape3UID companyRangeStartsAt = 190000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 220000L;
  const constexpr char* companyName                 = "ZB";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch(aP) {
    case Product::EXCEPTION: return companyRangeStartsAt + 0L;
    case Product::SPOTORNO: return companyRangeStartsAt + 500L;
    case Product::AVENIRCOMPLETE: return companyRangeStartsAt + 1000L;
    case Product::FITMORE: return companyRangeStartsAt + 1500L;
    case Product::G7PPSLTDHOLE:     return companyRangeStartsAt + 2000L;
    case Product::G7OSSEOTILTDHOLE: return companyRangeStartsAt + 2250L;

    };
    return 0;
  }

  inline constexpr SboShape3UID productRangeOffset(Product)
  {
    return 50L;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch(aP) {
    case Product::EXCEPTION: return "ZB EXCEPTION";
    case Product::SPOTORNO: return "ZB CLS SPOTORNO";
    case Product::AVENIRCOMPLETE: return "ZB AVENIR COMPLETE";
    case Product::FITMORE: return "ZB FITMORE";
    case Product::G7PPSLTDHOLE:     return "ZB G7 PPS LIMITED HOLE";
    case Product::G7OSSEOTILTDHOLE: return "ZB G7 OSSEOTI LIMITED HOLE";

    };
    return {};
  }

  inline constexpr const char* itemName(Product aP)
  {
    switch(aP) {
    case Product::EXCEPTION: return "EXCEPTION";
    case Product::SPOTORNO: return "SPOTORNO";
    case Product::AVENIRCOMPLETE: return "AVENIR COMPLETE";
    case Product::FITMORE: return "FITMORE";
    case Product::G7PPSLTDHOLE:     return "PPS LTD HOLE";
    case Product::G7OSSEOTILTDHOLE: return "OSSEOTI LTD HOLE";
    };
    return {};
  }

  inline constexpr const char* RCCIdName(Product aP)
  {
    switch(aP) {
    case Product::EXCEPTION: return "ZBEXCEPTION";
    case Product::SPOTORNO: return "ZBSPOTORNO";
    case Product::AVENIRCOMPLETE: return "ZBAVENIRCOMPLETE";
    case Product::FITMORE: return "ZBFITMORE";
    case Product::G7PPSLTDHOLE:     return "ZBG7PPSLTDHOLE";
    case Product::G7OSSEOTILTDHOLE: return "ZBG7OSSEOTILTDHOLE";
    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch(aP) {
    case Product::EXCEPTION: return "Exception.rcc";
    case Product::SPOTORNO: return "Spotorno.rcc";
    case Product::AVENIRCOMPLETE: return "Avenircomplete.rcc";
    case Product::FITMORE: return "Fitmore.rcc";
    case Product::G7PPSLTDHOLE:     return "Ppsltdhole.rcc";
    case Product::G7OSSEOTILTDHOLE: return "Osseotiltdhole.rcc";
    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch(aP) {
    case Product::EXCEPTION: return "/ZB/EXCEPTIONMeshes";
    case Product::SPOTORNO: return "/ZB/SPOTORNOMeshes";
    case Product::AVENIRCOMPLETE: return "/ZB/AVENIRCOMPLETEMeshes";
    case Product::FITMORE: return "/ZB/FITMOREMeshes";
    case Product::G7PPSLTDHOLE:     return "/ZB/G7Meshes";
    case Product::G7OSSEOTILTDHOLE: return "/ZB/G7Meshes";
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItems(Product aP)
  {
    switch (aP) {
    case Product::EXCEPTION: return 0;
    case Product::SPOTORNO: return 0;
    case Product::AVENIRCOMPLETE: return 0;
    case Product::FITMORE: return 4*14;
    case Product::G7PPSLTDHOLE:     return 14;
    case Product::G7OSSEOTILTDHOLE: return 20;
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItemsLoaded(Product aP)
  {
    switch (aP) {
    case Product::EXCEPTION: return 1;
    case Product::SPOTORNO: return 1;
    case Product::AVENIRCOMPLETE: return 1;
    case Product::FITMORE: return 4*14;
    case Product::G7PPSLTDHOLE:     return 14;
    case Product::G7OSSEOTILTDHOLE: return 20;
    };
    return {};
  }


} // namespace ZB

namespace AMPLI {

  enum Product { ACOR,
                 STELLAR,
                 SATURNEII,
                 EVOK,
                 FAIR};

  const constexpr SboShape3UID companyRangeStartsAt = 280000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 310000L;
  const constexpr char* companyName                 = "AMPLI";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch (aP) {
      case Product::ACOR: return companyRangeStartsAt + 0L;
      case Product::STELLAR: return companyRangeStartsAt + 250L;
      case Product::SATURNEII: return companyRangeStartsAt + 500L;
      case Product::EVOK: return companyRangeStartsAt + 750L;
      case Product::FAIR: return companyRangeStartsAt + 1250L;
    };
    return 0;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch (aP) {
      case Product::ACOR: return "AMPLI ACOR";
      case Product::STELLAR: return "AMPLI STELLAR";
      case Product::SATURNEII: return "AMPLI SATURNE II";
      case Product::EVOK: return "AMPLI EVOK";
      case Product::FAIR: return "AMPLI FAIR";

    };
    return {};
  }

  inline constexpr const char* RCCIdName(Product aP)
  {
    switch (aP) {
      case Product::ACOR: return "AMPLIACOR";
      case Product::STELLAR: return "AMPLISTELLAR";
      case Product::SATURNEII: return "AMPLISATURNEII";
      case Product::EVOK: return "AMPLIEVOK";
      case Product::FAIR: return "AMPLIFAIR";

    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch (aP) {
      case Product::ACOR: return "Acor.rcc";
      case Product::STELLAR: return "Freeliner.rcc";
      case Product::SATURNEII: return "Saturneii.rcc";
      case Product::EVOK: return "Evok.rcc";
      case Product::FAIR: return "Fair.rcc";

    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch (aP) {
      case Product::ACOR: return "/AMPLI/ACORMeshes";
      case Product::STELLAR: return "/AMPLI/STELLARMeshes";
      case Product::SATURNEII: return "/AMPLI/SATURNEIIMeshes";
      case Product::EVOK: return "/AMPLI/EVOKMeshes";
      case Product::FAIR: return "/AMPLI/FAIRMeshes";
    };
    return {};
  }
}  // namespace AMPLI


namespace ICAST {

  enum Product { ECOFITSTEMC, ECOFITCUP,ECOFITSTEMLESS };

  const constexpr SboShape3UID companyRangeStartsAt = 310000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 340000L;
  const constexpr char* companyName                 = "ICAST";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch (aP) {
      case Product::ECOFITSTEMC: return companyRangeStartsAt + 0L;
      case Product::ECOFITCUP:  return companyRangeStartsAt + 500L;
      case Product::ECOFITSTEMLESS: return companyRangeStartsAt + 750L;

    };
    return 0;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch (aP) {
      case Product::ECOFITSTEMC:     return "ICAST ECOFIT Cemented";
      case Product::ECOFITCUP:       return "ICAST ECOFIT";
      case Product::ECOFITSTEMLESS:  return "ICAST ECOFIT";

    };
    return {};
  }

  inline constexpr const char* itemName(Product aP)
  {
    switch (aP) {
      case Product::ECOFITSTEMC:     return "ECOFIT Cemented";
      case Product::ECOFITCUP:       return "ECOFIT";
      case Product::ECOFITSTEMLESS:  return "ECOFIT";

    };
    return {};
  }


  inline constexpr const char* RCCIdName(Product aP)
  {
    switch (aP) {
      case Product::ECOFITSTEMC: return "ICASTECOFITSTEMC";
    case Product::ECOFITCUP: return  "ICASTECOFITCUP";
      case Product::ECOFITSTEMLESS: return "ICASTECOFITSTEMLESS";

    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch (aP) {
      case Product::ECOFITSTEMC: return "Ecofitstem.rcc";
      case Product::ECOFITCUP: return "Ecofitcup.rcc";
      case Product::ECOFITSTEMLESS: return "Ecofitstemless.rcc";

    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch (aP) {
      case Product::ECOFITSTEMC: return "/ICAST/ECOFITSTEMCEMENTEDMeshes";
      case Product::ECOFITCUP: return "/ICAST/ECOFITCUPMeshes";
      case Product::ECOFITSTEMLESS: return "/ICAST/ECOFITSTEMLESSMeshes";

    };
    return {};
  }
}


namespace JNJ {

  enum Product { CORAIL,PINNACLE,ACTIS };

  const constexpr SboShape3UID companyRangeStartsAt = 160000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 190000L;
  const constexpr char* companyName                 = "JnJ";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch(aP) {
    case Product::CORAIL:     return companyRangeStartsAt + 0L;
    // case Product::CORAIL_REV: return companyRangeStartsAt + 500L;
    case Product::PINNACLE:   return companyRangeStartsAt + 1000L;
    case Product::ACTIS:      return companyRangeStartsAt + 1250L;
    };
    return 0;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch(aP) {
    case Product::CORAIL:   return "JnJ CORAIL";
    case Product::PINNACLE:   return "JnJ PINNACLE";
    case Product::ACTIS: return "JnJ ACTIS";
    };
    return {};
  }

  inline constexpr const char* itemName(Product aP)
  {
    switch(aP) {
    case Product::CORAIL:     return "CORAIL";
    case Product::PINNACLE:   return "PINNACLE";
    case Product::ACTIS: return "ACTIS";
    };
    return {};
  }

  inline constexpr const char* RCCIdName(Product aP)
  {
    switch(aP) {
    case Product::CORAIL:     return "JNJCORAIL";
    case Product::PINNACLE:   return "JNJPINNACLE";
    case Product::ACTIS: return "JNJACTIS";
    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch(aP) {
    case Product::CORAIL:     return "Corail.rcc";
    case Product::PINNACLE:   return "Pinnacle.rcc";
    case Product::ACTIS: return "Actis.rcc";
    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch(aP) {
    case Product::CORAIL:     return "/JNJDS/CORAILMeshes";
    case Product::PINNACLE:   return "/JNJDS/PINNACLEACECUPMeshes";
    case Product::ACTIS: return "/JNJDS/ACTISMeshes";
    };
    return {};
  }
}

namespace BBRAUN {

  enum Product { METHA,PLASMAFITPLUS };

  const constexpr SboShape3UID companyRangeStartsAt = 340000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 370000L;
  const constexpr char* companyName                 = "BBRAUN";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch(aP) {
    case Product::METHA:       return companyRangeStartsAt + 0L;
    case Product::PLASMAFITPLUS:   return companyRangeStartsAt + 500L;
    };
    return 0;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch(aP) {
    case Product::METHA:       return "BBRAUN METHA";
    case Product::PLASMAFITPLUS:   return "BBRAUN PLASMAFIT PLUS";
    };
    return {};
  }

  inline constexpr const char* itemName(Product aP)
  {
    switch(aP) {
    case Product::METHA:       return "METHA";
    case Product::PLASMAFITPLUS:   return "PLASMAFIT";
    };
    return {};
  }

  inline constexpr const char* RCCIdName(Product aP)
  {
    switch(aP) {
    case Product::METHA:       return "BBRAUNMETHA";
    case Product::PLASMAFITPLUS:   return "BBRAUNPLASMAFIT";
    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch(aP) {
    case Product::METHA:       return "metha.rcc";
    case Product::PLASMAFITPLUS:   return "plasmafit.rcc";
    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch(aP) {
    case Product::METHA:       return "/BBRAUN/METHAMeshes";
    case Product::PLASMAFITPLUS:   return "/BBRAUN/PLASMAFITMeshes";
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItems(Product aP)
  {
    switch (aP) {
      case Product::METHA: return 24;
      case Product::PLASMAFITPLUS: return 16;
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItemsLoaded(Product aP)
  {
    switch (aP) {
      case Product::METHA: return 24;
      case Product::PLASMAFITPLUS: return 16;
    };
    return {};
  }


}

namespace BIOIMP {

  enum Product { FINSHORT,FINDMD,SAPHIR,KORUS };

  const constexpr SboShape3UID companyRangeStartsAt = 370000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 400000L;
  const constexpr char* companyName                 = "BIOIMP";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch(aP) {
    case Product::FINSHORT:  return companyRangeStartsAt + 0L;
    case Product::FINDMD:    return companyRangeStartsAt + 500L;
    case Product::SAPHIR:    return companyRangeStartsAt + 750L;
    case Product::KORUS:    return companyRangeStartsAt + 1250L;
    };
    return 0;
  }

  inline constexpr SboShape3UID productRangeOffset(Product)
  {
    return 50L;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch(aP) {
    case Product::FINSHORT:  return "BIOIMP FINSHORT";
    case Product::FINDMD:   return "BIOIMP FIN DMD";
    case Product::SAPHIR:   return "BIOIMP SAPHIR";
    case Product::KORUS:    return "BIOIMP KORUS uncemented";
    };
    return {};
  }

  inline constexpr const char* itemName(Product aP)
  {
    switch(aP) {
    case Product::FINSHORT:  return "FINSHORT";
    case Product::FINDMD:   return "FIN DMD";
    case Product::SAPHIR:    return "SAPHIR";
    case Product::KORUS:    return "KORUS";
    };
    return {};
  }

  inline constexpr const char* RCCIdName(Product aP)
  {
    switch(aP) {
    case Product::FINSHORT:  return "BIOIMPFINSHORT";
    case Product::FINDMD:   return "BIOIMPFINDMD";
    case Product::SAPHIR:   return "BIOIMPSAPHIR";
    case Product::KORUS:   return "BIOIMPKORUS";
    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch(aP) {
    case Product::FINSHORT:  return "finshort.rcc";
    case Product::FINDMD:   return "findmd.rcc";
    case Product::SAPHIR:   return "saphir.rcc";
    case Product::KORUS:    return "korus.rcc";
    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch(aP) {
    case Product::FINSHORT:  return "/BIOIMP/FINSHORTMeshes";
    case Product::FINDMD:   return "/BIOIMP/FINCUPMeshes";
    case Product::SAPHIR:   return "/BIOIMP/SAPHIRMeshes";
    case Product::KORUS:    return "/BIOIMP/KORUSMeshes";
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItems(Product aP)
  {
    switch (aP) {
    case Product::FINSHORT: return 18;
    case Product::FINDMD:   return 16;
    case Product::SAPHIR:   return 29+29+9+9;
    case Product::KORUS:    return 10+10;
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItemsLoaded(Product aP)
  {
    switch (aP) {
    case Product::FINSHORT: return 18;
    case Product::FINDMD:   return 16;
    case Product::SAPHIR:   return 29+29+9+9;
    case Product::KORUS:    return 10+10;
    };
    return {};
  }

}

namespace UO {

  // CH for cluster-hole
  enum Product { CONFORMITY, UDMPRESSFIT, UMOTIONIICH };

  const constexpr SboShape3UID companyRangeStartsAt = 400000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 430000L;
  const constexpr char* companyName                 = "UO";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch(aP) {
    case Product::CONFORMITY:  return companyRangeStartsAt + 0L;
    case Product::UDMPRESSFIT:   return companyRangeStartsAt + 500L;
    case Product::UMOTIONIICH:   return companyRangeStartsAt + 750L;
    };
    return 0;
  }

  inline constexpr SboShape3UID productRangeOffset(Product aP)
  {
    switch(aP) {
    case Product::CONFORMITY:  return 50L;
    case Product::UDMPRESSFIT:   return 50L;
    case Product::UMOTIONIICH:   return 50L;
    };
    return 0;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch(aP) {
    case Product::CONFORMITY:  return "UO CONFORMITY";
    case Product::UDMPRESSFIT:   return "UO UDM Pressfit";
    case Product::UMOTIONIICH:   return "UO U-Motion II";
    };
    return {};
  }

  inline constexpr const char* itemName(Product aP)
  {
    switch(aP) {
    case Product::CONFORMITY:  return "CONFORMITY";
    case Product::UDMPRESSFIT:   return "UDM PRESSFIT";
    case Product::UMOTIONIICH:   return "U-MOTION II";
    };
    return {};
  }

  inline constexpr const char* RCCIdName(Product aP)
  {
    switch(aP) {
    case Product::CONFORMITY:  return "UOCONFORMITY";
    case Product::UDMPRESSFIT:   return "UDMPRESSFIT";
    case Product::UMOTIONIICH:   return "UMOTIONIICH";
    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch(aP) {
    case Product::CONFORMITY:  return "conformity.rcc";
    case Product::UDMPRESSFIT:   return "udmpressfit.rcc";
    case Product::UMOTIONIICH:   return "umotioniich.rcc";
    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch(aP) {
    case Product::CONFORMITY:  return "/UO/CONFORMITYMeshes";
    case Product::UDMPRESSFIT:   return "/UO/UDMMeshes";
    case Product::UMOTIONIICH:   return "/UO/UMOTIONIIMeshes";
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItems(Product aP)
  {
    switch (aP) {
      case Product::CONFORMITY: return 57;
      case Product::UDMPRESSFIT: return 10;
      case Product::UMOTIONIICH:  return 11;
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItemsLoaded(Product aP)
  {
    switch (aP) {
      case Product::CONFORMITY: return 57;
      case Product::UDMPRESSFIT: return 10;
      case Product::UMOTIONIICH:  return 11;
    };
    return {};
  }

}

namespace LC {

  enum Product { FRIENDLYSHORT};

  const constexpr SboShape3UID companyRangeStartsAt = 60000L;
  const constexpr SboShape3UID companyRangeEndsAt   = 90000L;
  const constexpr char* companyName                 = "LC";

  inline constexpr SboShape3UID productRangeStartsAt(Product aP)
  {
    switch(aP) {
    case Product::FRIENDLYSHORT:       return companyRangeStartsAt + 3250L;
    };
    return 0;
  }

  inline constexpr const char* productName(Product aP)
  {
    switch(aP) {
    case Product::FRIENDLYSHORT:       return "LC FRIENDLY SHORT";
    };
    return {};
  }

  inline constexpr const char* itemName(Product aP)
  {
    switch(aP) {
    case Product::FRIENDLYSHORT:       return "FRIENDLY SHORT";
    };
    return {};
  }

  inline constexpr const char* RCCIdName(Product aP)
  {
    switch(aP) {
    case Product::FRIENDLYSHORT:       return "LCFRIENDLYSHORT";
    };
    return {};
  }

  inline constexpr const char* RCCFileName(Product aP)
  {
    switch(aP) {
    case Product::FRIENDLYSHORT:       return "friendlyshort.rcc";
    };
    return {};
  }

  inline constexpr const char* RCCPath(Product aP)
  {
    switch(aP) {
    case Product::FRIENDLYSHORT:       return "/LC/FRIENDLYSHORTMeshes";
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItems(Product aP)
  {
    switch (aP) {
      case Product::FRIENDLYSHORT: return 8;
    };
    return {};
  }

  inline constexpr std::size_t nbrOfItemsLoaded(Product aP)
  {
    switch (aP) {
      case Product::FRIENDLYSHORT: return 8;
    };
    return {};
  }


}

HPROJ_END_NAMESPACE

"""Lookup utilities for implant stems across supported vendors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import amedacta_complete as mdca_amistem_implants
import implancast_ecofit_complete as icast_ecofit_implants
import johnson_actis_complete as jj_actis_implants
import johnson_corail_complete as jj_corail_implants
import lima_fit_complete as lima_fit_implants
import legacy_implants.mathys_implants as mys_implants


@dataclass(frozen=True)
class StemLookupResult:
    """Structured metadata for a resolved implant stem UID."""

    uid: int
    manufacturer: str
    enum_name: str
    friendly_name: str
    rcc_id: Optional[str]


def _friendly_enum_name(enum_name: str) -> str:
    """Convert an internal enum constant (e.g. STEM_STD_1) to a readable label."""

    return enum_name.replace("_", " ").strip()


def resolve_stem_uid(uid: Optional[int]) -> Optional[StemLookupResult]:
    """Return vendor metadata for the provided implant stem UID, if known."""

    if uid is None:
        return None

    lookup_table = (
        ("Medacta (AMISTEM)", mdca_amistem_implants.S3UID, mdca_amistem_implants.get_rcc_id),
        ("Mathys", mys_implants.S3UID, mys_implants.get_rcc_id),
        ("Johnson & Johnson (Corail)", jj_corail_implants.S3UID, jj_corail_implants.get_rcc_id),
        ("Johnson & Johnson (Actis)", jj_actis_implants.S3UID, jj_actis_implants.get_rcc_id),
        ("Implantcast (Ecofit)", icast_ecofit_implants.S3UID, icast_ecofit_implants.get_rcc_id),
        ("Lima (FIT)", lima_fit_implants.S3UID, lima_fit_implants.get_rcc_id),
    )

    for manufacturer, enum_cls, get_rcc in lookup_table:
        try:
            enum_member = enum_cls(uid)
        except ValueError:
            continue

        rcc_id = None
        try:
            rcc_id = get_rcc(enum_member)
        except KeyError:
            rcc_id = None

        return StemLookupResult(
            uid=uid,
            manufacturer=manufacturer,
            enum_name=enum_member.name,
            friendly_name=_friendly_enum_name(enum_member.name),
            rcc_id=rcc_id,
        )

    return None


__all__ = ["StemLookupResult", "resolve_stem_uid"]

import logging

from fastapi import APIRouter

from app.drivers.application_profiles import ApplicationProfilesInterfaceDep
from app.drivers.utilities import compare_min_rate_to_nef_bitrate
from app.schemas.camara.application_profiles import NetworkQualityThresholds
from app.schemas.camara.connectivity_insights_subscriptions import (
    NetworkQualityInsight,
    NetworkQualityThresholdsConfidence,
)
from app.schemas.nef.analytics_exposure import (
    AnalyticsEvent,
    AnalyticsEventNotification,
    TrafficInformation,
)

LOG = logging.getLogger(__name__)

router = APIRouter()

_REQUIREMENTS_MET = (
    NetworkQualityThresholdsConfidence.meets_the_application_requirements
)
_REQUIREMENTS_UNMET = (
    NetworkQualityThresholdsConfidence.unable_to_meet_the_application_requirements
)


@router.post("/nef/{ue_supi}")
async def nef_analytics_callback(
    ue_supi: str,
    body: AnalyticsEventNotification,
    application_profiles_interface: ApplicationProfilesInterfaceDep,
) -> None:
    """Receive WLAN_PERFORMANCE analytics notifications from the NEF."""
    notif_id = body.notifId
    LOG.info(
        "Received NEF analytics callback for UE supi=%s, notifId=%s", ue_supi, notif_id
    )

    if body.termCause is not None:
        LOG.warning(
            "UE supi=%s, notifId=%s: Analytics subscription terminated, cause=%s",
            ue_supi,
            notif_id,
            body.termCause,
        )
        return

    profile = await application_profiles_interface.get_application_profile(ue_supi)
    thresholds = profile.networkQualityThresholds
    if thresholds is None or not thresholds.model_dump(exclude_none=True):
        LOG.info(
            "UE supi=%s, notifId=%s: Empty/None thresholds for profile %s, skipping",
            ue_supi,
            notif_id,
            profile.applicationProfileId,
        )
        return

    insight = NetworkQualityInsight(
        papplicationProfileId=profile.applicationProfileId,
        # defaults to _REQUIREMENTS_MET; only targetMinUpstreamRate and targetMinDownstreamRate are enforced
        targetMinUpstreamRate=_REQUIREMENTS_MET,
        targetMinDownstreamRate=_REQUIREMENTS_MET,
    )

    notif = body.analyEventNotifs[0]  # should only return one notification at a time
    if notif.analyEvent != AnalyticsEvent.WLAN_PERFORMANCE:
        # should never happen (subscription is for WLAN_PERFORMANCE only)
        LOG.warning(
            "UE supi=%s, notifId=%s: Unsupported event %s (not WLAN_PERFORMANCE), ignoring",
            ue_supi,
            notif_id,
            notif.analyEvent,
        )
        return
    if not notif.wlanInfos:
        # should never happen (NEF returning empty wlanInfos)
        LOG.warning(
            "UE supi=%s, notifId=%s: wlanInfos empty/none for WLAN_PERFORMANCE notification",
            ue_supi,
            notif_id,
        )
        return

    # given subscription will, at max, return one wlanInfo (temporalGranSize >= offsetPeriod)
    if len(notif.wlanInfos) != 1:
        # should never happen
        LOG.warning(
            "UE supi=%s, notifId=%s: Received %d wlanInfos, expected 1. Processing first one.",
            ue_supi,
            notif_id,
            len(notif.wlanInfos),
        )

    wlan_info = notif.wlanInfos[0]
    ue_info = (
        next(
            (
                ue_entry.root
                for ue_entry in wlan_info.wlanPerUeIdInfos
                if ue_entry.root.gpsi and ue_entry.root.gpsi == f"msisdn-{notif_id}"
            ),
            None,
        )
        if wlan_info.wlanPerUeIdInfos
        else None
    )

    if ue_info is None:
        # should never happen (missing UE info — no traffic UEs will return zeroed metric values)
        LOG.warning(
            "UE supi=%s, notifId=%s: No matching UE info found in WLAN_PERFORMANCE notification, skipping",
            ue_supi,
            notif_id,
        )
        return

    for ts_entry in ue_info.wlanPerTsInfos:
        wlan_ts_info = ts_entry.root
        traffic = (
            wlan_ts_info.trafficInfo if wlan_ts_info.trafficInfo is not None else None
        )
        if not traffic:
            LOG.warning(
                "UE supi=%s, notifId=%s: Missing traffic information in ts_info, skipping",
                ue_supi,
                notif_id,
            )
            continue

        was_updated = _update_insight(thresholds, insight, traffic)
        if was_updated and _all_requirements_unmet(insight):
            break

    LOG.info(
        "UE supi=%s, notifId=%s: analytics SLA check — UL=%s, DL=%s",
        ue_supi,
        notif_id,
        insight.targetMinUpstreamRate,
        insight.targetMinDownstreamRate,
    )
    # TODO: propagate insight to application state store


def _update_insight(
    thresholds: NetworkQualityThresholds,
    insight: NetworkQualityInsight,
    traffic: TrafficInformation,
) -> bool:
    """Update insight with traffic measurements against thresholds. Once unmet, stays unmet.

    Currently only targetMinUpstreamRate and targetMinDownstreamRate are checked.
    Returns True if insight was changed.
    """
    updated = False

    if thresholds.targetMinUpstreamRate is not None:
        nef_ul_rate = traffic.root.uplinkRate
        if nef_ul_rate is not None:
            prev = insight.targetMinUpstreamRate
            if prev == _REQUIREMENTS_MET:
                new = compare_min_rate_to_nef_bitrate(
                    thresholds.targetMinUpstreamRate, nef_ul_rate
                )
                insight.targetMinUpstreamRate = _worst_confidence(prev, new)
                updated |= prev != insight.targetMinUpstreamRate
        else:
            LOG.warning(
                "Missing uplinkRate in traffic info, skipping targetMinUpstreamRate check"
            )

    if thresholds.targetMinDownstreamRate is not None:
        nef_dl_rate = traffic.root.downlinkRate
        if nef_dl_rate is not None:
            prev = insight.targetMinDownstreamRate
            if prev == _REQUIREMENTS_MET:
                new = compare_min_rate_to_nef_bitrate(
                    thresholds.targetMinDownstreamRate, nef_dl_rate
                )
                insight.targetMinDownstreamRate = _worst_confidence(prev, new)
                updated |= prev != insight.targetMinDownstreamRate
        else:
            LOG.warning(
                "Missing downlinkRate in traffic info, skipping targetMinDownstreamRate check"
            )

    return updated


def _all_requirements_unmet(insight: NetworkQualityInsight) -> bool:
    """Return True if all checked requirements are unmet."""
    checks = [insight.targetMinUpstreamRate, insight.targetMinDownstreamRate]
    return all(v == _REQUIREMENTS_UNMET for v in checks)


def _worst_confidence(
    current: NetworkQualityThresholdsConfidence,
    new: NetworkQualityThresholdsConfidence,
) -> NetworkQualityThresholdsConfidence:
    if current == _REQUIREMENTS_UNMET or new == _REQUIREMENTS_UNMET:
        return _REQUIREMENTS_UNMET
    return new

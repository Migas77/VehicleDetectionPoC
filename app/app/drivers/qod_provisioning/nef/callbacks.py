import logging

from fastapi import APIRouter

from app.drivers.qod_provisioning.deps import QoDProvisioningInterfaceDep
from app.drivers.ues import UEsInterfaceDep
from app.schemas.nef.afSessionWithQos import UserPlaneNotificationData
from app.schemas.nef.commonData import UserPlaneEvent
from app.schemas.poc import QosStatus

LOG = logging.getLogger(__name__)

router = APIRouter()

_AVAILABLE_EVENTS = {
    UserPlaneEvent.SUCCESSFUL_RESOURCES_ALLOCATION,
    UserPlaneEvent.QOS_GUARANTEED,
}
_UNAVAILABLE_EVENTS = {
    UserPlaneEvent.FAILED_RESOURCES_ALLOCATION,
    UserPlaneEvent.QOS_NOT_GUARANTEED,
    UserPlaneEvent.SESSION_TERMINATION,
}


@router.post("/nef/{ue_supi}")
async def nef_qos_callback(
    ue_supi: str,
    body: UserPlaneNotificationData,
    qod_provisioning_interface: QoDProvisioningInterfaceDep,
    ues_interface: UEsInterfaceDep,
) -> None:
    """Receive UserPlaneNotificationData events from the NEF for a given UE."""
    # LOG.info(
    #     "Received NEF QoS callback for UE supi=%s: %s event(s)",
    #     ue_supi,
    #     len(body.eventReports),
    # )
    # for report in body.eventReports:
    #     LOG.info("  UE supi=%s event: %s", ue_supi, report.event)
    status = _get_qos_status(body)
    if status is None:
        return

    # transaction is the subscription's 'self' link, ending in the subscription ID
    provisioning_id = str(body.transaction).rstrip("/").split("/")[-1]
    await qod_provisioning_interface.apply_qos_notification(
        ue_supi, provisioning_id, status
    )

    if (
        status == QosStatus.UNAVAILABLE
        and await qod_provisioning_interface.can_switch_to_fallback_qos_profile(ue_supi)
    ):
        LOG.warning(
            "UE supi=%s, subscriptionId=%s: QoS unavailable (events=%s)",
            ue_supi,
            provisioning_id,
            [report.event.value for report in body.eventReports],
        )
        ue = await ues_interface.get_ue_by_supi(ue_supi)
        await qod_provisioning_interface.switch_to_fallback_qos_profile(ue)


def _get_qos_status(body: UserPlaneNotificationData) -> QosStatus | None:
    """Map the reported events to a QoS status. A negative event wins over a positive one,
    since eventReports carries no ordering. Returns None if no event affects the status.
    """
    events = {report.event for report in body.eventReports}
    if events & _UNAVAILABLE_EVENTS:
        return QosStatus.UNAVAILABLE
    if events & _AVAILABLE_EVENTS:
        return QosStatus.AVAILABLE
    return None

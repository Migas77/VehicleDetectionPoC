import logging

from fastapi import APIRouter

from app.drivers.qod_provisioning.deps import QoDProvisioningInterfaceDep
from app.drivers.ues import UEsInterfaceDep
from app.schemas.camara.qodProvisioning import CloudEvent, StatusChanged
from app.schemas.poc import QosStatus

LOG = logging.getLogger(__name__)

router = APIRouter()


@router.post("/camara/{ue_supi}")
async def camara_qos_callback(
    ue_supi: str,
    body: CloudEvent,
    qod_provisioning_interface: QoDProvisioningInterfaceDep,
    ues_interface: UEsInterfaceDep,
) -> None:
    """Receive CloudEvent status-changed notifications from the CAMARA gateway for a given UE."""
    # LOG.info(
    #     "Received CAMARA QoD provisioning callback for UE supi=%s: "
    #     "type=%s, provisioningId=%s, status=%s",
    #     ue_supi,
    #     body.type,
    #     body.data.provisioningId,
    #     body.data.status,
    # )
    data = body.data
    if data.status is None:
        return
    status = (
        QosStatus.AVAILABLE
        if data.status == StatusChanged.AVAILABLE
        else QosStatus.UNAVAILABLE
    )

    provisioning_id = str(data.provisioningId)
    await qod_provisioning_interface.apply_qos_notification(
        ue_supi, provisioning_id, status
    )

    if (
        status == QosStatus.UNAVAILABLE
        and await qod_provisioning_interface.can_switch_to_fallback_qos_profile(ue_supi)
    ):
        LOG.warning(
            "UE supi=%s, provisioningId=%s: QoS unavailable (statusInfo=%s)",
            ue_supi,
            provisioning_id,
            data.statusInfo,
        )
        ue = await ues_interface.get_ue_by_supi(ue_supi)
        await qod_provisioning_interface.switch_to_fallback_qos_profile(ue)

from app.schemas.poc.ue import UE
from app.schemas.qos_profile import QosProfile


class UeWithQoS(UE):
    """UE that carries a QoS profile. qos_profile_id starts None until create_qos_profile runs."""

    qos_profile: QosProfile

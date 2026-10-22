import logging
from abc import ABC, abstractmethod
from typing import Any

from app.redis import get_redis
from app.schemas.poc import UE, CameraQosState, QosStatus
from app.schemas.poc.ue_with_qos import UeWithQoS
from app.settings import settings

LOG = logging.getLogger(__name__)


class QoDProvisioningInterface(ABC):
    def __init__(self) -> None:
        self._redis = get_redis()

    @staticmethod
    def _fallback_key(ue_supi: str) -> str:
        """Build the Redis key marking a UE as switched to the fallback QoS profile."""
        return f"poc:qod:fallback:{ue_supi}"

    @staticmethod
    def _qos_state_key(ue_supi: str) -> str:
        """Build the Redis key holding the UE's provisioning ID, applied and pending profiles."""
        return f"poc:qod:state:{ue_supi}"

    @staticmethod
    def _state_field(data: dict[Any, Any], field: str) -> str | None:
        """Read a field from the QoS state hash, mapping missing/empty to None."""
        # the client decodes responses, so values are always str
        value = str(data.get(field) or "")
        return value or None

    @abstractmethod
    async def _create_provisioning(self, ue: UeWithQoS) -> str:
        """Create an indefinite QoS provisioning for the UE and return its provisioning ID."""

    @abstractmethod
    async def _replace_provisioning(self, provisioning_id: str, ue: UeWithQoS) -> str:
        """Move the UE's existing provisioning to ue.qos_profile.

        Returns the provisioning ID now holding the request (unchanged if updated in
        place). The new profile only counts as applied once a notification confirms it.
        """

    @abstractmethod
    async def get_qod_provisioning(self, provisioning_id: str) -> dict[str, Any]:
        """Retrieve the QoS provisioning info by ID."""

    @abstractmethod
    async def delete_qod_provisioning(self, provisioning_id: str) -> bool:
        """Delete the QoS provisioning by ID. Returns True on success."""

    @abstractmethod
    async def retrieve_qod_provisioning_by_device(self, ue: UE) -> str | None:
        """Find the provisioning ID for the given UE device. Returns None if not found."""

    async def assign_qos_profile(self, ue: UeWithQoS) -> str:
        """Create an indefinite QoS provisioning for the UE and return its provisioning ID.

        The profile stays pending until a notification confirms it.
        """
        qos_profile_name = ue.qos_profile.qos_profile_name
        await self._request_qos_profile(ue.supi, qos_profile_name, None)
        try:
            provisioning_id = await self._create_provisioning(ue)
        except Exception:
            await self._cancel_qos_request(ue.supi, qos_profile_name)
            raise
        await self._redis.hset(
            self._qos_state_key(ue.supi), "provisioning_id", provisioning_id
        )
        return provisioning_id

    async def replace_qos_profile(self, ue: UeWithQoS) -> str:
        """Move the UE to ue.qos_profile, creating a provisioning if it has none.

        Returns the provisioning ID now holding the request.
        """
        provisioning_id = await self.retrieve_qod_provisioning_by_device(ue)
        if provisioning_id is None:
            return await self.assign_qos_profile(ue)
        return await self._replace_provisioning(provisioning_id, ue)

    async def can_switch_to_fallback_qos_profile(self, ue_supi: str) -> bool:
        """Return True if a fallback profile is configured and the UE isn't using it yet."""
        if settings.cameras.fallback_qos_profile is None:
            return False
        return not await self._redis.exists(self._fallback_key(ue_supi))

    async def switch_to_fallback_qos_profile(self, ue: UE) -> str | None:
        """Request the fallback QoS profile for the UE's provisioning.

        Switches at most once per UE (until clear_fallback_qos_profile is called).
        Returns the provisioning ID holding the request, or None if nothing was switched.
        """
        fallback = settings.cameras.fallback_qos_profile
        if fallback is None:
            return None
        key = self._fallback_key(ue.supi)
        # NX doubles as a lock against concurrent breach callbacks for the same UE
        if not await self._redis.set(key, fallback.qos_profile_name, nx=True):
            return None

        try:
            provisioning_id = await self.replace_qos_profile(
                UeWithQoS.model_validate(
                    {**ue.model_dump(), "qos_profile": fallback.model_dump()}
                )
            )
        except Exception:
            await self._redis.delete(key)
            raise

        LOG.warning(
            "UE supi=%s: requested fallback QoS profile %s (provisioningId=%s)",
            ue.supi,
            fallback.qos_profile_name,
            provisioning_id,
        )
        return provisioning_id

    async def clear_fallback_qos_profile(self, ue_supi: str) -> None:
        """Forget that the UE was switched to the fallback QoS profile."""
        await self._redis.delete(self._fallback_key(ue_supi))

    async def _request_qos_profile(
        self, ue_supi: str, qos_profile_name: str, provisioning_id: str | None
    ) -> None:
        """Mark a profile as requested for the UE, before the request is sent.

        Recorded beforehand so a notification racing the response finds it.
        provisioning_id is None when the request creates a new provisioning.
        """
        key = self._qos_state_key(ue_supi)
        if provisioning_id is None:
            # the creation is in flight, its ID is only known from the response
            await self._redis.hset(key, "provisioning_id", "")
        await self._redis.hset(key, "pending_qos_profile_name", qos_profile_name)
        await self._log_qos_event(ue_supi, "REQUESTED", qos_profile_name)

    async def _cancel_qos_request(self, ue_supi: str, qos_profile_name: str) -> None:
        """Clear the UE's requested profile after the request itself failed."""
        await self._redis.hset(
            self._qos_state_key(ue_supi), "pending_qos_profile_name", ""
        )
        await self._log_qos_event(
            ue_supi, "FAILED", qos_profile_name, level=logging.WARNING
        )

    async def _log_qos_event(
        self,
        ue_supi: str,
        event: str,
        qos_profile_name: str | None,
        level: int = logging.INFO,
    ) -> None:
        """Log a QoS profile event together with the UE's resulting QoS state.

        Grep for "QoS supi=" to follow the profiles; `active` is the applied profile.
        """
        state = await self.get_qos_state(ue_supi)
        LOG.log(
            level,
            "QoS supi=%s %s profile=%s | active=%s pending=%s provisioningId=%s",
            ue_supi,
            event,
            qos_profile_name,
            state.qos_profile_name if state is not None else None,
            state.pending_qos_profile_name if state is not None else None,
            state.provisioning_id if state is not None else None,
        )

    async def apply_qos_notification(
        self, ue_supi: str, provisioning_id: str, status: QosStatus
    ) -> None:
        """Update the UE's QoS state from a notification about one of its provisionings.

        A pending profile becomes the applied one only once confirmed. If it is
        rejected, the previously applied profile (if any) remains in place.
        """
        key = self._qos_state_key(ue_supi)
        data = await self._redis.hgetall(key)
        if not data:
            LOG.warning(
                "QoS supi=%s IGNORED %s notification for unknown provisioningId=%s",
                ue_supi,
                status.value,
                provisioning_id,
            )
            return
        current_id = self._state_field(data, "provisioning_id")
        # an empty ID means the creation is in flight, so the notification is for it
        if current_id is not None and current_id != provisioning_id:
            LOG.warning(
                "QoS supi=%s IGNORED %s notification for stale provisioningId=%s "
                "(current %s)",
                ue_supi,
                status.value,
                provisioning_id,
                current_id,
            )
            return

        pending = self._state_field(data, "pending_qos_profile_name")
        applied = self._state_field(data, "qos_profile_name")
        if status == QosStatus.AVAILABLE:
            if pending is None:
                await self._log_qos_event(ue_supi, "CONFIRMED", applied)
                return
            await self._redis.hset(
                key,
                mapping={"qos_profile_name": pending, "pending_qos_profile_name": ""},
            )
            await self._log_qos_event(ue_supi, "APPLIED", pending)
        elif pending is not None:
            # the previously applied profile (if any) remains in place
            await self._redis.hset(key, "pending_qos_profile_name", "")
            await self._log_qos_event(
                ue_supi, "REJECTED", pending, level=logging.WARNING
            )
        else:
            # no request in flight, so the applied profile itself was lost
            await self._redis.hset(key, "qos_profile_name", "")
            await self._log_qos_event(ue_supi, "LOST", applied, level=logging.WARNING)

    async def get_qos_state(self, ue_supi: str) -> CameraQosState | None:
        """Return the UE's current QoS state, or None if it was never provisioned."""
        data = await self._redis.hgetall(self._qos_state_key(ue_supi))
        if not data:
            return None
        return CameraQosState(
            provisioning_id=self._state_field(data, "provisioning_id"),
            qos_profile_name=self._state_field(data, "qos_profile_name"),
            pending_qos_profile_name=self._state_field(
                data, "pending_qos_profile_name"
            ),
        )

    async def clear_qos_state(self, ue_supi: str) -> None:
        """Forget the UE's provisioning and QoS profiles."""
        state = await self.get_qos_state(ue_supi)
        await self._redis.delete(self._qos_state_key(ue_supi))
        if state is not None:
            # called alongside deleting its provisioning, which reverts the UE's QoS
            await self._log_qos_event(ue_supi, "REMOVED", state.qos_profile_name)

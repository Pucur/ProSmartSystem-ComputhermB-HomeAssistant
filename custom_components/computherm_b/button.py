import logging
from homeassistant.components.button import ButtonEntity
from .auth import ProSmartAuth
from homeassistant.helpers.aiohttp_client import async_get_clientsession

DOMAIN = "computherm_b"
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up ProSmart buttons from a config entry."""
    email = entry.data["email"]
    password = entry.data["password"]
    session = async_get_clientsession(hass)
    auth = ProSmartAuth(session, email, password)

    entities = []

    devices = await auth.request("GET", "https://api.prosmartsystem.com/api/devices")

    for dev in devices:
        device_id = dev["id"]
        device_name = dev.get("name") or dev.get("serial_number")

        entities.append(ProSmartModeButton(hass, auth, device_id, "MANUAL", device_name))
        entities.append(ProSmartModeButton(hass, auth, device_id, "SCHEDULE", device_name))
        entities.append(ProSmartModeButton(hass, auth, device_id, "OFF", device_name))


    async_add_entities(entities)
    _LOGGER.info("ProSmart buttons added: %s", [e.name for e in entities])


class ProSmartModeButton(ButtonEntity):
    """Button to set heating mode (MANUAL / SCHEDULE)."""

    def __init__(self, hass, auth: ProSmartAuth, device_id, mode, name):
        self.hass = hass
        self._auth = auth
        self._device_id = device_id
        self._mode = mode
        self._attr_name = f"{name} {mode}"
        self._attr_unique_id = f"{device_id}_{mode}_button"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": f"ProSmart {self._device_id}",
            "manufacturer": "ProSmart System",
            "model": "BBoil Classic",
        }

    async def async_press(self):
        """Send the mode change POST request."""
        await self._send_cmd({"mode": self._mode})

    async def _send_cmd(self, json_data):
        try:
            await self._auth.request(
                "POST",
                f"https://api.prosmartsystem.com/api/devices/{self._device_id}/cmd",
                json=json_data
            )
            _LOGGER.info("Mode set to %s for device %s", self._mode, self._device_id)
        except Exception as e:
            _LOGGER.error("Failed to set mode %s: %s", self._mode, e)

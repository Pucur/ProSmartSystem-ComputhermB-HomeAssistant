import logging
from homeassistant.components.number import NumberEntity
from .auth import ProSmartAuth
from homeassistant.helpers.aiohttp_client import async_get_clientsession


_LOGGER = logging.getLogger(__name__)
DOMAIN = "computherm_b"

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up ProSmart numbers from a config entry."""
    email = entry.data["email"]
    password = entry.data["password"]
    session = async_get_clientsession(hass)
    auth = ProSmartAuth(session, email, password)

    entities = []

    try:
        devices = await auth.request("GET", "https://api.prosmartsystem.com/api/devices")
    except Exception as e:
        _LOGGER.error("Error fetching devices: %s", e)
        return

    for dev in devices:
        device_id = dev["id"]
        device_name = dev.get("name") or dev.get("serial_number")

        entities.append(ProSmartBoostDuration(auth, device_id, device_name))
        entities.append(ProSmartBoostTemperature(auth, device_id, device_name))
        entities.append(ProSmartManualTemperature(auth, device_id, device_name))
        entities.append(ProSmartHysteresisLow(auth, device_id, device_name))
        entities.append(ProSmartHysteresisHigh(auth, device_id, device_name))

    async_add_entities(entities)
    _LOGGER.info("ProSmart numbers added: %s", [e.name for e in entities])


class ProSmartNumberBase(NumberEntity):
    """Base class for all ProSmart numbers."""

    def __init__(self, auth, device_id, device_name):
        self._auth = auth
        self._device_id = device_id
        self._device_name = device_name

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Computherm / ProSmart",
            "model": "Wi-Fi Thermostat",
        }

    async def _send_cmd(self, json_data):
        """Csak POST-olás, GET nincs."""
        try:
            await self._auth.request(
                "POST",
                f"https://api.prosmartsystem.com/api/devices/{self._device_id}/cmd",
                json=json_data
            )
        except Exception as e:
            _LOGGER.error("Error sending command %s: %s", json_data, e)
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device_id)},
            "name": self._device_name,
            "manufacturer": "Computherm / ProSmart",
            "model": "Wi-Fi Thermostat",
        }


class ProSmartBoostDuration(ProSmartNumberBase):
    def __init__(self, auth, device_id, device_name):
        super().__init__(auth, device_id, device_name)
        self._attr_name = f"{device_name} Boost Duration"
        self._attr_unique_id = f"{device_id}_boost_duration"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 180
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "min"
        self._boost_minutes = 0  # default érték

    @property
    def native_value(self):
        return self._boost_minutes

    async def async_set_native_value(self, value: float):
        self._boost_minutes = int(value)
        self.async_write_ha_state()
        await self._send_cmd({"relay": 1, "boost_time": self._boost_minutes * 60})


class ProSmartBoostTemperature(ProSmartNumberBase):
    def __init__(self, auth, device_id, device_name):
        super().__init__(auth, device_id, device_name)
        self._attr_name = f"{device_name} Boost Temperature"
        self._attr_unique_id = f"{device_id}_boost_temperature"
        self._attr_native_min_value = 5
        self._attr_native_max_value = 35
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "°C"
        self._temperature = 24.0  # default

    @property
    def native_value(self):
        return self._temperature

    async def async_set_native_value(self, value: float):
        self._temperature = round(float(value), 1)
        self.async_write_ha_state()
        await self._send_cmd({"relay": 1, "boost_set_point": self._temperature})


class ProSmartManualTemperature(ProSmartNumberBase):
    def __init__(self, auth, device_id, device_name):
        super().__init__(auth, device_id, device_name)
        self._attr_name = f"{device_name} Manual Temperature"
        self._attr_unique_id = f"{device_id}_manual_temperature"
        self._attr_native_min_value = 5
        self._attr_native_max_value = 35
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "°C"
        self._temperature = 22.0  # default

    @property
    def native_value(self):
        return self._temperature

    async def async_set_native_value(self, value: float):
        self._temperature = round(float(value), 1)
        self.async_write_ha_state()
        await self._send_cmd({"relay": 1, "manual_set_point": self._temperature})

class ProSmartHysteresisHigh(ProSmartNumberBase):
    def __init__(self, auth, device_id, device_name):
        super().__init__(auth, device_id, device_name)
        self._attr_name = f"{device_name} Hysteresis High"
        self._attr_unique_id = f"{device_id}_hysteresis_high"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 20
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "°C"
        self._temperature = 0  # default

    @property
    def native_value(self):
        return self._temperature

    async def async_set_native_value(self, value: float):
        self._temperature = round(float(value), 1)
        self.async_write_ha_state()
        await self._send_cmd({"relay": 1, "hysteresis_high": self._temperature})

class ProSmartHysteresisLow(ProSmartNumberBase):
    def __init__(self, auth, device_id, device_name): 
        super().__init__(auth, device_id, device_name)    
        self._attr_name = f"{device_name} Hysteresis Low"
        self._attr_unique_id = f"{device_id}_hysteresis_low"
        self._attr_native_min_value = 0 
        self._attr_native_max_value = 20
        self._attr_native_step = 0.1
        self._attr_native_unit_of_measurement = "°C"
        self._temperature = 0  # default

    @property
    def native_value(self): 
        return self._temperature

    async def async_set_native_value(self, value: float):
        self._temperature = round(float(value), 1)
        self.async_write_ha_state()
        await self._send_cmd({"relay": 1, "hysteresis_low": self._temperature})

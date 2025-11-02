import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)
DOMAIN = "computherm_b"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration (without config entries)."""
    _LOGGER.info("ProSmart integration loaded (async_setup)")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the integration from a config entry."""
    # Forward setup to sensor and number platforms
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "number", "button"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor", "number", "button"])

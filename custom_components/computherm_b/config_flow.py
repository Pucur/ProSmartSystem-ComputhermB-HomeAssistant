import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required("email"): str,
    vol.Required("password"): str,
})

class ProSmartConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for ProSmart."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            email = user_input["email"]
            password = user_input["password"]

            session = async_get_clientsession(self.hass)  # <--- helyesen
            try:
                async with session.post(
                    "https://api.prosmartsystem.com/api/auth/login",
                    json={"email": email, "password": password},
                    timeout=10
                ) as resp:
                    if resp.status != 200:
                        errors["base"] = "auth"
                    else:
                        data = await resp.json()
                        token = data.get("access_token")
                        if not token:
                            errors["base"] = "auth"
                        else:
                            return self.async_create_entry(title=email, data=user_input)
            except Exception as e:
                _LOGGER.error("Error connecting to ProSmart API: %s", e)
                errors["base"] = "auth"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors
        )

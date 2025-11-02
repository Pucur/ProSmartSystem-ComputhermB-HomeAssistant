import asyncio
import logging

_LOGGER = logging.getLogger(__name__)

class ProSmartAuth:
    """Handles token acquisition and request retries."""

    def __init__(self, session, email, password):
        self.session = session
        self.email = email
        self.password = password
        self.token = None

    async def get_token(self):
        """Return a valid token, logging in if needed."""
        if not self.token:
            await self._login()
        return self.token

    async def _login(self):
        while True:
            try:
                async with self.session.post(
                    "https://api.prosmartsystem.com/api/auth/login",
                    json={"email": self.email, "password": self.password},
                    timeout=10
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    token = data.get("access_token")
                    if token:
                        self.token = token
                        _LOGGER.info("ProSmart login successful")
                        return
                    else:
                        _LOGGER.error("No access token returned, retrying in 10s")
            except Exception as e:
                _LOGGER.warning("Login failed, retrying in 10s: %s", e)
            await asyncio.sleep(10)

    async def request(self, method, url, **kwargs):
        """Make a request with token. Retry on 401 or network errors."""
        while True:
            if not self.token:
                await self._login()
            headers = kwargs.pop("headers", {})
            headers["Authorization"] = f"Bearer {self.token}"
            try:
                async with self.session.request(method, url, headers=headers, **kwargs) as resp:
                    if resp.status == 401:
                        _LOGGER.warning("Token expired, re-login")
                        self.token = None
                        continue
                    resp.raise_for_status()
                    return await resp.json()
            except Exception as e:
                _LOGGER.warning("Request failed, retrying in 10s: %s", e)
                await asyncio.sleep(10)

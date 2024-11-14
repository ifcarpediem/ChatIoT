"""The ChatIoT Conversation integration."""
from __future__ import annotations

from .utils.logs import _logger

_logger.debug(f"Start __init__.py")

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_logger.debug("__init__.py: module import completed")

PLATFORMS = [Platform.CONVERSATION]

_logger.debug(f"Start load {DOMAIN} integration")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    '''安装集成'''
    _logger.debug(f"Start install {DOMAIN} integration")

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    '''卸载集成'''
    _logger.debug(f"Start uninstall {DOMAIN} integration")

    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
"""Platform for light integration."""
from __future__ import annotations

import logging

from .artnet import ArtNet
import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA,
                                            LightEntity, ColorMode)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_USERNAME, default='admin'): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
})


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    
    host = config[CONF_HOST]
    _LOGGER.debug(f"HOST: {host}")
    username = config[CONF_USERNAME]
    password = config.get(CONF_PASSWORD)

    # Setup connection with devices/cloud
    light = ArtNet(host.split(":")[0], int(host.split(":")[1]), [])

    # Add devices
    add_entities([AwesomeLight(light)])


class AwesomeLight(LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, light) -> None:
        """Initialize an AwesomeLight."""
        self._light = light
        self._name = self._light.name
        self._state = None
        self._brightness = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def color_mode(self) -> str:
        return ColorMode.RGB

    @property
    def supported_color_modes(self):
        return [ColorMode.RGB]

    @property
    def rgb_color(self) -> tuple[int, int, int]:
        """Return the rgb color value."""
        return self._light.rgb

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._state

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        _LOGGER.debug(f"Arguments passed to turn_on in light.py {kwargs}")
        if "brightness" in kwargs:
            self._light.set_brightness(kwargs.get("brightness", 255))
        if "rgb_color" in kwargs:
            self._light.set_rgb(kwargs.get("rgb_color", (255,255,255)))

        self._light.turn_on()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._light.turn_off()

    def update(self) -> None:
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        # self._light.update()
        self._state = self._light.is_on
        self._brightness = self._light.brightness
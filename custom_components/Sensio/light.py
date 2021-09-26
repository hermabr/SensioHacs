"""Platform for light integration."""
import logging

import requests

import homeassistant.helpers.config_validation as cv

# Import the device class from the component that you want to support
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    PLATFORM_SCHEMA,
    LightEntity,
    SUPPORT_BRIGHTNESS,
)

# from homeassistant.const import CONF_HOST,

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present

    light_dicts_request = requests.get("http://localhost:6913/getall")  # TODO: FIX HOST

    if light_dicts_request.status_code != 200:
        _LOGGER.error("Could not connect to sensio server")
        return

    # Add devices
    add_entities(
        SensioLight(light_dict) for light_dict in light_dicts_request.json()["lights"]
    )


class SensioLight(LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, light_dict):
        """Initialize an AwesomeLight."""

        self._group_name = light_dict["group_name"]
        self._brightness = light_dict["value"]

    @property
    def name(self):
        """Return the display name of this light."""
        return self._group_name

    @property
    def unique_id(self):
        """Return the unique id of this light."""
        return "sensio." + self._group_name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._brightness

    @property
    def supported_features(self):
        supported_features = SUPPORT_BRIGHTNESS
        return supported_features

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._brightness >= 1

    def turn_on(self, **kwargs):
        """Instruct the light to turn on.

        You can skip the brightness part if your light does not support
        brightness control.
        """
        new_brightness = kwargs.get(ATTR_BRIGHTNESS, 255)

        requests.get(
            f"http://localhost:6913/set?group_name={self._group_name}&value={new_brightness*100/255}"
        )

    def turn_off(self, **kwargs):
        """Instruct the light to turn off."""
        requests.get(f"http://localhost:6913/set?group_name={self._group_name}&value=0")

    def update(self):
        """Fetch new state data for this light.

        This is the only method that should fetch new data for Home Assistant.
        """
        r = requests.get(f"http://localhost:6913/get?group_name={self._group_name}")
        json_data = r.json()

        self._brightness = json_data["value"] * 255 / 100

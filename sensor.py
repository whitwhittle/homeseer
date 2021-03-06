"""
Support for HomeSeer sensor-type devices.
"""
import logging

from homeassistant.const import DEVICE_CLASS_BATTERY
from homeassistant.helpers.entity import Entity
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['homeseer']


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up HomeSeer sensor-type devices."""
    from pyhs3 import HASS_SENSORS, DEVICE_ZWAVE_BATTERY

    sensor_devices = []
    homeseer = hass.data[DOMAIN]

    for device in homeseer.devices:
        if device.device_type_string in HASS_SENSORS:
            if device.device_type_string == DEVICE_ZWAVE_BATTERY:
                dev = HSBattery(device, homeseer)
            else:
                dev = HSSensor(device, homeseer)
            sensor_devices.append(dev)
            _LOGGER.info('Added HomeSeer sensor-type device: {}'.format(dev.name))

    async_add_entities(sensor_devices)


class HSSensor(Entity):
    """Representation of a HomeSeer sensor-type device."""
    def __init__(self, device, connection):
        self._device = device
        self._connection = connection

    @property
    def available(self):
        """Return whether the device is available."""
        from pyhs3 import STATE_LISTENING
        return self._connection.api.state == STATE_LISTENING

    @property
    def device_state_attributes(self):
        attr = {
            'Device Ref': self._device.ref
        }
        return attr

    @property
    def name(self):
        """Return the name of the device."""
        if self._connection.location_names:
            return '{} {} {}'.format(self._device.location2, self._device.location, self._device.name)
        else:
            return self._device.name

    @property
    def state(self):
        """Return the state of the device."""
        return self._device.value

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    async def async_added_to_hass(self):
        """Register value update callback."""
        self._device.register_update_callback(self.async_schedule_update_ha_state)


class HSBattery(HSSensor):

    @property
    def unit_of_measurement(self):
        return '%'

    @property
    def icon(self):
        if self.state == 100:
            return 'mdi:battery'
        elif self.state > 89:
            return 'mdi:battery-90'
        elif self.state > 79:
            return 'mdi:battery-80'
        elif self.state > 69:
            return 'mdi:battery-70'
        elif self.state > 59:
            return 'mdi:battery-60'
        elif self.state > 49:
            return 'mdi:battery-50'
        elif self.state > 39:
            return 'mdi:battery-40'
        elif self.state > 29:
            return 'mdi:battery-30'
        elif self.state > 19:
            return 'mdi:battery-20'
        elif self.state > 9:
            return 'mdi:battery-10'

    @property
    def device_class(self):
        return DEVICE_CLASS_BATTERY

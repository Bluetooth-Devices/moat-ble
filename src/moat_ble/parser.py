"""Parser for Moat BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/moat.py

MIT License applies.
"""

from __future__ import annotations

import logging
from struct import unpack

from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import SensorLibrary

_LOGGER = logging.getLogger(__name__)


MOAT_S2_SERVICE_DATA_UUID = "00001000-0000-1000-8000-00805f9b34fb"


def short_address(address: str) -> str:
    """Convert a Bluetooth address to a short address."""
    results = address.replace("-", ":").split(":")
    if len(results[-1]) == 2:
        return f"{results[-2].upper()}{results[-1].upper()}"
    return results[-1].upper()


class MoatBluetoothDeviceData(BluetoothData):
    """Date update for Moat Bluetooth devices."""

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing moat BLE advertisement data: %s", service_info)
        service_data = service_info.service_data
        if not service_data or MOAT_S2_SERVICE_DATA_UUID not in service_data:
            return
        address = service_info.address
        self.set_device_manufacturer("Moat")
        data = service_data[MOAT_S2_SERVICE_DATA_UUID]
        _LOGGER.debug("Parsing Moat BLE advertisement data: %s", data)
        if "moat_s2" in service_info.name.lower():
            self.set_device_type("Moat S2")
            self.set_device_name(f"Moat S2 {short_address(address)}")
            (temp, humi, volt) = unpack("<HHH", data[10:16])
            temperature = -46.85 + 175.72 * temp / 65536.0
            humidity = -6.0 + 125.0 * humi / 65536.0
            voltage = volt / 1000
            if volt >= 3000:
                batt = 100
            elif volt >= 2900:
                batt = 42 + (volt - 2900) * 0.58
            elif volt >= 2740:
                batt = 18 + (volt - 2740) * 0.15
            elif volt >= 2440:
                batt = 6 + (volt - 2440) * 0.04
            elif volt >= 2100:
                batt = (volt - 2100) * (6 / 340)
            else:
                batt = 0
            self.update_predefined_sensor(
                SensorLibrary.TEMPERATURE__CELSIUS, round(temperature, 3)
            )
            self.update_predefined_sensor(
                SensorLibrary.HUMIDITY__PERCENTAGE, round(humidity, 3)
            )
            self.update_predefined_sensor(
                SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT, voltage
            )
            self.update_predefined_sensor(
                SensorLibrary.BATTERY__PERCENTAGE, round(batt, 1)
            )

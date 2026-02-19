#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# You may find it more helpful to your design to adjust the
# functionality, constants and interfaces (if there are any)
# provided within in order to meet the needs of your specific
# Programming the Internet of Things project.
# 

import logging

from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator
from programmingtheiot.data.SensorData import SensorData

class HumidityI2cSensorAdapterTask():
	"""
	Shell representation of class for student implementation.
	
	"""

	def __init__(self):
		super(HumidityI2cSensorAdapterTask, self).__init__(typeID = 
		SensorData.HUMIDITY_SENSOR_TYPE, minVal = SensorDataGenerator.LOW_NORMAL_ENV_HUMIDITY, 
		maxVal = SensorDataGenerator.HI_NORMAL_ENV_HUMIDITY)

		self.sensorType = SensorData.HUMIDITY_SENSOR_TYPE

		# Example only: Read the spec for the SenseHAT humidity sensor to obtain the appropriate starting address and use i2c-tools to verify.
		self.humidAddr = 0x5F

		# init the I2C bus at the humidity address
		# WARNING: only use I2C bus 1 when working with the SenseHAT on the Raspberry Pi!!
		self.i2cBus = smbus.SMBus(1)
		self.i2cBus.write_byte_data(self.humidAddr, 0, 0)
	
	def generateTelemetry(self) -> SensorData:
		pass
	
	def getTelemetryValue(self) -> float:
		pass
	
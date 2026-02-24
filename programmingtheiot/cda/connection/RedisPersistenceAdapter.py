"""
RedisPersistenceAdapter.py

Simple Redis persistence adapter for CDA.
Stores SensorData (and optionally ActuatorData) using Redis.
"""

import logging
import json
import redis

from programmingtheiot.common.ConfigConst import ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.model.SensorData import SensorData

# You can also move this to ConfigConst if preferred
DATA_GATEWAY_SERVICE = "Data.GatewayService"

class RedisPersistenceAdapter:
    """
    Simple adapter for persisting data to Redis.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = ConfigUtil()

        # Get configuration properties
        self.host = self.config.getProperty(
            DATA_GATEWAY_SERVICE,
            ConfigConst.HOST_KEY
        )

        self.port = self.config.getInteger(
            DATA_GATEWAY_SERVICE,
            ConfigConst.PORT_KEY
        )

        self.logger.info(f"Redis host: {self.host}")
        self.logger.info(f"Redis port: {self.port}")

        # Create Redis client
        self.client = redis.Redis(
            host=self.host,
            port=self.port,
            decode_responses=True
        )

        self.isConnected = False

    # -------------------------------------------------------
    # Connection Management
    # -------------------------------------------------------

    def connectClient(self) -> bool:
        if self.isConnected:
            self.logger.warning("Redis client already connected.")
            return True

        try:
            # Ping to test connection
            self.client.ping()
            self.isConnected = True
            self.logger.info("Connected to Redis successfully.")
            return True

        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            return False

    def disconnectClient(self) -> bool:
        if not self.isConnected:
            self.logger.warning("Redis client already disconnected.")
            return True

        try:
            # redis-py does not require explicit close in older versions,
            # but close() exists in newer versions
            self.client.close()
            self.isConnected = False
            self.logger.info("Disconnected from Redis successfully.")
            return True

        except Exception as e:
            self.logger.error(f"Failed to disconnect from Redis: {e}")
            return False

    # -------------------------------------------------------
    # Data Storage
    # -------------------------------------------------------

    def storeData(self, resource: ResourceNameEnum, data: SensorData) -> bool:
        """
        Store SensorData (or ActuatorData) in Redis.

        Uses ResourceNameEnum as key.
        Stores JSON string.
        """

        if not self.isConnected:
            self.logger.warning("Cannot store data - client not connected.")
            return False

        try:
            # Convert object to dictionary
            payload = data.__dict__

            # Convert to JSON
            jsonData = json.dumps(payload)

            # Use resource name as Redis key
            key = resource.name

            self.client.set(key, jsonData)

            self.logger.info(f"Stored data in Redis under key: {key}")
            return True

        except Exception as e:
            self.logger.error(f"Error storing data in Redis: {e}")
            return False
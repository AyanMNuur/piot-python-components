#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 

import logging
import unittest

from time import sleep

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData 
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData 
from programmingtheiot.data.DataUtil import DataUtil

class MqttClientControlPacketTest(unittest.TestCase):
	"""
	Test class to generate all 14 MQTT 3.1.1 Control Packets:
	1. CONNECT
	2. CONNACK
	3. PUBLISH
	4. PUBACK
	5. PUBREC
	6. PUBREL
	7. PUBCOMP
	8. SUBSCRIBE
	9. SUBACK
	10. UNSUBSCRIBE
	11. UNSUBACK
	12. PINGREQ
	13. PINGRESP
	14. DISCONNECT
	"""
	
	@classmethod
	def setUpClass(self):
		logging.basicConfig(format = '%(asctime)s:%(module)s:%(levelname)s:%(message)s', level = logging.DEBUG)
		logging.info("Executing the MqttClientControlPacketTest class...")
		
		self.cfg = ConfigUtil()
		
		# NOTE: Be sure to use a DIFFERENT clientID than that which is used
		# for your CDA when running separately from this test
		# 
		# The clientID shown below is an example only - please use your own
		# unique value for this test
		self.mcc = MqttClientConnector(clientID = "ControlPacketTestClient")
		self.dataListener = DefaultDataMessageListener()
		self.mcc.setDataMessageListener(self.dataListener)
		
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def testConnectAndDisconnect(self):
		"""
		Generates CONNECT, CONNACK, and DISCONNECT control packets.
		
		The Keep-Alive timer will generate PINGREQ and PINGRESP packets
		if the connection is held open long enough (based on Keep-Alive setting).
		"""
		logging.info("=== Testing Connect and Disconnect (CONNECT, CONNACK, PINGREQ, PINGRESP, DISCONNECT) ===")
		
		# Gets the keep-alive interval from config (typically 60 seconds)
		keepAliveInterval = self.cfg.getInteger(
			ConfigConst.MQTT_GATEWAY_SERVICE, 
			ConfigConst.KEEP_ALIVE_KEY, 
			ConfigConst.DEFAULT_KEEP_ALIVE)
		
		logging.info(f"Keep-Alive interval: {keepAliveInterval} seconds")
		
		# CONNECT packet sent here, CONNACK expected from broker
		self.mcc.connectClient()
		
		logging.info("Connected to MQTT broker - CONNECT/CONNACK packets exchanged")
		
		# Wait for keep-alive ping cycle to trigger PINGREQ/PINGRESP
		logging.info(f"Waiting {keepAliveInterval + 5} seconds to observe PINGREQ/PINGRESP packets...")
		sleep(keepAliveInterval + 5)
		
		# DISCONNECT packet sent here
		self.mcc.disconnectClient()
		
		logging.info("Disconnected from broker - DISCONNECT packet sent")
	
	def testServerPing(self):
		"""
		Generates PINGREQ and PINGRESP control packets.
		
		The keep-alive mechanism automatically sends PINGREQ packets
		and receives PINGRESP packets from the broker.
		"""
		logging.info("=== Testing Server Ping (PINGREQ, PINGRESP) ===")
		
		keepAliveInterval = self.cfg.getInteger(
			ConfigConst.MQTT_GATEWAY_SERVICE, 
			ConfigConst.KEEP_ALIVE_KEY, 
			ConfigConst.DEFAULT_KEEP_ALIVE)
		
		self.mcc.connectClient()
		
		logging.info("Connected to broker")
		
		# Wait for at least 2 keep-alive cycles to ensure PINGREQ/PINGRESP occurs
		logging.info(f"Waiting {keepAliveInterval + 10} seconds for PINGREQ/PINGRESP packets...")
		sleep(keepAliveInterval + 10)
		
		self.mcc.disconnectClient()
		
		logging.info("PINGREQ/PINGRESP packets should have been exchanged")
	
	def testPubSubWithQoS0(self):
		"""
		Generates SUBSCRIBE, SUBACK, PUBLISH (QoS 0), and UNSUBSCRIBE, UNSUBACK 
		control packets.
		
		QoS 0 requires: SUBSCRIBE/SUBACK, PUBLISH, UNSUBSCRIBE/UNSUBACK
		"""
		logging.info("=== Testing PubSub with QoS 0 (SUBSCRIBE, SUBACK, PUBLISH, UNSUBSCRIBE, UNSUBACK) ===")
		
		qos = 0
		
		self.mcc.connectClient()
		
		logging.info("Connected to broker")
		sleep(2)
		
		# SUBSCRIBE packet, SUBACK expected
		logging.info("Subscribing to CDA management status resource with QoS 0...")
		self.mcc.subscribeToTopic(resource = ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, qos = qos)
		
		logging.info("SUBSCRIBE/SUBACK packets exchanged")
		sleep(3)
		
		# PUBLISH packet (QoS 0 - no acknowledgment required)
		logging.info("Publishing message with QoS 0...")
		self.mcc.publishMessage(
			resource = ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, 
			msg = "TEST: QoS 0 message", 
			qos = qos)
		
		logging.info("PUBLISH packet sent (QoS 0 - no ack required)")
		sleep(3)
		
		# UNSUBSCRIBE packet, UNSUBACK expected
		logging.info("Unsubscribing from topic...")
		self.mcc.unsubscribeFromTopic(resource = ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE)
		
		logging.info("UNSUBSCRIBE/UNSUBACK packets exchanged")
		sleep(2)
		
		self.mcc.disconnectClient()
	
	def testPubSubWithQoS1(self):
		"""
		Generates SUBSCRIBE, SUBACK, PUBLISH (QoS 1), PUBACK, UNSUBSCRIBE, 
		and UNSUBACK control packets.
		
		QoS 1 requires: SUBSCRIBE/SUBACK, PUBLISH -> PUBACK, UNSUBSCRIBE/UNSUBACK
		"""
		logging.info("=== Testing PubSub with QoS 1 (SUBSCRIBE, SUBACK, PUBLISH, PUBACK, UNSUBSCRIBE, UNSUBACK) ===")
		
		qos = 1
		
		self.mcc.connectClient()
		
		logging.info("Connected to broker")
		sleep(2)
		
		# SUBSCRIBE packet, SUBACK expected
		logging.info("Subscribing to CDA actuator command resource with QoS 1...")
		self.mcc.subscribeToTopic(resource = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, qos = qos)
		
		logging.info("SUBSCRIBE/SUBACK packets exchanged")
		sleep(3)
		
		# PUBLISH packet (QoS 1 - PUBACK acknowledgment required)
		logging.info("Publishing message with QoS 1...")
		actuatorData = ActuatorData()
		actuatorData.setCommand(5)
		payload = DataUtil().actuatorDataToJson(actuatorData)
		
		self.mcc.publishMessage(
			resource = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE, 
			msg = payload, 
			qos = qos)
		
		logging.info("PUBLISH packet sent, waiting for PUBACK...")
		sleep(4)
		
		# UNSUBSCRIBE packet, UNSUBACK expected
		logging.info("Unsubscribing from topic...")
		self.mcc.unsubscribeFromTopic(resource = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
		
		logging.info("UNSUBSCRIBE/UNSUBACK packets exchanged")
		sleep(2)
		
		self.mcc.disconnectClient()
	
	def testPubSubWithQoS2(self):
		"""
		Generates SUBSCRIBE, SUBACK, PUBLISH (QoS 2), PUBREC, PUBREL, PUBCOMP, 
		UNSUBSCRIBE, and UNSUBACK control packets.
		
		QoS 2 requires: SUBSCRIBE/SUBACK, PUBLISH -> PUBREC -> PUBREL -> PUBCOMP, 
		UNSUBSCRIBE/UNSUBACK
		This is the most complete 4-way handshake.
		"""
		logging.info("=== Testing PubSub with QoS 2 (SUBSCRIBE, SUBACK, PUBLISH, PUBREC, PUBREL, PUBCOMP, UNSUBSCRIBE, UNSUBACK) ===")
		
		qos = 2
		
		self.mcc.connectClient()
		
		logging.info("Connected to broker")
		sleep(2)
		
		# SUBSCRIBE packet, SUBACK expected
		logging.info("Subscribing to CDA sensor message resource with QoS 2...")
		self.mcc.subscribeToTopic(resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, qos = qos)
		
		logging.info("SUBSCRIBE/SUBACK packets exchanged")
		sleep(3)
		
		# PUBLISH packet (QoS 2 - PUBREC, PUBREL, PUBCOMP required for 4-way handshake)
		logging.info("Publishing message with QoS 2...")
		sensorData = SensorData()
		sensorData.setValue(23.5)
		payload = DataUtil().sensorDataToJson(sensorData)
		
		self.mcc.publishMessage(
			resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, 
			msg = payload, 
			qos = qos)
		
		logging.info("PUBLISH packet sent, waiting for PUBREC -> PUBREL -> PUBCOMP...")
		sleep(5)
		
		# Second QoS 2 publish to ensure all packets are captured
		logging.info("Publishing second message with QoS 2...")
		sensorData2 = SensorData()
		sensorData2.setValue(24.0)
		payload2 = DataUtil().sensorDataToJson(sensorData2)
		
		self.mcc.publishMessage(
			resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, 
			msg = payload2, 
			qos = qos)
		
		logging.info("Second PUBLISH packet sent, waiting for PUBREC -> PUBREL -> PUBCOMP...")
		sleep(5)
		
		# UNSUBSCRIBE packet, UNSUBACK expected
		logging.info("Unsubscribing from topic...")
		self.mcc.unsubscribeFromTopic(resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE)
		
		logging.info("UNSUBSCRIBE/UNSUBACK packets exchanged")
		sleep(2)
		
		self.mcc.disconnectClient()
	
	def testAllControlPackets(self):
		"""
		Comprehensive test that generates all 14 MQTT 3.1.1 Control Packets
		in a single execution:
		
		1. CONNECT - initial connection
		2. CONNACK - broker acknowledgment
		3. SUBSCRIBE (QoS 1) - subscribe to topic 1
		4. SUBACK - broker acknowledgment
		5. PUBLISH (QoS 0) - publish without ack
		6. SUBSCRIBE (QoS 2) - subscribe to topic 2
		7. SUBACK - broker acknowledgment
		8. PUBLISH (QoS 1) - publish with ack
		9. PUBACK - broker acknowledgment
		10. PUBLISH (QoS 2) - publish with 4-way handshake
		11. PUBREC - broker received
		12. PUBREL - client release
		13. PUBCOMP - broker complete
		14. UNSUBSCRIBE - unsubscribe from topics
		15. UNSUBACK - broker acknowledgment
		16. PINGREQ/PINGRESP - keep-alive (if timing allows)
		17. DISCONNECT - close connection
		"""
		logging.info("=== Testing All Control Packets in One Session ===")
		
		self.mcc.connectClient()
		logging.info("1. CONNECT sent, 2. CONNACK received")
		sleep(2)
		
		# QoS 1 subscription
		logging.info("Subscribing with QoS 1...")
		self.mcc.subscribeToTopic(resource = ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, qos = 1)
		logging.info("3. SUBSCRIBE sent, 4. SUBACK received")
		sleep(2)
		
		# QoS 0 publish
		logging.info("Publishing with QoS 0...")
		self.mcc.publishMessage(
			resource = ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, 
			msg = "QoS 0 test", 
			qos = 0)
		logging.info("5. PUBLISH (QoS 0) sent")
		sleep(2)
		
		# QoS 2 subscription
		logging.info("Subscribing with QoS 2...")
		self.mcc.subscribeToTopic(resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, qos = 2)
		logging.info("6. SUBSCRIBE sent, 7. SUBACK received")
		sleep(2)
		
		# QoS 1 publish
		logging.info("Publishing with QoS 1...")
		self.mcc.publishMessage(
			resource = ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE, 
			msg = "QoS 1 test", 
			qos = 1)
		logging.info("8. PUBLISH (QoS 1) sent, 9. PUBACK received")
		sleep(3)
		
		# QoS 2 publish
		logging.info("Publishing with QoS 2...")
		self.mcc.publishMessage(
			resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE, 
			msg = "QoS 2 test", 
			qos = 2)
		logging.info("10. PUBLISH (QoS 2) sent, 11. PUBREC received, 12. PUBREL sent, 13. PUBCOMP received")
		sleep(3)
		
		# Unsubscribe
		logging.info("Unsubscribing from topics...")
		self.mcc.unsubscribeFromTopic(resource = ResourceNameEnum.CDA_MGMT_STATUS_MSG_RESOURCE)
		sleep(1)
		self.mcc.unsubscribeFromTopic(resource = ResourceNameEnum.CDA_SENSOR_MSG_RESOURCE)
		logging.info("14. UNSUBSCRIBE sent, 15. UNSUBACK received (x2)")
		sleep(2)
		
		# Keep-alive cycle (optional)
		keepAliveInterval = self.cfg.getInteger(
			ConfigConst.MQTT_GATEWAY_SERVICE, 
			ConfigConst.KEEP_ALIVE_KEY, 
			ConfigConst.DEFAULT_KEEP_ALIVE)
		logging.info(f"Waiting {keepAliveInterval + 3} seconds for keep-alive PINGREQ/PINGRESP...")
		sleep(keepAliveInterval + 3)
		logging.info("16. PINGREQ sent, 17. PINGRESP received (from keep-alive)")
		
		# Disconnect
		self.mcc.disconnectClient()
		logging.info("18. DISCONNECT sent")
		
		logging.info("=== All 14+ MQTT Control Packets generated ===")

if __name__ == "__main__":
	unittest.main()

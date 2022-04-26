import time
import paho.mqtt.client as mqtt
import logging


class Publisher:
    def __init__(self, access):
        self.logger = logging.getLogger(__name__)

        self.mqttc = mqtt.Client(client_id=self.getserial(), clean_session=False)
        self.mqttc.enable_logger(self.logger)
        self.mqttc.username_pw_set(access, None)
        self.mqttc.connect("mqtt.thingsboard.cloud", 1883, 0)

        self.mqttc.loop_start()

    def getserial(self):
    # Extract serial from cpuinfo file
        cpuserial = "0000000000001234"
        try:
            f = open('/proc/cpuinfo','r')
            for line in f:
                if line[0:6]=='Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"

        self.logger.debug('Serial number: ' + cpuserial)

        return cpuserial

    def send_message(self, a_message):
        infot = self.mqttc.publish('v1/devices/me/telemetry', a_message, qos=1)
        try:
            infot.wait_for_publish(2)
            return True  # We have not really checked if it worked
        except RuntimeError:  # This is very intermittent
            self.logger.warning('Could not publish MQTT message - no internet.')
            return False

    def stop(self):
        self.mqttc.disconnect()

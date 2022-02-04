import serial

from pms7003 import Pms7003Sensor, PmsSensorException
from pms7003.TimeAverager import DictAverager
from pms7003.publisher import Publisher

serial_port = '/dev/serial0'
serial_device = serial.Serial(port=serial_port, baudrate=9600, bytesize=serial.EIGHTBITS,
                              parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=2)

if __name__ == '__main__':

    sensor = Pms7003Sensor(serial_device)
    pub = Publisher()
    dict_averager = None

    started = False


    def call_on_count(latest, delta_t):
        message = str(latest)
        pub.send_message(message)
        print('Delta t: ' + str(delta_t))


    while True:
        try:
            latest, latest_labelled = sensor.read()
            if not started:
                dict_averager = DictAverager(latest_labelled, 10, call_on_count)
            else:
                dict_averager.update(latest_labelled)
            print(latest_labelled)
            print(latest)
        except PmsSensorException:
            print('Wrong frame length or non-byte value, connection problem?')

    sensor.close()
    pub.stop()
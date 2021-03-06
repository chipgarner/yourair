import logging
import logging.handlers
import os
from publish.publisher import Publisher
import save.saver
from Secrets import SECRET  # Credential string for MQTT on Thingsboard - don't put credentials in Git


from sense.sensors import PmsSensor

try:
    from display.display import Display
    display = True
except ModuleNotFoundError:
    display = False  # Assuming this means no display is installed

from publish.publish import Publish
from save.save import Save


class RunMePms7003:
    def __init__(self):
        log_format = '%(asctime)s %(name)s %(message)s'
        logging.basicConfig(format=log_format,
                            datefmt='%m/%d/%Y %I:%M:%S %p',
                            level=logging.DEBUG)
        self.logger = logging.getLogger()

        directory_path = os.path.dirname(__file__)
        formatter = logging.Formatter(log_format, datefmt='%m/%d/%Y %I:%M:%S %p')

        file_path = directory_path + '/warning.log'
        warning_log_handler = logging.handlers.TimedRotatingFileHandler(file_path, when='D', interval=1,
                                                                        backupCount=5, utc=True)
        warning_log_handler.setLevel(logging.WARNING)
        warning_log_handler.setFormatter(formatter)
        self.logger.addHandler(warning_log_handler)

        file_path = directory_path + '/debug.log'
        debug_log_handler = logging.handlers.TimedRotatingFileHandler(file_path, when='D', interval=1,
                                                                      backupCount=5, utc=True)
        debug_log_handler.setLevel(logging.DEBUG)
        debug_log_handler.setFormatter(formatter)
        self.logger.addHandler(debug_log_handler)

        self.sensors = PmsSensor()

        if display:
            self.display = Display()
        else:
            self.logger.warning('Could not import display, assuming there is none.')
            self.display = None

        self.publish = Publish(Publisher(SECRET))
        saver = save.saver.Saver()
        self.save = Save(saver)

        self.running = True

    def loop(self):
        self.logger.info('Starting loop')
        while self.running:
            latest = self.sensors.get_latest()
            if self.display is not None:
                self.display.display(latest)
            self.publish.publish(latest)
            self.save.save(latest)

        self.logger.error('Exited main loop')
        self.sensors.stop()


if __name__ == '__main__':
    runner = RunMePms7003()
    runner.loop()

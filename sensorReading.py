"""Class to hold a single reading from a sensor.
"""
from datetime import datetime

class SensorReading(object):
    def __init__(self, s_name, s_type, timestamp, value):
        self.sensor_name = s_name
        self.sensor_type = s_type
        self.timestamp = timestamp
        self.value = value
        return

    def __str__(self):
        s = "(name='{}', type='{}', timestamp='{}', " \
            "value={})".format(self.sensor_name, self.sensor_type, self.timestamp, self.value)
        return s

    def get_name(self):
        return self.sensor_name

    def get_type(self):
        return self.sensor_type

    def get_timestamp(self):
        return self.timestamp

    def get_value(self):
        return self.value

    def as_dict(self):
        return {'name': self.sensor_name, 'type': self.sensor_type, 'timestamp': self.timestamp, 'value': self.value}

# TODO implement as_JSON() method for SensorReading class

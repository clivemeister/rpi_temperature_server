import random
from abc import ABC, abstractmethod
from datetime import datetime


class Sensor(ABC):
    """A sensor attached to the system, of a particular type, able to return its data value.
       Subclass this and override the value() method for a particular implementation.
    Attributes:
        sensor_type:  A string with the type of sensor
        name: A string with the unique name of this particular sensor
        value: current reading of sensor, in units appropriate to its type
    """

    def __init__(self, name):
        self.name = name
        self.value = -1
        self.sensor_type = "abstract sensor"

    @classmethod
    @abstractmethod
    def get_reading(self):
        """return the current sensor reading for this sensor instance"""
        pass

    def get_type(self):
        return self.sensor_type

    def get_name(self):
        return self.name


class TemperatureSensor(Sensor):
    """A temperature sensor"""
    sensor_type = "temperature"

    def get_reading(self):
        r = SensorReading(s_name=self.name, s_type=self.sensor_type,
                          timestamp=datetime.now(), value=random.randint(-5, 25))
        # TODO work out how to get a real temperature reading in here, by instance
        return r


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

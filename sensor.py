import random
from abc import ABC, abstractmethod

class Sensor(ABC):
    """A sensor attached to the system, of a particular type, able to return its data value.
       Subclass this and override the value() method for a particular implementation.
    Attributes:
        type:  A string with the type of sensor
        name: A string with the unique name of this particular sensor
        value: current reading of sensor, in units appropriate to its type
    """

    sensor_type="abstract sensor"

    def __init__(self,name):
        self.name = name
        self.value = -1

    @classmethod
    @abstractmethod
    def get_reading(self):
        """return the current sensor reading for this sensor instance"""
        pass

    def get_type(self):
        return self.sensor_type

    def get_name(self):
        return self.name

class Temperature_sensor(Sensor):
    """A temperature sensor"""
    sensor_type="temperature"

    def get_reading(self):
        return random.randint(-5,25)
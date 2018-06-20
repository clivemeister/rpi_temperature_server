import random
from abc import ABC, abstractmethod
from datetime import datetime
from sensorReading import SensorReading

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

    # these are used when we need to fake the temperature setting
    last_temp = 4.0  
    fan_on = False

    def get_reading(self):
        temperature = 0.0
        try:
            import smbus
            # 0 for /dev/i2c-0,  1 for /dev/i2c-1
            I2C_BUS = 1
            bus = smbus.SMBus(I2C_BUS)
                
            #7 bit address (will be left shifted to add the read write bit)
            DEVICE_ADDRESS = 0x48      

            #Read the temp register
            temp_reg_12bit = bus.read_word_data(DEVICE_ADDRESS , 0 )
            temp_low = (temp_reg_12bit & 0xff00) >> 8
            temp_high = (temp_reg_12bit & 0x00ff)
            #convert to temp from page 6 of datasheet
            temp  = ((( temp_high * 256 ) + temp_low) >> 4 )
            #handle negative temps
            if temp > 0x7FF:
                    temp = temp-4096;
            temperature = float(temp) * 0.0625
        except ModuleNotFoundError:
            if (TemperatureSensor.fan_on):
                temperature = float(TemperatureSensor.last_temp) - random.randint(15,18)/10.0
                if (temperature <= 2.5):
                    TemperatureSensor.fan_on = False
            else:
                temperature = float(TemperatureSensor.last_temp) + random.randint(2,5)/10.0
                if (temperature >= 11.5):
                    TemperatureSensor.fan_on = True
            TemperatureSensor.last_temp = temperature
            # print("No sensor.  Using randint(-5,25)=%i for temperature reading"%(temperature))
        
        r = SensorReading(s_name=self.name, s_type=self.sensor_type,
                          timestamp=datetime.now(), value=temperature)
        return r



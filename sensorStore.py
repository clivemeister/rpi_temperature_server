"""Responsible for storing and retrieving sensor data to a non-volatile database
"""
import sqlite3

from datetime import datetime
from sensorReading import SensorReading

class SensorStore(object):

    def __init__(self):
        try:
            # Creates or opens a file called mydb with a SQLite3 DB
            self.db = sqlite3.connect('sensorData.db')
            self.db_open = True
            cursor = self.db.cursor()
            # Check if table users does not exist and create it
            cursor.execute('''CREATE TABLE IF NOT EXISTS
                          readings(sensor_name TEXT NOT NULL, created_at timestamp NOT NULL, 
                          reading_type TEXT, value INTEGER)''')
            # Commit the change
            self.db.commit()
        # Catch the exception
        except Exception as e:
            # Roll back any change if something goes wrong
            self.db.rollback()
            raise e
        return

    def add_reading(self, sensor_name, when, reading_type, value):
        try:
            with self.db:
                self.db.execute('''INSERT INTO readings(sensor_name, created_at, reading_type, value) 
                                VALUES(?,?,?,?)''',
                                (sensor_name, when, reading_type, value))
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        return

    def get_readings(self, count=10):
        """Retrieve the most recent <count> readings (default 10) from the store
           Returns: a list of SensorReading
        """
        rdr = []
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT sensor_name, created_at, reading_type, value 
                                    FROM readings
                                    ORDER BY created_at DESC
                                    LIMIT ?''', (count,))
                for row in cursor:
                    rdr.insert(0, SensorReading(s_name=row[0], s_type=row[2], timestamp=datetime.strptime(row[1],"%Y-%m-%d %H:%M:%S.%f"), value=row[3]))
        except Exception as e:
            # TODO do better error processing if no data retrieved from db
            raise e
        return rdr

    def get_readings_as_dicts(self, count=10):
        rdr = self.get_readings(count)
        r_as_dicts = []
        for i in rdr:
            r_as_dicts.append(i.as_dict())
        return r_as_dicts

    def get_readings_for_sensor(self, sensor_name, count=10):
        rdr = []
        try:
            with self.db:
                cursor = self.db.cursor()
                cursor.execute('''SELECT sensor_name, created_at, reading_type, value 
                                    FROM readings 
                                    WHERE (sensor_name=?)
                                    ORDER BY created_at DESC
                                    LIMIT ?''', (sensor_name, count)
                               )
                for row in cursor:
                    rdr.insert(0, SensorReading(s_name=row[0], s_type=row[2], timestamp=datetime.strptime(row[1],"%Y-%m-%d %H:%M:%S.%f"), value=row[3]))
        except Exception as e:
            # TODO do better error processing if no data retrieved from db
            raise e
        return rdr

    def close(self):
        if self.db_open:
            self.db.close()
            self.db_open = False
        return

    def __del__(self):
        # Close the db connection
        self.close()
        return


# Run some tests if we are actually invoked from the command line
if __name__ == '__main__':
    from datetime import datetime, timedelta

    print("Running SensorStore test cases")
    store = SensorStore()
    print("...created store")
    now = datetime.now()
    delta = timedelta(seconds=1)
    one_sec_ago = now - delta
    store.add_reading("test sensor", one_sec_ago, "temperature", 17)
    print("written a value of 17 for <test sensor> at timestamp {}".format(one_sec_ago))
    store.add_reading("test sensor", now, "temperature", 18)
    print("written a value of 18 for <test sensor> at timestamp {}".format(now))
    readings = store.get_readings(2)
    print("Read back 2 readings:")
    for r in readings:
        print(r)
    store.close()
    print("Closed store")

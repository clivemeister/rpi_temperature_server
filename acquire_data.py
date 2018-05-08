""" Reads the sensors and writes the results to the database
        -h             print this help text
        --pause=10          reads the sensors every 10 seconds (default: 5 seconds)
        --iters=25          run for 25 sets of sensor readings, then exit (default: 12 sets)
        --log=d/i/w   run with this level of debugging.  Options d,i,w (default: warning)
"""
import sys
import logging
import getopt
import time
from sensor import TemperatureSensor
from sensorStore import SensorStore
import json

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(message)s",
                    stream=sys.stdout)

logger = logging.getLogger('acquire_data')

# set defaults
pause_time = 2        # read sensors every 5 seconds by default
max_iterations = 5      # read sensors this many times before stopping (if -1,then never stop)


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        logging.debug("Parsing arguments")
        try:
            opts, extra_args = getopt.getopt(argv[1:], "h", ["help", "debug=", "iters=", "pause="])
        except getopt.GetoptError:
            print(__doc__)
            raise Usage("Help, unable to get options!")
        parse_args(opts)
    except Usage:
        print("for help, use --help")
        return 2

    global pause_time
    global max_iterations

    logging.info("Starting run with interval time of {} seconds for {} iterations".format(pause_time, max_iterations))
    store = SensorStore()

    # TODO switch to real sensors
    sensor_list = [TemperatureSensor("thermometer 1"), TemperatureSensor("thermometer 2")]

    iteration = 1    # count for current iteration
    while max_iterations == -1 or iteration <= max_iterations:
        if iteration > 1:
            logging.info("Pausing for {} seconds".format(pause_time))
            time.sleep(pause_time)
        sensor_readings = read_sensors(sensor_list)
        store_sensor_readings(store, sensor_readings)
        iteration += 1   # starting next iteration
        logging.info("Completed iteration {}".format(iteration))

    # TODO here we should be streaming the data back to the server
    readings = store.get_readings_as_dicts(10)
    print("Read back last few readings:")
    print(json.dumps(readings, indent=2))
        
    store.close()
    return


def parse_args(opts):
    global pause_time
    global max_iterations

    for opt, arg in opts:
        logging.debug("Option switch {} with argument {}".format(opt, arg))
        if opt in ("-h", "--help"):
            print(__doc__)
            raise Usage("help given")
        elif opt == "--log":
            lvl = arg
            logging.debug("Found argument -log with option {}".format(arg))
            if lvl == "d":
                logger.setLevel(logging.DEBUG)
            elif lvl == "i":
                logger.setLevel(logging.INFO)
            elif lvl == "w":
                logger.setLevel(logging.WARNING)
        elif opt == "--pause":
            pause_time = int(arg)
            logging.debug("Pause time set to {}".format(pause_time))
        elif opt in "--iters":
            max_iterations = int(arg)
            logging.debug("Max iterations set to {}".format(max_iterations))
        else:
            assert False, "unhandled commandline argument"
    return


def read_sensors(sensor_list):
    logging.info(">>reading sensors")
    sensor_readings = []
    for s in sensor_list:
        sensor_readings.append(s.get_reading())
    return sensor_readings


def store_sensor_readings(store, readings):
    logging.info(">>storing sensor readings: {}".format(readings))
    for r in readings:
        store.add_reading(sensor_name=r.get_name(), when=r.get_timestamp(),
                          reading_type=r.get_type(), value=r.get_value())
    return


if __name__ == '__main__':
    sys.exit(main())

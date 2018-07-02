"""
iot_fridge: when run as main, starts web server and kicks off background thread that
reads sensors every few seconds, writing to database.
 - Web page /livedata does http GET to retrieve the last few sensor readings from the
   database as JSON every few seconds.
 - Web page /fridge presents a virtual fridge where you can take out cans (drag and
   drop) and "drink" them.  While doing so, keeps track of cans still in fridge, and
   of "payment" for the different can types.
"""
import logging
import os

import cherrypy

from mako.lookup import TemplateLookup

from sensor import TemperatureSensor
from sensorStore import SensorStore

from fridge import Fridge
from account import Account

THE_FRIDGE = Fridge()   # initial empty fridge, as globaly accessible variable
THE_FRIDGE.set_red_can(n=4)
THE_FRIDGE.set_green_can(n=2)
THE_FRIDGE.set_blue_can(n=2)
print("Fridge initial stock loaded")  # fridge now loaded with initial stock

THE_FRIDGE_ACCOUNT = Account(initialBalance=10.0)

@cherrypy.expose
class JSONGeneratorWebService(object):
    """Web service to allow HTTP GET against fridge sensor readings database
    """

    @cherrypy.tools.accept(media='application/json')
    @cherrypy.tools.json_out()
    def GET(self, n=10, sensor_name="*"):
        """Return last n records of sensor data in response to HTTP GET request
        """
        store = SensorStore()
        if sensor_name == "*":
            reading_list = store.get_readings(count=n)
        else:
            reading_list = store.get_readings_for_sensor(sensor_name, count=n)
        store.close()

        cherrypy.log("In GET: retrieve {} readings from database for {}".format(n, sensor_name))
        results = dict()
        if sensor_name == "*":
            results['label'] = "All sensor readings"
        else:
            results['label'] = sensor_name

        results['data'] = [ \
                           [int(1000 * r.get_timestamp().timestamp()), r.get_value()] \
                           for r in reading_list \
                          ]

        return results


@cherrypy.expose
class Root(object):
    """Used to service requests for templates in the root of http://my.domain.com/
       Includes code to feed the fqdn for our web server into the templates, to allow callbacks.
    """

    # tell mako the list of directories in which to hunt for templates
    mylookupdirs = TemplateLookup(directories=['./'])
    # get our fully-qualified domain name
    import socket
    hostname = socket.gethostname()
    if hostname == "FREEMACL11":
        # special case: running on local laptop, where firewall forces us to use loopback address
        myfqdn = '127.0.0.1'
    else:
        myfqdn = socket.getfqdn(hostname)
    print("My fully-qualified domain name is: %s"%(myfqdn))


    @cherrypy.expose
    def index(self):
        """ Returns some barebones html in response to calls to the root like http://foo.com/
        """
        return ("Hello World! <br>You might want to check out <a href='fridge'>fridge</a>",
                " to see the fridge, or <a href='livedata'>livedata</a>",
                " to see the graphs and cool stuff.")

    @cherrypy.expose
    def livedata(self):
        """ Called to as /livedata url and returns a web page that shows the live data
        """
        mytemplate = self.mylookupdirs.get_template("flot_livedata.html")
        return mytemplate.render(fqdn=self.myfqdn)

    @cherrypy.expose
    def subscriber(self):
        """ Called as /subscriber url and returns a web page that shows
            the subscriber what they can do now
        """
        print("subscriber online")
        mytemplate = self.mylookupdirs.get_template("subscriber.html")
        return mytemplate.render(fqdn=self.myfqdn)

    @cherrypy.expose
    def fridge(self):
        """ Called as /fridge url to render an html template into a web page for the fridge
        """
        mytemplate = self.mylookupdirs.get_template("fridge.html")
        red_cans = THE_FRIDGE.get_red_can()
        green_cans = THE_FRIDGE.get_green_can()
        blue_cans = THE_FRIDGE.get_blue_can()
        return mytemplate.render(fqdn=self.myfqdn, \
                                 totalCanCount=red_cans + green_cans + blue_cans, \
                                 redCanCount=red_cans, \
                                 greenCanCount=green_cans, \
                                 blueCanCount=blue_cans, \
                                 balance=THE_FRIDGE_ACCOUNT.balance)

    @cherrypy.expose
    def fridgeAccountBalance(self, *args):
        """ Called by jQuery on the fridge page to GET the current balance
        """
        cherrypy.log("Getting fridge account balance")
        cherrypy.response.status = 200
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return "%.2f" % THE_FRIDGE_ACCOUNT.balance

    @cherrypy.expose
    def fridgeCheckRestock(self):
        """ Called by jQuery on the subscriber page to GET the flag that
            indicates if the fridge needs restocking
        """
        cherrypy.response.status = 200
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return repr(THE_FRIDGE.check_stock())


@cherrypy.expose
class FridgeUpdate():
    """Attached to /fridgeupdate HTTP path, so HTTP PUT with
       various suboptions like /fridgeupdate/dragFromFridge, etc,
       can update the fridge contents
    """

    @cherrypy.expose
    def PUT(self, *args, **kw):
        """Handle the HTTP PUT command from javascript in the web pages to update
           the contents of the fridge in various ways.
        """
        print(args, kw)
        print("Pre-move contents: "+THE_FRIDGE.status())
        if args[0] == "dragFromFridge":
            can_type = args[1]
            if can_type == "red_can":
                THE_FRIDGE.decr_red_can()
                THE_FRIDGE_ACCOUNT.deposit(0.3)
                cherrypy.response.status = "204 No Content"
            elif can_type == "green_can":
                THE_FRIDGE.decr_green_can()
                THE_FRIDGE_ACCOUNT.deposit(0.4)
                cherrypy.response.status = "204 No Content"
            elif can_type == "blue_can":
                THE_FRIDGE.decr_blue_can()
                THE_FRIDGE_ACCOUNT.deposit(0.5)
                cherrypy.response.status = "204 No Content"
            else:
                cherrypy.response.status = "404 Error"
        elif args[0] == "dropInFridge":
            THE_FRIDGE.incr_can(args[1])
            THE_FRIDGE_ACCOUNT.withdraw(0.2)
            cherrypy.response.status = "204 No Content"
        elif args[0] == "restockFridge":
            THE_FRIDGE.restock()
            cherrypy.response.status = "204 No Content"
        else:
            cherrypy.response.status = "404 Error"
        print("Post-move contents: "+THE_FRIDGE.status())
        # Possible responses are 204 (No Content)  or 404 (Error)
        return


def read_and_store_sensors():
    """function spun off into separate thread by main() in order to
       periodically read the sensor(s) and write their values to the database
    """
    logging.info("reading the sensors and writing to the database")

    store = SensorStore()

    sensor_list = [TemperatureSensor("thermometer 1"), TemperatureSensor("thermometer 2")]

    # Read the sensors
    sensor_readings = []
    for sensor in sensor_list:
        sensor_readings.append(sensor.get_reading())

    # Write the results to the local db
    for result in sensor_readings:
        store.add_reading(sensor_name=result.get_name(), when=result.get_timestamp(),
                          reading_type=result.get_type(), value=result.get_value())

    print("+", end='', flush=True)

    store.close()

if __name__ == '__main__':
    # Global config
    cherrypy.config.update({'environment': 'production', \
                            'log.access_file' : '', \
                            'access_log': None})

    # Kick off the background process that reads the sensor values into the database
    MONITOR_PROC = cherrypy.process.plugins.BackgroundTask(5, read_and_store_sensors)
    MONITOR_PROC.start()

    # Set up configs for the different application classes that we run
    JSON_CONF = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json'), \
                                               ('Access-Control-Allow-Origin', '*')],
        }
    }

    PATH = os.path.abspath(os.path.dirname(__file__))
    HTML_CONF = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': PATH,
            'tools.staticdir.index': 'index.html',
            'log.access_file':''
        }
    }

    # Attach the JSON web service applications to the right places
    cherrypy.tree.mount(JSONGeneratorWebService(), '/json', JSON_CONF)
    cherrypy.tree.mount(FridgeUpdate(), '/fridgeupdate', JSON_CONF)
    # Attach the file serving methods
    cherrypy.tree.mount(Root(), '/', HTML_CONF)

    # Bind to all IP addresses (accessible locally in browser at 127.0.0.1)
    cherrypy.server.socket_host = '0.0.0.0'

    # Boot up the web server
    cherrypy.engine.start()
    cherrypy.engine.block()

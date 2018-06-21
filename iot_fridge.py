"""
iot_fridge: when run as main, starts web server and kicks off background thread that reads sensors every
few seconds, writing to database.  
 - Web page /livedata does http GET to retrieve the last few sensor readings from the
   database as JSON every few seconds.  
 - Web page /fridge presents a virtual fridge where you can take out cans (drag and drop) and "drink" them.
   While doing so, keeps track of cans still in fridge, and of "payment" for the different can types.
"""
import json
import random
import string
import logging
import os

import cherrypy

from sensor import TemperatureSensor
from sensorReading import SensorReading
from sensorStore import SensorStore

from fridge import Fridge
from account import Account

from mako.template import Template
from mako.lookup import TemplateLookup

theFridge=Fridge()   # initial empty fridge, as globaly accessible variable
theFridgeAccount=Account(initialBalance=10.0)

@cherrypy.expose
class JSONGeneratorWebService(object):

    @cherrypy.tools.accept(media='application/json')
    @cherrypy.tools.json_out()
    def GET(self,n=10,sensor_name="*"):
        store = SensorStore()
        if sensor_name == "*":
            reading_list = store.get_readings(count=n)
        else:
            reading_list = store.get_readings_for_sensor(sensor_name,count=n)
        store.close()

        cherrypy.log("In GET: read back last {} readings from database for {}".format(n,sensor_name))
        results = dict()
        if sensor_name =="*" :
            results['label'] = "All sensor readings"
        else:
            results['label'] = sensor_name
        results['data'] = [[int(1000 * r.get_timestamp().timestamp()), r.get_value()] for r in reading_list]

        return results


@cherrypy.expose
class Root(object):
    
    # tell mako the list of directories in which to hunt for templates
    mylookupdirs = TemplateLookup(directories=['./'])  
    # get our fully-qualified domain name
    import socket
    hostname = socket.gethostname()
    if (hostname=="FREEMACL11"):
        # special case: running on local laptop, where firewall forces us to use loopback address
        myfqdn= '127.0.0.1'
    else:
        myfqdn = socket.getfqdn( hostname )     
    print("My fully-qualified domain name is: %s"%(myfqdn))

    
    @cherrypy.expose
    def index(self):
        return "Hello World! <br>You might want to check out <a href='fridge'>fridge</a> to see the fridge, or <a href='livedata'>livedata</a> to see the graphs and cool stuff."
    
    @cherrypy.expose
    def livedata(self):
        # Called to as /livedata url and returns a web page that shows the live data
        mytemplate = self.mylookupdirs.get_template("flot_livedata.html")
        return mytemplate.render(fqdn=self.myfqdn)
        
    @cherrypy.expose
    def fridge(self):
        # Called as /fridge url to render an html template into a web page for the fridge
        theFridge.set_red_can(n=3)
        theFridge.set_green_can(n=2)
        theFridge.set_blue_can(n=1)
        print("Fridge initial stock loaded")
        mytemplate = self.mylookupdirs.get_template("fridge.html")
        return mytemplate.render(fqdn=self.myfqdn,totalCanCount=6,redCanCount=3,greenCanCount=2,blueCanCount=1,balance=theFridgeAccount.balance)

    def POST(self, newstring):
        cherrypy.log("Post string to Root <%s>"%(newstring))
        cherrypy.session['mystring'] = newstring 
        return newstring

    @cherrypy.expose
    def fridgeAccountBalance(self, *args):
        # This method is called by jQuery on the fridge page to GET the current balance
        cherrypy.log("Getting fridge account balance")
        cherrypy.response.status=200
        cherrypy.response.headers['Content-Type']='text/plain'
        return "%.2f" % theFridgeAccount.balance


@cherrypy.expose
class fridgeUpdate():
   @cherrypy.expose
   def PUT(self, *args, **kw):
        print(args, kw)
        print("Pre-move contents: "+theFridge.status())
        if args[0]=="dragFromFridge":
            canType = args[1]
            if (canType=="red_can"):
                c=theFridge.decr_red_can()
                theFridgeAccount.deposit(0.3)
                cherrypy.response.status = "204 No Content"
            elif (canType=="green_can"):
                c=theFridge.decr_green_can()
                theFridgeAccount.deposit(0.4)
                cherrypy.response.status = "204 No Content"
            elif (canType=="blue_can"):
                c=theFridge.decr_blue_can()
                theFridgeAccount.deposit(0.5)
                cherrypy.response.status = "204 No Content"
            else:
                cherrypy.response.status = "404 Error"
        elif (args[0]=="dropInFridge"):
            theFridge.incr_can(args[1])
            theFridgeAccount.withdraw(0.2)
            cherrypy.response.status = "204 No Content"
        else:
            cherrypy.response.status = "404 Error"
        print("Post-move contents: "+theFridge.status())

        # Possible responses are 200 (OK)  202 (Accepted)  204 (No Content)  or 404 (Error)
        return

def read_and_store_sensors():
    logging.info("reading the sensors and writing to the database")

    store = SensorStore()

    sensor_list = [TemperatureSensor("thermometer 1"), TemperatureSensor("thermometer 2")]

    # Read the sensors
    sensor_readings = []
    for s in sensor_list:
        sensor_readings.append(s.get_reading())

    # Write the results to the local db
    for r in sensor_readings:
        store.add_reading(sensor_name=r.get_name(), when=r.get_timestamp(),
                          reading_type=r.get_type(), value=r.get_value())

    print("+",end='',flush=True);
    
    store.close()

if __name__ == '__main__':
    # Global config
    cherrypy.config.update({'environment': 'production', 'log.access_file' : '', 'access_log': None })
    
    # Kick off the background process that reads the sensor values into the database
    pr = cherrypy.process.plugins.BackgroundTask(5,read_and_store_sensors)
    pr.start()

    # Set up configs for the different application classes that we run
    json_conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json'),('Access-Control-Allow-Origin', '*')],
        }
    }

    PATH = os.path.abspath(os.path.dirname(__file__))
    html_conf = {
        '/': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': PATH,
            'tools.staticdir.index': 'index.html',
            'log.access_file':'' 
        }
    }

    # Attach the JSON web service applications to the right places
    cherrypy.tree.mount(JSONGeneratorWebService(), '/json', json_conf)
    cherrypy.tree.mount(fridgeUpdate(), '/fridgeupdate',json_conf)
    # Attach the file serving application
    cherrypy.tree.mount(Root(), '/', html_conf)

    # Bind to all IP addresses (accessible locally in browser at 127.0.0.1)
    cherrypy.server.socket_host = '0.0.0.0'

    # set up logging
    cherrypy.config.update({'environment': 'staging'})

    # Boot up the web server
    cherrypy.engine.start()
    cherrypy.engine.block()

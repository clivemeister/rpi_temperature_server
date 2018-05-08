import random
import string

import cherrypy


@cherrypy.expose
class StringGeneratorWebService(object):

    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        # TODO retrieve requested number of lines from the database, return as JSON
        return cherrypy.session['mystring']

    def POST(self, length=8):
        some_string = ''.join(random.sample(string.hexdigits, int(length)))
        cherrypy.session['mystring'] = some_string
        return some_string

    def PUT(self, another_string):
        cherrypy.session['mystring'] = another_string

    def DELETE(self):
        cherrypy.session.pop('mystring', None)

def testFunc():
    print("reading the sensors and writing to the database")
    # TODO obviously need to put the real code in here

if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        }
    } # TODO don't forget to change content type to JSON
    pr = cherrypy.process.plugins.BackgroundTask(5,testFunc)
    pr.start()

    cherrypy.quickstart(StringGeneratorWebService(), '/', conf)
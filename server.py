import cherrypy
import cherrypy_cors
import sys
import route

class Server(object):
	def __init__(self):
		object.__init__(self)
		self.test = "test"

	@cherrypy.expose
	def index(self):
		return "HELLO WORLD!"

	@cherrypy.expose
	#@cherrypy_cors.tools.expose()
	@cherrypy.tools.json_out()
	@cherrypy.tools.json_in(force=False)
	def query(self, curr_lat="0.0", curr_lng="0.0", dest_lat="0.0", dest_lng="0.0"):
		ret = {
			'coords': None,
		}

		# DO PATH COORDINATES FINDING STUFF HERE

		#ret['coords'] = "returned: " + curr_lat + curr_lng + dest_lat + dest_lng
		try:
			#ret['coords'] = route.getRoute(40.7416646,-74.0011315,40.7467947,-73.98848897)
			ret['coords'] = self.test
		except Exception as e:
			print("ERROR: " + e)
			ret['coords'] = None
			
		return ret

def CORS():
	cherrypy.response.headers["Access-Control-Allow-Origin"] = "*"


if __name__ == '__main__':
	cherrypy.tools.CORS = cherrypy.Tool('before_finalize', CORS)
	cherrypy.config.update({'tools.CORS.on': True,})
	cherrypy.server.socket_host = '0.0.0.0'
	cherrypy.quickstart(Server())

"""
bp_broker API module.

Listens and responds to ssl connections.  Proxies connection requests to registered event handlers.
"""


import threading
import Queue
import json
import BaseHTTPServer, SimpleHTTPServer
import ssl
import time
import re
from urlparse import urlparse, parse_qs
from StringIO import StringIO

import bpbroker


default_config = {
	'listen_port': 20443,
	'listen_ip': '',	# default bind to all interfaces
	'ssl_cert': 'bpbroker/dummy_api.crt',
	'ssl_key': 'bpbroker/dummy_api.key',
}



#####################################################


class TimeoutBaseHTTPServer(BaseHTTPServer.HTTPServer):
	timeout = 1


class Response():

	#status = False
	#headers = []	# list of dicts: {'keyword': x, 'value': y }
	#response = False

	def __init__(self,status=False,headers=[],response=False):  
		print "init"
		self.status = status
		self.headers = headers	# list of dicts: {'keyword': x, 'value': y }
		#self.headers = []
		self.response = response
		print self.headers
		print "end init"


	def AddHeader(self,keyword,value):  self.headers.append({'keyword': keyword, 'value': value})



class APIHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def log_error(self, format, *args):
		pass
	def log_request(self, code='-', size='-'):
		pass


	def ParseRequest(self):
		(undef,self.package,self.method) = urlparse(self.path).path.split("/",3)
		self.qs = parse_qs(urlparse(self.path).query)


	def ValidateRequest(self):
		error = False
		with bpbroker.config.rlock:
			if self.package not in bpbroker.config.data:  error = "Unauthorized package"
			if re.match("_",self.method):  error = "Unauthorized method"
			else:
				try:
					if not hasattr(getattr(bpbroker,self.package), self.method):  error = "Unauthorized method"
				except:
					error = "Unauthorized method"

		if error: self.send_error(401, error)

		return(not error)


	def do_GET(self):  self.ProcessRequest()
	def do_POST(self):  self.ProcessRequest()
	def do_DELETE(self):  self.ProcessRequest()


	def ProcessRequest(self):
		self.end_headers()
		self.ParseRequest()
		if self.ValidateRequest():  getattr(getattr(bpbroker,self.package), self.method)(self)



class APIThread(threading.Thread):

	def __init__(self,worker_queue,health_queue,config={}):
		threading.Thread.__init__(self)
		self.worker_queue = worker_queue
		self.health_queue = health_queue
		self._stop_event = threading.Event()
		bpbroker.config.data['hits'] = []
		self.config = dict(list(default_config.items()) + list(config.items()))


	def join(self,timeout=None):
		self._stop_event.set()
		threading.Thread.join(self, timeout)


	def run(self):
		#self.web_server = TimeoutBaseHTTPServer((self.config['listen_ip'], self.config['listen_port']), SimpleHTTPServer.SimpleHTTPRequestHandler)
		self.web_server = TimeoutBaseHTTPServer((self.config['listen_ip'], self.config['listen_port']), APIHTTPRequestHandler)
		self.web_server.socket = ssl.wrap_socket (self.web_server.socket, 
									 			  server_side=True,
									 			  certfile=self.config['ssl_cert'],
									 			  keyfile=self.config['ssl_key'],
												  )
		while not self._stop_event.is_set():
			self.web_server.handle_request()
			self.HealthCheck()


	def HealthCheck(self):
		self.health_queue.put_nowait({'thread': 'API', 'ts': int(time.time())})




import socket
import sys
import time
import threading
import random
import hashlib
import json

#class for creating a connection between 2 nodes
class NodeConnection(threading.Thread):
	'''
	main_node: The Node class that received a connection.
	sock: The socket that is assiociated with the client connection.
	id: The id of the connected node.
	host: The host/ip of the main node.
	port: The port of the server of the main node.
	'''
	def __init__(self,main_node,sock,id,host,port):

		#instatiate a new connection and start a thread
		super(NodeConnection,self).__init__()

		self.host = host
		self.port = port
		self.main_node = main_node
		self.sock = sock
		self.terminate_flag = threading.Event()

		self.id = id

		#to mark the end of transmission of a message
		self.EOT_CHAR = 0x04.to_bytes(1, 'big')

		#store extra info
		self.info = {}

		self.main_node.debug_print("NodeConnection.send: Started with client (" + self.id + ") '" + self.host + ":" + str(self.port) + "'")

	#send string data to client
	def send(self,data,encoding_type='utf-8'):
		if isinstance(data,str):
			self.sock.sendall(data.encode(encoding_type)+self.EOT_CHAR)
		else:
			self.main_node.debug_print('datatype used is not valid plese use str')

	#check the validity of data
	def check_message(self,data):
		pass

	#decode the received packets
	def parse(self,data,decoding_type='utf-8'):

		try:
			decoded = data.decode(decoding_type)
			return decoded
		except UnicodeDecodeError:
			return data

	def set_info(self,key,value):
		self.info[key] = value

	def get_info(self,key):
		if key in self.info:
			return info[key]
		else:
			return "Sorry, but the key doesn't exist!"

	def get_keys(self):
		return list(self.info.keys())

	#Implementing the thread
	def run(self):
		self.sock.settimeout(10.0)
		buffer=b''

		while not self.terminate_flag.is_set():
			chunk = b''

			try:
				chunk = self.sock.recv(4096)

			except socket.timeout:
				self.main_node.debug_print("NodeConnection: timeout")

			except Exception as e:
				self.terminate_flag.set()
				self.main_node.debug_print("Unexcpected error")
				self.main_node.debug_print(e)

			if chunk != b'':
				buffer += chunk
				print(len(buffer))
				eot_pos = buffer.find(self.EOT_CHAR)

				while eot_pos >0:
					packet = buffer[:eot_pos]
					buffer = buffer[eot_pos+1:]

					self.main_node.message_count_recv += 1
					self.main_node.node_message(self,self.parse(packet))
					eot_pos = buffer.find(self.EOT_CHAR,0,4096)

			time.sleep(0.01)

		self.main_node.send_bye(self)

		self.sock.settimeout(None)
		self.sock.close()
		self.main_node.debug_print("NodeConnection: Stopped")


	def __str__(self):
		return 'NodeConnection: {}:{} <-> {}:{} ({})'.format(self.main_node.host, self.main_node.port, self.host, self.port, self.id)


	def __repr__(self):
		return '<NodeConnection: Node {}:{} <-> Connection {}:{}>'.format(self.main_node.host, self.main_node.port, self.host, self.port)







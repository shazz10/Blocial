import socket
import sys
import time
import threading
import random
import hashlib
from uuid import getnode as get_mac

from p2pnetwork.nodeconnection import NodeConnection


class Node(threading.Thread):
	#Implmentation of a node that can connect to other nodes 

	def __init__(self,host,port):
		#create instance of a node 

		super(Node,self).__init__()

		self.terminate_flag = threading.Event()

		self.host = host
		self.port = port

		#connection in and out
		self.nodes_inbound = []
		self.nodes_outbound = []

		mac = get_mac()
		macid = hashlib.sha512()
		macid.update(str(mac).encode('ascii'))
		#a fixed uniqueID
		self.id = macid.hexdigest()

		# Start the TCP/IP server
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.init_server()

		# Message counters to make sure everyone is able to track the total messages
		self.message_count_send = 0
		self.message_count_recv = 0
		self.message_count_rerr = 0

		# Debugging on or off!
		self.debug = True

	def all_nodes(self):
		return self.nodes_inbound + self.nodes_outbound

	def print_connections(self):
		print("Node connection overview:")
		print("- Total nodes connected with us: %d" % len(self.nodes_inbound))
		print("- Total nodes connected to     : %d" % len(self.nodes_outbound))


	def debug_print(self,message):
		if self.debug:
			print("DEBUG: "+message)

	def init_server(self):
		#start tcp/ip server
		print("Initialisation of the Node on port: " + str(self.port) + " on node (" + self.id + ")")
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
		self.sock.bind((self.host,self.port))
		self.sock.settimeout(10.0)
		self.sock.listen(1)

	def create_new_connection(self,connection,id,host,port):
		#create actual connection between nodes
		return NodeConnection(self,connection,id,host,port)

	def connect_with_node(self,host,port):
		#make a connection with another node

		if host == self.host and port == self.port:
			print("Cannot connect with yourself!!")
			return False

		for node in self.nodes_outbound:
			if node.host == host and node.port == port:
				print("connect_with_node: Already connected with this node.")
				return True

		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.debug_print("Connecting to {} port {}".format(host,port))
			sock.connect((host,port))

			#send and recieve id of nodes
			sock.send(self.id.encode('utf-8'))
			connected_node_id = sock.recv(4096).decode('utf-8')

			thread_client = self.create_new_connection(sock,connected_node_id,host,port)
			thread_client.start()

			self.nodes_outbound.append(thread_client)
			self.outbound_node_connected(thread_client)

		except Exception as e:
			self.debug_print("TcpServer.connect_with_node: Could not connect with node. (" + str(e) + ")")

	def disconnect_with_node(self,node):
		#disconnect from provided node
		if node in self.nodes_outbound:
			self.node_disconnect_with_outbound_node(node)
			node.stop()
			node.join()  # When this is here, the application is waiting and waiting
			del self.nodes_outbound[self.nodes_outbound.index(node)]

		else:
			print("Node disconnect_with_node: cannot disconnect with a node with which we are not connected.")


	def delete_closed_connections(self):
		#like a clean up crew
	
		for n in self.nodes_inbound:
			if n.terminate_flag.is_set():
				self.inbound_node_disconnected(n)
				n.join()
				del self.nodes_inbound[self.nodes_inbound.index(n)]

		for n in self.nodes_outbound:
			if n.terminate_flag.is_set():
				self.outbound_node_disconnected(n)
				n.join()
				del self.nodes_outbound[self.nodes_inbound.index(n)]


	def send_to_nodes(self,data,exclude=[]):
		self.message_count_send+=1

		for n in self.nodes_inbound:
			if n in exclude:
				self.debug_print("Node send_to_nodes: Excluding node in sending the message")
			else:
				self.send_to_node(n, data)

		for n in self.nodes_outbound:
			if n in exclude:
				self.debug_print("Node send_to_nodes: Excluding node in sending the message")
			else:
				self.send_to_node(n, data)


	def send_to_node(self, n, data):
	# Send the data to the node n if it exists.
		
		self.delete_closed_connections()
		if n in self.nodes_inbound or n in self.nodes_outbound:
			try:
				n.send(data)
				self.message_count_send = self.message_count_send + 1
			except Exception as e:
				self.debug_print("Node send_to_node: Error while sending data to the node (" + str(e) + ")")
		else:
			self.debug_print("Node send_to_node: Could not send the data, node is not found!")
			
	def stop(self):
		#stop the node
		self.node_request_to_stop()
		self.terminate_flag.set()


	def run(self):
		#running the thread and maintaining inbound connections

		while not self.terminate_flag.is_set():
			try:
				self.debug_print("Node: Waiting for incoming connections")

				connection, client_address = self.sock.accept()

				#id exchange
				connected_node_id = connection.recv(4096).decode('utf-8')
				connection.send(self.id.encode('utf-8'))

				thread_client = self.create_new_connection(connection, connected_node_id, client_address[0], client_address[1])
				thread_client.start()

				self.nodes_inbound.append(thread_client)

				self.inbound_node_connected(thread_client)

			except socket.timeout:
				self.debug_print("Node: Connection timeout!")

			except Exception as e:
				raise e


			time.sleep(0.01)

		print("Node stopping...")
		for t in self.nodes_inbound:
			t.stop()

		for t in self.nodes_outbound:
			t.stop()

		time.sleep(1)

		for t in self.nodes_inbound:
			t.join()

		for t in self.nodes_outbound:
			t.join()

		self.sock.settimeout(None)   
		self.sock.close()
		print("Node stopped")


	def outbound_node_connected(self, node):
		self.debug_print("outbound_node_connected: " + node.id)
		
	def inbound_node_connected(self, node):
		self.debug_print("inbound_node_connected: " + node.id)
		
	def inbound_node_disconnected(self, node):
		self.debug_print("inbound_node_disconnected: " + node.id)
		
	def outbound_node_disconnected(self, node):
		self.debug_print("outbound_node_disconnected: " + node.id)
		
	def node_message(self, node, data):
		self.debug_print("node_message: " + node.id + ": " + str(data))
		
	def node_disconnect_with_outbound_node(self, node):
		self.debug_print("node wants to disconnect with oher outbound node: " + node.id)
		
	def node_request_to_stop(self):
		self.debug_print("node is requested to stop!")
		
	def __str__(self):
		return 'Node: {}:{}'.format(self.host, self.port)

	def __repr__(self):
		return '<Node {}:{} id: {}>'.format(self.host, self.port, self.id)
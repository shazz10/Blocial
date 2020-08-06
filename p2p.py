from node import Node

class p2pNode(Node):

	# Python class constructor
	def __init__(self, host, port):
		super(p2pNode, self).__init__(host, port)
		print("My p2p Node Started!!")

	#implement Abstraction here
	def stop_node(self):
		pass

	def add_node(self):
		pass

	def delete_node(self):
		pass

	def refresh_node(self):
		pass

	def send_message(self):
		pass

	def debug_toggle(self):
		pass


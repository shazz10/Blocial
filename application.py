import sys
import time
from get_port import find_free_port
from p2p import p2pNode

def main():
	print("WELCOME TO MY P2P NETWORK!!!")
	while 1:
		
		print("Choices:\n 1)Start MyNode\n 2)Add node\n 3)Delete Node\n 4)Send message\n 5)Stop MyNode\n 6)Close Application\n")
		c = int(input("Enter your choice number: "))

		if c==1:
			#start node
			node = p2pNode("0.0.0.0", find_free_port()[0])
			node.start()
			time.sleep(2)
		elif c==2:
			#add node
			host = input("Enter the client host: ")
			port = int(input("Enter the client port: "))

			node.connect_with_node(host,port)

			time.sleep(2)

		elif c==3:
			#delete node
			print("The outbound nodes are: ")
			for i in range(len(node.nodes_outbound)):
				print("{}) Id:{} , Host:{}, Port:{}".format(i,node.nodes_outbound[i].id,node.nodes_outbound[i].host,node.nodes_outbound[i].port))

			ch = int(input("Enter the node index to be deleted: "))
			node.disconnect_with_node(node.nodes_outbound[ch])

			time.sleep(2)

		elif c==4:
			#send message
			s = int(input("Enter 1 to send to a specific node, 0 to send to all connected nodes: "))
			if s==1:
				#send to 1 node
				message = input("Enter your message: ")
				print("Select from the following connected nodes")
				connected_nodes = node.all_nodes()
				for i in range(len(connected_nodes)):
					print("{}) Id:{} , Host:{}, Port:{}".format(i,connected_nodes[i].id,node.connected_nodes[i].host,node.connected_nodes[i].port))
				ch = int(input("Enter the node index to be deleted: "))
				node.send_to_node(connected_nodes[ch],message)
			elif s==0:
				#send to all nodes
				message = input("Enter your message: ")
				node.send_to_nodes(message)
			else:
				print("Invalid input!!")
			time.sleep(2)

		elif c==5:
			node.stop()
			time.sleep(2)

		elif c==6:
			node.stop()
			time.sleep(2)
			print("Exiting the application..")
			break

		else:
			print("Invalid choice please enter again!")


if __name__=="__main__":
	main()
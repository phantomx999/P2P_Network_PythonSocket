'''
M_server.py
Description:  
1.  M server listens on TCP socket for server connections
2.  Accepts connections, uses lock to not have race conditions with multi thread server requests
3.  Assigns server to a new ip and port, adds server to the cache, and refers server to first added server
in the cache
4.  Keeps track of total current servers requesting to be added to p2p network, writes this data onto file
'''


# Andrew Steinbrueck
# Student ID:  3949010
# CSCI 4211
# Socket Programming Assignment
# Phase 1 and Phase 2
# Date: April 21st 2019

# META SERVER

'''
to run:

> python M_server.py

'''

from socket import*
from _thread import*
import threading
import os
from time import sleep

print_lock = threading.Lock()

numberIPAddress = 10000  #assigned ip addresses basis
portNumber = 5000        #assigned port numbers
cache = []               #store servers in p2p
network = {}
numberOfServers = 0      #total servers in p2p

#create assigned ip address 
def makeIPString():
	global numberIPAddress
	numberIPAddress = numberIPAddress + 1
	tempString = str(numberIPAddress)
	tempStringList = list(tempString)
	tempStringList.insert(2, ".")
	tempStringList.insert(4, ".")
	tempStringList.insert(6, ".")
	result = ''.join(tempStringList)
	return result

#create assigned port
def makePort():
	global portNumber
	portNumber = portNumber + 1
	portString = str(portNumber)
	return portString

#keep track of total servers in p2p in file
def WriteToFile(numberOfServers):
	text_file="NumberOfServers.txt"
	with open(text_file, 'w') as filetowrite:
		filetowrite.write(str(numberOfServers))
		filetowrite.close()

#check servers in cache
def searchCache(server_id, ip):
	global cache
	if not cache:  # cache empty, add current server as first server
		cache.append(ip)
		print("Empty cache, adding " + server_id + " at ip address " + ip + " as first element in cache")
		return "empty_cache"
	else:
		cache.append(ip)  # add server to cache
		print("Referring server to first server in cache, ip address " + cache[0])
		return cache[0]  # refer to first server in cache

# only one server per thread at a time
# M server sends details to server to connect to P2P
def thread(connectionSocket):
	global numberOfServers
	server_id = ""
	while True:
		try:
			# get server id
			server_id = connectionSocket.recv(1024).decode("ascii")
			print("***Connected to " + server_id + " ***")
			# get p2p flag
			serverFlag = connectionSocket.recv(1024).decode("ascii")
			if serverFlag != "P2P" and serverFlag != "p2p" and serverFlag != "P2p":
				connectionSocket.sendall("Bad Input".encode())
				sleep(0.5)
			else:  # correct server flag
				connectionSocket.sendall("Good Input".encode())
				sleep(0.5)
			queryNewInput = ""
			# continually request for correct flag if invalid
			while serverFlag != "P2P" and serverFlag != "p2p" and serverFlag != "P2p":
				print("*****Invalid Flag*****")
				serverFlag = connectionSocket.recv(1024).decode("ascii")
				if serverFlag != "P2P" and serverFlag != "p2p" and serverFlag != "P2p":
					queryNewInput = "Bad Input"
				else:
					queryNewInput = "Good Input"
				connectionSocket.sendall(queryNewInput.encode())
				sleep(0.5)
			print("*****Valid Flag!*****")
		except:
			print("Error in M SERVER function thread()")
			break;
		numberOfServers = numberOfServers + 1  # increase server N
		WriteToFile(numberOfServers)
		strNewIP = makeIPString()
		print("***Assigning " + server_id + " new assigned IP address " + strNewIP + " ***")
		assignedPort = makePort()
		port = 5001
		strReferredAddress = searchCache(server_id, strNewIP)
		print("For " + server_id + " => New IP address: " + strNewIP + ", Referred IP address: "
				 + strReferredAddress + ", Referred Port: " + str(port) + ", AssignedPort: " + assignedPort)
		print("Sending <"+assignedPort+", " + str(port) + "> message to server " + server_id)
		# message info back to server, referral to other servers...
		assignedServerValues = strNewIP + ", " + strReferredAddress + ", " + str(port) + ", " + assignedPort
		connectionSocket.sendall(assignedServerValues.encode())
		sleep(0.5)
		print_lock.release()  # lock released
		print("Close M connection socket with " + server_id)
		break;
	connectionSocket.close()
	print("M server ready to receive new connections from servers...\n\n")

def Main():
	cwd = os.getcwd()
	topo = cwd + "/topo.txt" #topo file
	file1 = open(topo, "w")  #used to delete old file data from last time project was run
	file1.close()
	#M server starts TCP listening socket
	serverPort = 5000
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	serverSocket.bind(('', serverPort))  
	serverSocket.listen(5)
	print("M SERVER listening... waiting for server connections...")
	#M server continually accepts new requests from other servers	
	while True:
		connectionSocket, addr = serverSocket.accept()
		print('M SERVER accepts connection')	
		print_lock.acquire()  #thread locked by one server
		start_new_thread(thread, (connectionSocket,))
		# thread released lock, new servers can start thread
	serverSocket.close()
	
if __name__ == '__main__':
	Main()

'''
server_client.py
Description:
1: Adds server to network by first contacting MetaServer
2. Receives info from M Server and referred server to connect with on P2P network
3. If first server added:
	- awaits listening socket connections
   If not first server added:
	- attempts to connect with first server
	- if first server has < 2 connections, connection accepted
	- if first server has >= 2 connections, refers to neighbor servers
        - once server makes connection with a P2P server, server then listens for new requests
4. Continue adding more servers onto network until full number of servers (user inputted) added to network
5. After this, goes into file sharing mode
 	- if server requesting downloaded file, checks own server files first, then makes request to neighbor server for file if necessary
	- if server awaiting for downloaded file request, checks current files, then forwards request to next neighbor server
	- if server has file, makes connection with original requesting server, sends file to this server and then closes connection
6. Prints topo information of network
7. Exits program
'''


# Andrew Steinbrueck
# Student ID:  3949010
# CSCI 4211
# Socket Programming Assignment
# Phase 1 and Phase 2
# Date: April 21st 2019

# P2P server S1, S2, S3.....Sn

'''
to run:
> python server_client.py

or

> python server_client.py <number_of_total_server>

(default = 5 if <number_of_total_server> is omitted)
'''

from socket import*
from _thread import*
import threading
from M_server import network
from time import sleep
import copy
import sys
import os

numberConnections = 0
assignID = ""
assignedIP = 0
assignedPort = 0
neighborList = []
numberOfServers = 0
userNumberServers = 0
serverRunning = False
STOP = False
fileDownloadingMode = False
fileNameDownload = ""
originalFileServer = False
originalFileServerID = ""
originalFileServerPort = ""
lock = threading.Lock()
firstServer = False

# parse "var1, var2, var3, var4" string
def parseResponse(data):
	strList = data.split(",") 
	temp = ''.join(strList)
	strList = temp.split(" ")
	return strList[0], strList[1], strList[2], strList[3]

# parse "var1:var2:var3:var4" string	
def parseResonse2(data):
	strList = data.split(":")
	return strList[0], strList[1], strList[2], strList[3]

# first UI, add server to P2P, print topo
def UserInput():
	global serverRunning
	global assignID
	global fileNameDownload
	id = ""
	addToNetwork = ""
	# beginning UI prompt, enter 1 or 2
	while (addToNetwork != "1" and addToNetwork != 1) and (addToNetwork != "2" and addToNetwork != 2):
		addToNetwork = raw_input("Enter \"1\" to add server to the network, \"2\" to download file:  ")
		if (addToNetwork == "1" or addToNetwork == 1) and serverRunning:
			print("Error, this server already on P2P network, "
			"open a new terminal and run \'python server_client.py\' to add another new server to P2P\n\n")
			addToNetwork = "error"
		elif (addToNetwork == "2" or addToNetwork == 2) and not serverRunning:
			print("Error, server not on P2P network yet, can't download file")
			addToNetwork = "error"
	# enter server id
	if addToNetwork == "1" or addToNetwork == 1:
		while not id:
			id = raw_input("Input server ID (s1...s5 for file sharing):  ")
		assignID = id
		print("Server id = " + assignID)
	# enter files for downloading
	elif addToNetwork == "2" or addToNetwork == 2:
		file = ""
		print("Enter the filename you wish to download (Don't forget to add \'.txt\' to end of file name):  ")
		file = raw_input("Otherwise leave blank and press enter in order for this server to receive file sharing request...  ")
		if file != "":
			file = "ServerFiles/" + file 
		fileNameDownload = file
		return
	# print out topo
	topo = raw_input("Enter \"topo\" to view current network (before adding this server), else press enter to ignore:  ")
	if topo == "TOPO" or topo == "topo" or topo == "Topo":
		print("\nTOPO CURRENT NETWORK:  ")
		viewNetwork()

# for UI2
def Menu():
	global assignID
	print("\n\n********** "+ assignID +" User Input**************************")
	print("1.  Enter \"topo\" to view current P2P network ")
	print("2.  Enter \"2\" to enter file sharing mode ")
	print("3.  Enter \"stop\" to exit server program")
	print("***************************************************")

# after all servers added to P2P
# for file sharing mode, print topo, or close down server
def UserInput2():
	global STOP
	global fileNameDownload
	global originalFileServer
	input = ""
	#print topo, download files, or stop
	while not STOP and (input != "2" and input != 2):
		Menu()		
		input = raw_input("")
		if input == "stop "or input == "Stop" or input == "STOP":
			STOP = True
			return
		if input == "TOPO" or input == "topo" or input == "Topo":
			viewNetwork()
	# enter file to download, or receive file sharing request
	if input == "2" or input == 2:
		sought_file = ""
		print("Enter the filename you wish to download (Don't forget to add \'.txt\' to end of file name)...  ")
		print("Otherwise leave blank and press enter in order for this server to receive file sharing requests from other servers...  ")
		sought_file = raw_input(assignID + " input:  ")
		if sought_file != "":
			sought_file = sought_file 
			originalFileServer = True
		fileNameDownload = sought_file
		return
	return

# look at topo file info for server
def checkContents(topo, client):
	try:
		file1 = open(topo, "r")
	except OSERROR:
		print("could not open file, quitting program....")
		quit()
	countLine = -1
	for line in file1:
		countLine = countLine + 1
		stri = line
		stri = stri.split()[0]
		if client == stri:
			file1.close()
    			return "found", countLine
	file1.close()
	return "not_found", 0 

# check if file is empty
def is_non_zero_file(fpath):  
    return os.path.isfile(fpath) and os.path.getsize(fpath) > 0

# print out topo file
def viewNetwork():
	cwd = os.getcwd()
	topo = cwd + "/topo.txt"
	sizeFile = is_non_zero_file(topo)
	if sizeFile == 0:
		print("empty network!")
	else:
		f = open(topo, "r")
		print(f.read())

# get current total N servers on P2P	
def ReadTotalServerCount():
	cwd = os.getcwd()
	count = cwd + "/NumberOfServers.txt"
	sizeFile = is_non_zero_file(count)
	if sizeFile == 0:
		print("No NumberOFServers.txt file exists!")
		return -1
	else:
		with open(count, 'r') as file:
			data = file.readlines()
		return int(data[0])

# add server connections in topo file
def addNode(client, server):
	cwd = os.getcwd()
	topo = cwd + "/topo.txt"
	if server == "":     # add server and connections on file line if not there yet
		file1 = open(topo, "w")
		line = client + " :  \n"
		file1.write(line)
		file1.close()
	else:  # or add on server connections if server already on topo file line
		f, lineNumber = checkContents(topo, client)
		temp = ''
		if f == "found":
			with open(topo) as fp:
    				for i, line in enumerate(fp):
        				if i == lineNumber:
        					stri = server + " \n"
						temp = line.replace("\n", stri)
						break
			with open(topo, 'r') as file:
				data = file.readlines()
			data[lineNumber] = temp
			with open(topo, 'w') as file:
				file.writelines(data)
    		else:  # for client server adding receiving server
    			file1 = open(topo, "a")
			line = client + " :  " + server + " \n"
			file1.write(line)
			file1.close() 

# store server neighbors
def addToNeighbors(neighborinfo):
	global neighborList
	stri = neighborinfo + ", null"
	neighborList.append(stri)

# refer to first server neighbor of current server
def ReferToNeighbor():
	global neighborList
	return neighborList[0]

# file sharing, check if current server has file
def FindFile():
	global fileNameDownload
	global numberOfServers
	sought_file = ""
	# set up prefix for file name based on server id
	if assignID == "s1" or assignID == "S1":
		sought_file = "f"
	elif assignID == "s2" or assignID == "S2":
		sought_file = "pin"
	elif assignID == "s3" or assignID == "S3":
		sought_file = "pwd"
	elif assignID == "s4" or assignID == "S4":
		sought_file = "snn"
	elif assignID == "s5" or assignID == "S5":
		sought_file = "u"
	else:
		print("Error, server ID does not match s1...s5")
		return False
	temp = sought_file
	# compare files saved in server with download requested file
	for i in range(numberOfServers+1):
		temp = temp + str(i+1) + ".txt"
		if fileNameDownload == temp:
			return True
		temp = sought_file
	return False

# read contents of downloaded file
def ReadFileContent(sought_file):
	cwd = os.getcwd()
	count = cwd + "/" + sought_file
	sizeFile = is_non_zero_file(count)
	if sizeFile == 0:
		print("No Content in file "+ sought_file + "!")
	else:
		print("Reading contents of file now.....")
		with open(count, 'r') as file:
			data = file.readlines()
			print(data)
	print("All done with downloading file " + sought_file + "!")

def DownloadSender(listener, sender):
	global STOP
	global fileDownloadingMode
	global fileNameDownload
	global originalFileServer
	global assignID
	global assignedPort	
	global originalFileServerID
	global originalFileServerPort
	if originalFileServer:	#for original, first server only
		found = FindFile()  #original server first checks if it has file
		if found:
			print("File " + fileNameDownload + " already exists in original server " + assignID)
			ignore_message = "ignore"
			sender.sendall(ignore_message.encode())
			read_file = "ServerFiles/" + fileNameDownload
			ReadFileContent(read_file)
			fileDownloadingMode = False
			fileNameDownload = ""
			originalFileServer = False
		else:				#server sends id, port, and file to next server
			message = assignID + ":" + str(assignedPort) + ":" + fileNameDownload + ":" + assignID
			sender.sendall(message.encode())	
			#requesting server awaits connection from the response server that has the file
			print(assignID + ":  Waiting on other server(s) to enter file sharing mode, or for correct server to send back file...")
			receivingFileSocket, addr = listener.accept()
			file_response = receivingFileSocket.recv(1024).decode("ascii")
			response_server, sought_file, invalid, junk2 = parseResponse(file_response)
			print("Closing connection with " + response_server)			
			receivingFileSocket.close()
			if invalid == "invalid_entry":
				print("Server " + assignID + " received " + invalid + ", " + sought_file + " from " + response_server)
			else:
				print("Server " + assignID + " downloaded " + sought_file + " from " + response_server)
				read_file = "ServerFiles/" + sought_file
				ReadFileContent(read_file)
			fileDownloadingMode = False
			fileNameDownload = ""
			originalFileServer = False
	else:	#for all other non original servers relaying request to next server
		found = FindFile()  #check if file in current server 
		if found:
			print("File " + fileNameDownload + " exists in server " + assignID)
			print("Sending back fileNameDownload to " + originalFileServerID + " at connection " + originalFileServerPort)
			#create message to send back to original server
			message = assignID + ", " + fileNameDownload + ", garbage1, garbage2" 
			#send file back now to original server
			respondingFileSocket = socket(AF_INET, SOCK_STREAM)
			respondingFileSocket.connect(("localhost", int(originalFileServerPort)))
			respondingFileSocket.sendall(message.encode())
			fileDownloadingMode = False
			fileNameDownload = ""
			print("Closing connection with " + originalFileServerID + " at connection " + originalFileServerPort)
			respondingFileSocket.close()
		elif not found and assignedPort == 5001: 
			print("Could not find " + fileNameDownload + ", invalid entry")			
			print("Sending back \"invalid entry\" to " + originalFileServerID + " at connection " + originalFileServerPort)
			message = assignID + ", file_not_found, invalid_entry, garbage2" 
			respondingFileSocket = socket(AF_INET, SOCK_STREAM)
			respondingFileSocket.connect(("localhost", int(originalFileServerPort)))
			respondingFileSocket.sendall(message.encode())
			fileDownloadingMode = False
			fileNameDownload = ""
			print("Closing connection with " + originalFileServerID + " at connection " + originalFileServerPort)
			respondingFileSocket.close()
		else:  #file not in current server, relay request to next server
			message = originalFileServerID + ":" + originalFileServerPort + ":" + fileNameDownload + ":" + assignID
			sender.sendall(message.encode())
			fileDownloadingMode = False
			fileNameDownload = ""

#receiving side servers already in P2P that wait for file sharing request
def DownloadReceiver(listener, receiver, sender):
	global STOP
	global originalFileServerID
	global originalFileServerPort
	global fileDownloadingMode
	global fileNameDownload
	global assignedPort
        # for servers waiting for file download request
	file_sharing_message = receiver.recv(1024).decode("ascii")

        # listening server prints out request info, keeps track of original server downloading request
	if file_sharing_message != "ignore":
		previous_id, port, sought_file, current_server_sender = parseResonse2(file_sharing_message)
		originalFileServerID = previous_id
		originalFileServerPort = port
		fileNameDownload = sought_file
		fileDownloadingMode = True
		print("***Received " + originalFileServerID + ":" + originalFileServerPort + ":" + fileNameDownload + 
		" from Server " + current_server_sender + "***")
		if assignedPort != 5001:
			DownloadSender(listener, sender)
		else:
			DownloadSender(listener, receiver)
	return

# for multi threading, download files
def DownloadFile(listener, sender, receiver):
	global STOP
	download_thread_sender = threading.Thread(target=DownloadSender, args=(listener, sender, ))
	download_thread_receiver = threading.Thread(target=DownloadReceiver, args=(listener, receiver, ))
	while not STOP:
			try:
				download_thread_sender.start()
				download_thread_receiver.start()
			except:
				download_thread_sender = threading.Thread(target=DownloadSender, args=(listener, sender, ))
				download_thread_receiver = threading.Thread(target=DownloadReceiver, args=(listener, receiver, ))
				download_thread_sender.start()
				download_thread_receiver.start()
	return

# third and last server only have 1 connection
# must have their own unique call for file sharing
def ThirdandLastServer(serverSocket, previous_server_connection):
	global numberOfServers
	global userNumberServers
	global fileNameDownload
	global STOP
        # wait until all servers added to P2P network
	while numberOfServers != userNumberServers:
		sleep(3)
		numberOfServers = ReadTotalServerCount()
        # print topo, enter file sharing, or stop to end program
	while not STOP:
		UserInput2()
		if STOP:
			return
		if fileNameDownload != "":
			DownloadSender(serverSocket, previous_server_connection)

# servers added to P2P, for file sharing, printing topo, or closing program
def SecondPhase(serverSocket, firstServerConnection, previous_server_connection):
	global STOP
	global fileNameDownload
	global numberConnections
	global assignedPort
	print("All done with adding total servers to P2P, now onto file sharing...")
	while not STOP:
		UserInput2()
		# end program
		if STOP:
			return
                # first server is endpoint for file sharing
		if assignedPort == 5001 and fileNameDownload == "":
			DownloadReceiver(serverSocket, firstServerConnection, previous_server_connection)
		elif assignedPort == 5001 and fileNameDownload != "":  # first server has downloaded file
			found = FindFile()
			if found:
				print("Found file " + fileNameDownload + " in own, original server")
			else:
				print("Could not find " + fileNameDownload + ", invalid entry")
		elif numberConnections == 2 and fileNameDownload != "": # all non leaf servers relaying requests
			DownloadSender(serverSocket, previous_server_connection)
		else:   # listening servers wait for request
			DownloadReceiver(serverSocket, firstServerConnection, previous_server_connection)

# P2P server waits to accept connection requests
def ServerAcceptingConnection(port, assignID, ip, referredIP, previous_server_connection):
	global numberConnections
	global serverRunning
	global firstServer
	global numberOfServers
	global userNumberServers
	global assignedPort
	global STOP
	serverRunning = True
	# server starts listening socket
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	serverSocket.bind(('', port))
	serverSocket.listen(5)

	# third server always will have only 1 connection, enter file sharing mode
	# since already has 1 connection
	if assignedPort == 5003:
		ThirdandLastServer(serverSocket, previous_server_connection)
		return
	# last server also only has 1 connections, enter file sharing mode
	temp = assignedPort % 10
	if temp == userNumberServers:
		ThirdandLastServer(serverSocket, previous_server_connection)
		return
	
	# server waits and accepts connections
	print("Server " + assignID + ":  Waiting to Receive and accept other server connections at address " + ip + " and port number " + str(port))
	firstServerConnection, addr = serverSocket.accept()
	connectionSocketserver = firstServerConnection
	while True:	
		# server lets other requesting server know # of connections
		connectionSocketserver.sendall(str(numberConnections).encode())
		sleep(0.5)
		# server able to take on new connections
		if numberConnections < 2:
			print("\nServer " + assignID + " accepts connection from sender")
			numberConnections = numberConnections + 1		
			info = connectionSocketserver.recv(1024).decode("ascii")
			serverID, ip, port, junk = parseResponse(info)			
			addNode(assignID, serverID)  # update server connections topo
			sleep(1.0)
			neighborinfo = serverID + ", " + ip + ", " + port
			addToNeighbors(neighborinfo)
			print("Server " + assignID + " adds " + serverID + " to network...")
			connectionSocketserver.sendall(assignID.encode())
			print("Server " + assignID + " waiting to receive and accept other server connections...")
			sleep(0.5)
		else:  # server connections >= 2, must refer to another server
			print("Server " + assignID + " cannot take any more connections, already has 2 connections")
			stri3 = ReferToNeighbor()
			# refer requestion server to neighbor server
			connectionSocketserver.sendall(stri3.encode())
			sleep(0.5)
			print("Server " + assignID + " refers to other server -> " + stri3 + ", \n...server is waiting to refer more new servers...")
			connectionSocketserver.close()  # close temp connection
		print("")
		# if total N servers added to network, exit loop
		numberOfServers = ReadTotalServerCount()
		if numberOfServers == userNumberServers:
			break
		# else, await new connections
		connectionSocketserver, addr = serverSocket.accept()
		# keep track of both sockets for first server
		if firstServer:
			previous_server_connection = connectionSocketserver
			firstServer = False
	# all servers added, now enter file sharing...
	SecondPhase(serverSocket, firstServerConnection, previous_server_connection)
	print("Server " + assignID + " server side:  All done, close connection(s)")
	connectionSocketserver.close()
	serverSocket.close()
	return

def Main():
	global assignID
	global assignedPort
	global STOP
	global firstServer
	global numberConnections
	global userNumberServers

	# command line arguments, default = 5 total servers
	if (len(sys.argv)) == 1:
		userNumberServers = 5
	elif (len(sys.argv)) == 2:
		if int(sys.argv[1]) > 9:
			userNumberServers = 9
		elif int(sys.argv[1]) < 1:
			userNumberServers = 5
		else:
			userNumberServers = int(sys.argv[1])
	else:
		print("Invalid number of arguments, \"python P2Pserver.py <number_of_servers>\"")
		return
	# UI input
	UserInput()
	
	#Contact Meta Server, set flag
	serverName = "localhost"
	serverPort = 5000
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((serverName,serverPort))
	clientSocket.sendall(assignID.encode())
	sleep(0.5)
	flag = ""
	while flag == "":
		flag = raw_input("Enter \"p2p\" as input to set valid flag:  ")
	clientSocket.sendall(flag.encode())
	sleep(0.5)
	flagResponse = clientSocket.recv(1024).decode("ascii")
	while flagResponse == "Bad Input":
		flag2 = ""
		while flag2 == "":
			flag2 = raw_input("Bad Input.  Enter \"P2P\" as input to set valid flag:  ")
		clientSocket.sendall(flag2.encode())
		sleep(0.5)
		flagResponse = clientSocket.recv(1024).decode("ascii")
	clientSocket.sendall("ready_to_accept".encode())
	sleep(0.5)

	# receive response from Meta Server
	reponse = ''
	while True:
		response = clientSocket.recv(1024).decode("ascii")
		if response:
			break
	ip, referredIP, port, own_port = parseResponse(response)
	firstServerPort = int(port)
	assignedPort = int(own_port)
	print("\nServer " + assignID + ": Gets own port " + own_port + " and referred port " + port + " from Metadata Server")
	print("Server " + assignID + ": closing socket connection with Metadata Server")
	clientSocket.close()  # close out connection with Meta Server
	clientSocket2 = socket(AF_INET, SOCK_STREAM)

	# if first server on network
	if referredIP == "empty_cache":
		firstServer = True
		clientSocket2.close()
		addNode(assignID, "")
		print("Server " + assignID + " is first server added to network")
		# server listens and receives connections from other newly added servers
		ServerAcceptingConnection(firstServerPort, assignID, ip, referredIP, clientSocket2)
	else:  # non-first server on network
		print("Connecting to " + referredIP + " at port " + str(firstServerPort))
		connections = 0
		referredNodeIP = referredIP
		referredNodePort = str(firstServerPort)

		# connect to first server in network
		clientSocket2.connect(("localhost", firstServerPort))
		acceptedConnection = clientSocket2.recv(1024).decode("ascii")
		connections = int(acceptedConnection)
		if connections >= 2:
			print("Server " + referredIP + " already has 2 connections, referring now to other servers")
		else:
			print("Connecting to " + referredNodeIP + " at port " + referredNodePort + " successful")

		# for any listening servers already with >= 2 connections, refer this server to another server
		while connections >= 2:
			info = clientSocket2.recv(1024).decode("ascii")
			clientSocket2.close()
			receiverID, receiverIP, receiverPort, junk = parseResponse(info)
			clientSocket2 = socket(AF_INET, SOCK_STREAM)
			clientSocket2.connect(("localhost", int(receiverPort)))
			acceptedConnection = clientSocket2.recv(1024).decode("ascii")
			connections = int(acceptedConnection)
			if connections >= 2:
				print("Server " + receiverID + " already has 2 connections, referring now to other servers")

		# server finally connects with an available server on network
		numberConnections = numberConnections + 1  # increment this server connections
		sleep(0.5)
		stri2 = assignID + ", " + ip + ", " + str(assignedPort) + ", garbage"
		clientSocket2.send(stri2.encode())
		sleep(0.5)
		serverID = clientSocket2.recv(1024).decode("ascii")
		sleep(1.0)
		addNode(assignID, serverID)  # update server connections topo
		print("Client server " + assignID + " connects to " + serverID + " on network")
		# server goes onto listen for new servers adding to network
		ServerAcceptingConnection(assignedPort, assignID, ip, referredIP, clientSocket2)
	# server exiting program, close down connections
	print("Server " + assignID + " client side:  All done, close connection(s)")
	clientSocket2.close()


if __name__ == '__main__':
	Main()




















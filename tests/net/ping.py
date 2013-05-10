#!/usr/bin/env python

#
# These code was borrowed and modified from: http://www.g-loaded.eu/2009/10/30/python-ping/
#
# Original license is this:
#

"""
    A pure python ping implementation using raw socket.


    Note that ICMP messages can only be sent from processes running as root.


    Derived from ping.c distributed in Linux's netkit. That code is
    copyright (c) 1989 by The Regents of the University of California.
    That code is in turn derived from code written by Mike Muuss of the
    US Army Ballistic Research Laboratory in December, 1983 and
    placed in the public domain. They have my thanks.

    Bugs are naturally mine. I'd be glad to hear about them. There are
    certainly word - size dependenceies here.

    Copyright (c) Matthew Dixon Cowles, <http://www.visi.com/~mdc/>.
    Distributable under the terms of the GNU General Public License
    version 2. Provided with no warranties of any sort.

    Original Version from Matthew Dixon Cowles:
      -> ftp://ftp.visi.com/users/mdc/ping.py

    Rewrite by Jens Diemer:
      -> http://www.python-forum.de/post-69122.html#69122

    Rewrite by George Notaras:
      -> http://www.g-loaded.eu/2009/10/30/python-ping/

    Revision history
    ~~~~~~~~~~~~~~~~

    November 8, 2009
    ----------------
    Improved compatibility with GNU/Linux systems.

    Fixes by:
     * George Notaras -- http://www.g-loaded.eu
    Reported by:
     * Chris Hallman -- http://cdhallman.blogspot.com

    Changes in this release:
     - Re-use time.time() instead of time.clock(). The 2007 implementation
       worked only under Microsoft Windows. Failed on GNU/Linux.
       time.clock() behaves differently under the two OSes[1].

    [1] http://docs.python.org/library/time.html#time.clock

    May 30, 2007
    ------------
    little rewrite by Jens Diemer:
     -  change socket asterisk import to a normal import
     -  replace time.time() with time.clock()
     -  delete "return None" (or change to "return" only)
     -  in checksum() rename "str" to "source_string"

    November 22, 1997
    -----------------
    Initial hack. Doesn't do much, but rather than try to guess
    what features I (or others) will want in the future, I've only
    put in what I need now.

    December 16, 1997
    -----------------
    For some reason, the checksum bytes are in the wrong order when
    this is run under Solaris 2.X for SPARC but it works right under
    Linux x86. Since I don't know just what's wrong, I'll swap the
    bytes always and then do an htons().

    December 4, 2000
    ----------------
    Changed the struct.pack() calls to pack the checksum and ID as
    unsigned. My thanks to Jerome Poincheval for the fix.


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $
"""



__all__ = ["do_ping_and_receive_ttl"]

import os, sys, socket, struct, select, time
from cStringIO import StringIO
from net_decoders import *
from struct import pack

# From /usr/include/linux/icmp.h; your milage may vary.
ICMP_ECHO_REQUEST = 8 # Seems to be the same on Solaris.


def checksum(source_string):
    """
    I'm not too confident that this is right but testing seems
    to suggest that it gives the same answers as in_cksum in ping.c
    """
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff # Necessary?
        count = count + 2

    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff # Necessary?

    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff

    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def receive_one_ping(my_socket, ID, timeout):
    """
    receive the ping from the socket.
    """
    timeLeft = timeout
    while True:
        startedSelect = time.time()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout
            return

        timeReceived = time.time()
        recPacket, addr = my_socket.recvfrom(1024)

        ttl, = struct.unpack("B", recPacket[8])

        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return

def receive_one_ttl_ping(my_socket, ID, timeout):
    """
    receive the ping from the socket and return their TTL
    """
    timeLeft = timeout
    while True:
        whatReady = select.select([my_socket], [], [], timeLeft)
        if whatReady[0] == []: # Timeout
            return

        recPacket, addr = my_socket.recvfrom(1024)
        ttl, = struct.unpack("B", recPacket[8])

        return ttl

def receive_one_seq_tcp(my_socket, timeout):
    """
    receive the ping from the socket and return their TTL
    """
    timeLeft = timeout
    while True:
        whatReady = select.select([my_socket], [], [], timeLeft)
        print whatReady
        if whatReady[0] == []: # Timeout
            return

        recPacket, addr = my_socket.recvfrom(1024)
        ttl, = struct.unpack("B", recPacket[8])

        return ttl


def send_one_ping(my_socket, dest_addr, ID):
    """
    Send one ping to the given >dest_addr<.
    """
    dest_addr  =  socket.gethostbyname(dest_addr)

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    my_checksum = 0

    # Make a dummy heder with a 0 checksum.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + data

    # Calculate the checksum on the data and the dummy header.
    my_checksum = checksum(header + data)

    # Now that we have the right checksum, we put that in. It's just easier
    # to make up a new header than to stuff it into the dummy.
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1



def do_ping_and_receive_ttl(dest_addr, timeout):
    """
    Returns either the delay (in seconds) or none on timeout.
    """
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error, (errno, msg):
        if errno == 1:
            # Operation not permitted
            msg = msg + (
                " - Note that ICMP messages can only be sent from processes"
                " running as root."
            )
            raise socket.error(msg)
        raise # raise the original error

    my_ID = os.getpid() & 0xFFFF

    send_one_ping(my_socket, dest_addr, my_ID)
    ttl = receive_one_ttl_ping(my_socket, my_ID, timeout)

    my_socket.close()
    return ttl


# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0

    # loop taking 2 characters at a time
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        s = s + w

    s = (s>>16) + (s & 0xffff);
    s = s + (s >> 16);

    #complement and mask to 4 byte short
    s = ~s & 0xffff

    return s

def do_tcp_connect_and_receive_seq(dest_addr, timeout):
    """
    Returns either the delay (in seconds) or none on timeout.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

    #sr = socket.socket()
    #sr.connect((dest_addr, 80))

    # tcp header fields
    tcp_source = 1234   # source port
    tcp_dest = 80   # destination port
    tcp_seq = 454
    tcp_ack_seq = 0
    tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
    #tcp flags
    tcp_fin = 0
    tcp_syn = 1
    tcp_rst = 0
    tcp_psh = 0
    tcp_ack = 0
    tcp_urg = 0
    tcp_window = socket.htons (5840)    #   maximum allowed window size
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_offset_res = (tcp_doff << 4) + 0
    tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)

    # the ! in the pack format string means network order
    tcp_header = pack('!HHLLBBHHH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)

    user_data = 'Hello, how are you'

    # pseudo header fields
    #source_address = socket.inet_aton( source_ip )
    #dest_address = socket.inet_aton(dest_ip)
    #placeholder = 0
    #protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header) + len(user_data)

    #psh = pack('!4s4sBBH' , source_address , dest_address , placeholder , protocol , tcp_length);
    #psh = psh + tcp_header + user_data;
    psh = tcp_header + user_data

    tcp_check = checksum(psh)
    #print tcp_checksum

    # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
    tcp_header = pack('!HHLLBBH' , tcp_source, tcp_dest, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + pack('H' , tcp_check) + pack('!H' , tcp_urg_ptr)

    # final full packet - syn packets dont have any data
    packet = tcp_header + user_data

    #Send the packet finally - the port specified has no effect
    s.sendto(packet, (dest_addr , 0 ))    # put this in a loop if you want to flood the target


    #s.connect((dest_addr, 80))

    # Send an HTTP request
    #sr.send("aaaa")
    # Get the response (in several parts, if necessary)
    #m_response = StringIO()

    while True:
        whatReady = select.select([s], [], [], timeout)

        if whatReady[0] == []: # Timeout
            continue

        buffer_lenght = 1024
        buf, addr        = s.recvfrom(buffer_lenght)
        #m_response.write( buffer )

        #while len(buffer) >= buffer_lenght:
            #buffer, addr = s.recvfrom(buffer_lenght)
            #m_response.write( buffer )

        break

    s.close()

    #dp = dumphex(m_response.getvalue())

    p = decode_ip_packet(buf)
    print struct.unpack("B", buf[8])
    #seq, = struct.unpack("H", buffer[24:28])

    print p["dst_ip"]

    #print m_response.getvalue()

    # Send an HTTP request
    # Get the response (in several parts, if necessary)
    #m_response = StringIO()


    #send_one_ping(my_socket, dest_addr, my_ID)
    #my_socket.connect((dest_addr, 80))
    #dest_addr  =  socket.gethostbyname(dest_addr)
    #my_socket.send("GET / HTTP/1.1\r\n\r\n") #, (dest_addr, 80)) # Don't know about the 1

    #print "a"
    #recPacket, addr = my_socket.recvfrom(1024)
    #print recPacket
    #print "b"

    #while True:
        #whatReady = select.select([my_socket], [], [], timeLeft)
        #print whatReady
        #if whatReady[0] == []: # Timeout
            #return


    #ttl = receive_one_seq_tcp(my_socket, timeout)

    #my_socket.close()
    #return ttl


def do_one(dest_addr, timeout):
    """
    Returns either the delay (in seconds) or none on timeout.
    """
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error, (errno, msg):
        if errno == 1:
            # Operation not permitted
            msg = msg + (
                " - Note that ICMP messages can only be sent from processes"
                " running as root."
            )
            raise socket.error(msg)
        raise # raise the original error

    my_ID = os.getpid() & 0xFFFF

    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)

    my_socket.close()
    return delay


def verbose_ping(dest_addr, timeout = 2, count = 4):
    """
    Send >count< ping to >dest_addr< with the given >timeout< and display
    the result.
    """
    for i in xrange(count):
        print "ping %s..." % dest_addr,
        try:
            delay  =  do_one(dest_addr, timeout)
        except socket.gaierror, e:
            print "failed. (socket error: '%s')" % e[1]
            break

        if delay  ==  None:
            print "failed. (timeout within %ssec.)" % timeout
        else:
            delay  =  delay * 1000
            print "get ping in %0.4fms" % delay
    print


if __name__ == '__main__':

    #print do_ping_and_receive_ttl("10.211.55.23",2)
    print do_tcp_connect_and_receive_seq("10.211.55.23",2)
    #print do_tcp_connect_and_receive_seq("208.84.244.10",2)